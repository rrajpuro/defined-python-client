"""Shared infrastructure for the :mod:`defined_client.cli` command line app."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any, TypeVar
from urllib.parse import urlparse

import click

from defined_client import DefinedClient, DefinedClientError


DEFAULT_BASE_URL = "https://api.defined.net"
DEFAULT_TIMEOUT = 30.0

T = TypeVar("T")


class APIError(click.ClickException):
    """A concise API or transport error (exit status 1)."""

    exit_code = 1


class ErrorHandlingGroup(click.Group):
    """Translate client exceptions without exposing tracebacks."""

    def invoke(self, ctx: click.Context) -> Any:
        try:
            return super().invoke(ctx)
        except DefinedClientError as exc:
            state = ctx.obj
            message = (
                state.redact(str(exc)) if isinstance(state, CLIState) else str(exc)
            )
            raise APIError(message) from exc


class JSONValue(click.ParamType):
    """Decode an inline JSON value or a UTF-8 ``file://`` document."""

    name = "json"

    def __init__(
        self,
        expected: type[Any] | tuple[type[Any], ...] | None = None,
        expected_name: str | None = None,
    ) -> None:
        self.expected = expected
        self.expected_name = expected_name

    def convert(
        self,
        value: Any,
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> Any:
        if not isinstance(value, str):
            return value

        source = value
        if value.startswith("file://"):
            filename = value[len("file://") :]
            if not filename:
                self.fail("file:// must be followed by a path", param, ctx)
            try:
                source = Path(filename).read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                self.fail(f"cannot read {filename!r}: {exc}", param, ctx)

        def reject_nonstandard_constant(constant: str) -> None:
            raise ValueError(f"non-standard JSON constant {constant!r} is not allowed")

        try:
            decoded = json.loads(source, parse_constant=reject_nonstandard_constant)
        except json.JSONDecodeError as exc:
            self.fail(
                f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}",
                param,
                ctx,
            )
        except ValueError as exc:
            self.fail(f"invalid JSON: {exc}", param, ctx)

        if self.expected is not None and not isinstance(decoded, self.expected):
            label = self.expected_name or "the expected top-level type"
            self.fail(f"JSON value must be {label}", param, ctx)
        return decoded


JSON_OBJECT = JSONValue(dict, "an object")
JSON_ARRAY = JSONValue(list, "an array")


class CLIState:
    """Per-invocation configuration and lazily-created API client."""

    def __init__(
        self,
        root_context: click.Context,
        *,
        api_key: str | None,
        base_url: str,
        timeout: float,
        output: str,
    ) -> None:
        self.root_context = root_context
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.output = output
        self._client: DefinedClient | None = None

    def get_client(self, *, require_auth: bool = True) -> DefinedClient:
        """Return one client per invocation, requiring auth only when needed."""
        if require_auth and not self.api_key:
            raise click.UsageError(
                "DEFINED_API_KEY is not set; export it before running this command"
            )
        if self._client is None:
            self._client = DefinedClient(
                api_key=self.api_key if require_auth else None,
                base_url=self.base_url,
                timeout=self.timeout,
            )
            self.root_context.call_on_close(self._client.close)
        return self._client

    def redact(self, message: str) -> str:
        """Remove the configured credential from diagnostics."""
        if self.api_key:
            return message.replace(self.api_key, "[REDACTED]")
        return message

    def emit(self, value: Any) -> None:
        """Write exactly one successful result to stdout."""
        if self.output == "json":
            click.echo(json.dumps(value, indent=2, ensure_ascii=False))
        else:
            click.echo(render_table(value))


def validate_base_url(
    _ctx: click.Context, _param: click.Parameter, value: str
) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise click.BadParameter("must be an absolute http:// or https:// URL")
    return value


def ensure_envelope(data: Any) -> dict[str, Any]:
    """Wrap service-only values in the same envelope shape as API responses."""
    if isinstance(data, dict) and "data" in data:
        envelope = dict(data)
        envelope.setdefault("metadata", {})
        return envelope
    return {"data": data, "metadata": {}}


def _cell(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, separators=(",", ":"), sort_keys=True)
    return str(value)


def _grid(headers: list[str], rows: list[list[str]]) -> str:
    widths = [len(header) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))

    def line(values: Sequence[str]) -> str:
        return " | ".join(
            value.ljust(widths[index]) for index, value in enumerate(values)
        ).rstrip()

    separator = "-+-".join("-" * width for width in widths)
    return "\n".join([line(headers), separator, *(line(row) for row in rows)])


def render_table(value: Any) -> str:
    """Render response data as a deterministic, dependency-free table."""
    data = value.get("data") if isinstance(value, dict) and "data" in value else value

    if data is None or data == [] or data == {}:
        return "No results."

    if isinstance(data, list):
        if not data:
            return "No results."
        if all(isinstance(item, Mapping) for item in data):
            keys = sorted({str(key) for item in data for key in item})
            rows = [[_cell(item.get(key)) for key in keys] for item in data]
            return _grid(keys, rows)
        return _grid(["value"], [[_cell(item)] for item in data])

    if isinstance(data, Mapping):
        rows = [[str(key), _cell(data[key])] for key in sorted(data, key=str)]
        return _grid(["key", "value"], rows)

    return _grid(["value"], [[_cell(data)]])


def paginate(
    list_method: Callable[..., dict[str, Any]],
    *,
    page_size: int,
    starting_token: str | None,
    no_paginate: bool,
    **kwargs: Any,
) -> dict[str, Any]:
    """Call a cursor endpoint once or exhaust it into one complete envelope."""
    if no_paginate:
        return list_method(cursor=starting_token, page_size=page_size, **kwargs)

    cursor = starting_token
    seen_cursors: set[str] = {starting_token} if starting_token else set()
    items: list[Any] = []
    combined: dict[str, Any] | None = None
    combined_metadata: dict[str, Any] = {}

    while True:
        response = list_method(cursor=cursor, page_size=page_size, **kwargs)
        if not isinstance(response, dict):
            raise DefinedClientError("Invalid paginated response")
        page = response.get("data", [])
        metadata = response.get("metadata", {})
        if not isinstance(page, list) or not isinstance(metadata, dict):
            raise DefinedClientError("Invalid paginated response")

        if combined is None:
            combined = dict(response)
            combined_metadata = dict(metadata)
        else:
            for key, metadata_value in metadata.items():
                if key not in {
                    "hasNextPage",
                    "hasPrevPage",
                    "nextCursor",
                    "prevCursor",
                    "page",
                }:
                    combined_metadata.setdefault(key, metadata_value)
        items.extend(page)

        if not metadata.get("hasNextPage"):
            break
        next_cursor = metadata.get("nextCursor")
        if not isinstance(next_cursor, str) or not next_cursor:
            raise DefinedClientError(
                "Invalid paginated response: next cursor is missing"
            )
        if next_cursor in seen_cursors:
            raise DefinedClientError(
                "Invalid paginated response: repeated next cursor"
            )
        seen_cursors.add(next_cursor)
        cursor = next_cursor

    if combined is None:  # pragma: no cover - the loop always executes once
        combined = {"data": [], "metadata": {}}
    combined_metadata.pop("nextCursor", None)
    combined_metadata.pop("prevCursor", None)
    combined_metadata["hasNextPage"] = False
    combined_metadata["hasPrevPage"] = False
    if isinstance(combined_metadata.get("page"), dict):
        page_metadata = dict(combined_metadata["page"])
        page_metadata["count"] = len(items)
        combined_metadata["page"] = page_metadata
    combined["data"] = items
    combined["metadata"] = combined_metadata
    return combined


def require_changes(**changes: Any) -> None:
    """Reject an update for which every option was omitted."""
    if all(value is None for value in changes.values()):
        options = ", ".join(f"--{name.replace('_', '-')}" for name in changes)
        raise click.UsageError(f"provide at least one change option: {options}")


def repeated_or_clear(
    values: tuple[T, ...],
    clear: bool,
    *,
    option_name: str,
    clear_option_name: str,
) -> list[T] | None:
    """Turn repeatable flags into an optional list while supporting clearing."""
    if values and clear:
        raise click.UsageError(
            f"--{option_name} cannot be used with --{clear_option_name}"
        )
    if clear:
        return []
    if values:
        return list(values)
    return None


def validate_tag_position(before: str | None, after: str | None) -> None:
    if before is not None and after is not None:
        raise click.UsageError("--before and --after are mutually exclusive")


def list_options(function: Callable[..., T]) -> Callable[..., T]:
    """Common options for all cursor-based list commands."""
    decorators = [
        click.option(
            "--page-size",
            type=click.IntRange(1, 500),
            default=100,
            show_default=True,
            help="Items requested per API page.",
        ),
        click.option(
            "--starting-token", help="Cursor from which to begin listing."
        ),
        click.option(
            "--no-paginate",
            is_flag=True,
            help="Request only one page and retain its cursor metadata.",
        ),
        click.option(
            "--include-counts", is_flag=True, help="Ask the API for count metadata."
        ),
    ]
    for decorator in reversed(decorators):
        function = decorator(function)
    return function


def emit(state: CLIState, result: Any, *, helper: bool = False) -> None:
    state.emit(ensure_envelope(result) if helper else result)
