"""Host commands."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import click

from defined_client.services import HostService

from .core import (
    JSON_ARRAY,
    JSON_OBJECT,
    CLIState,
    emit,
    list_options,
    paginate,
    repeated_or_clear,
    require_changes,
)


@click.group()
def hosts() -> None:
    """Create, inspect, and manage hosts."""


def _host_create_options[F: Callable[..., Any]](function: F) -> F:
    decorators = [
        click.option("--name", required=True, help="Host name."),
        click.option("--network-id", required=True, help="Network identifier."),
        click.option("--role-id", help="Role identifier."),
        click.option("--ip-address", help="Managed network IPv4 address."),
        click.option(
            "--static-address",
            "static_addresses",
            multiple=True,
            help="Static host:port address; repeat for multiple values.",
        ),
        click.option(
            "--listen-port",
            type=click.IntRange(0, 65535),
            default=0,
            show_default=True,
            help="Nebula UDP listen port.",
        ),
        click.option("--is-lighthouse", is_flag=True, help="Create a lighthouse."),
        click.option("--is-relay", is_flag=True, help="Create a relay."),
        click.option(
            "--tag", "tags", multiple=True, help="Host tag; repeat for multiple values."
        ),
        click.option(
            "--config-overrides",
            type=JSON_ARRAY,
            metavar="JSON|file://PATH",
            help="Config overrides JSON array.",
        ),
    ]
    for decorator in reversed(decorators):
        function = decorator(function)
    return function


def _validate_host_create(
    *,
    static_addresses: tuple[str, ...],
    listen_port: int,
    is_lighthouse: bool,
    is_relay: bool,
) -> None:
    if is_lighthouse and is_relay:
        raise click.UsageError("a host cannot be both a lighthouse and a relay")
    if is_lighthouse and not static_addresses:
        raise click.UsageError("--is-lighthouse requires --static-address")
    if (is_lighthouse or is_relay) and listen_port == 0:
        kind = "--is-lighthouse" if is_lighthouse else "--is-relay"
        raise click.UsageError(f"{kind} requires a non-zero --listen-port")


def _create_host(
    state: CLIState,
    *,
    with_enrollment: bool,
    name: str,
    network_id: str,
    role_id: str | None,
    ip_address: str | None,
    static_addresses: tuple[str, ...],
    listen_port: int,
    is_lighthouse: bool,
    is_relay: bool,
    tags: tuple[str, ...],
    config_overrides: list[dict[str, Any]] | None,
) -> None:
    _validate_host_create(
        static_addresses=static_addresses,
        listen_port=listen_port,
        is_lighthouse=is_lighthouse,
        is_relay=is_relay,
    )
    resource = state.get_client().hosts
    method = resource.create_with_enrollment if with_enrollment else resource.create
    result = method(
        name=name,
        network_id=network_id,
        role_id=role_id,
        ip_address=ip_address,
        static_addresses=list(static_addresses) or None,
        listen_port=listen_port,
        is_lighthouse=is_lighthouse,
        is_relay=is_relay,
        tags=list(tags) or None,
        config_overrides=config_overrides,
    )
    emit(state, result)


@hosts.command("create")
@_host_create_options
@click.pass_obj
def create_host(state: CLIState, **kwargs: Any) -> None:
    """Create a host, lighthouse, or relay."""
    _create_host(state, with_enrollment=False, **kwargs)


@hosts.command("create-with-enrollment")
@_host_create_options
@click.pass_obj
def create_host_with_enrollment(state: CLIState, **kwargs: Any) -> None:
    """Create a host together with a one-time enrollment code."""
    _create_host(state, with_enrollment=True, **kwargs)


@hosts.command("list")
@list_options
@click.option("--filter-endpoint-oidc-user-id")
@click.option(
    "--filter-is-blocked/--no-filter-is-blocked",
    default=None,
    help="Filter block state.",
)
@click.option(
    "--filter-is-lighthouse/--no-filter-is-lighthouse",
    default=None,
    help="Filter lighthouse state.",
)
@click.option(
    "--filter-is-relay/--no-filter-is-relay", default=None, help="Filter relay state."
)
@click.option("--filter-metadata-last-seen-at", type=click.Choice(["null"]))
@click.option(
    "--filter-metadata-platform",
    type=click.Choice(["mobile", "dnclient", "null"]),
)
@click.option(
    "--filter-metadata-update-available/--no-filter-metadata-update-available",
    default=None,
    help="Filter update availability.",
)
@click.option("--filter-role-id")
@click.pass_obj
def list_hosts(
    state: CLIState,
    page_size: int,
    starting_token: str | None,
    no_paginate: bool,
    include_counts: bool,
    **filters: Any,
) -> None:
    """List hosts, automatically following pagination cursors."""
    result = paginate(
        state.get_client().hosts.list,
        page_size=page_size,
        starting_token=starting_token,
        no_paginate=no_paginate,
        include_counts=include_counts,
        **filters,
    )
    emit(state, result)


@hosts.command("get")
@click.option("--host-id", required=True)
@click.pass_obj
def get_host(state: CLIState, host_id: str) -> None:
    """Get a host by identifier."""
    emit(state, state.get_client().hosts.get(host_id))


@hosts.command("get-by-name")
@click.option("--name", required=True)
@click.pass_obj
def get_host_by_name(state: CLIState, name: str) -> None:
    """Get a host by exact name, failing when it does not exist."""
    result = HostService(state.get_client()).get_by_name(name)
    emit(state, result, helper=True)


@hosts.command("find-by-name")
@click.option("--name", required=True)
@click.pass_obj
def find_host_by_name(state: CLIState, name: str) -> None:
    """Find a host by exact name, returning null when it does not exist."""
    result = HostService(state.get_client()).find_by_name(name)
    emit(state, result, helper=True)


@hosts.command("update")
@click.option("--host-id", required=True)
@click.option("--name")
@click.option("--role-id")
@click.option("--static-address", "static_addresses", multiple=True)
@click.option("--clear-static-addresses", is_flag=True)
@click.option("--listen-port", type=click.IntRange(0, 65535))
@click.option("--tag", "tags", multiple=True)
@click.option("--clear-tags", is_flag=True)
@click.option("--config-overrides", type=JSON_ARRAY, metavar="JSON|file://PATH")
@click.pass_obj
def update_host(
    state: CLIState,
    host_id: str,
    name: str | None,
    role_id: str | None,
    static_addresses: tuple[str, ...],
    clear_static_addresses: bool,
    listen_port: int | None,
    tags: tuple[str, ...],
    clear_tags: bool,
    config_overrides: list[dict[str, Any]] | None,
) -> None:
    """Safely update fields while preserving omitted host values."""
    static_address_values = repeated_or_clear(
        static_addresses,
        clear_static_addresses,
        option_name="static-address",
        clear_option_name="clear-static-addresses",
    )
    tag_values = repeated_or_clear(
        tags, clear_tags, option_name="tag", clear_option_name="clear-tags"
    )
    require_changes(
        name=name,
        role_id=role_id,
        static_addresses=static_address_values,
        listen_port=listen_port,
        tags=tag_values,
        config_overrides=config_overrides,
    )
    result = HostService(state.get_client()).safe_update(
        host_id,
        name=name,
        role_id=role_id,
        static_addresses=static_address_values,
        listen_port=listen_port,
        tags=tag_values,
        config_overrides=config_overrides,
    )
    emit(state, result)


@hosts.command("replace")
@click.option("--host-id", required=True)
@click.option("--document", required=True, type=JSON_OBJECT, metavar="JSON|file://PATH")
@click.pass_obj
def replace_host(state: CLIState, host_id: str, document: dict[str, Any]) -> None:
    """Replace host fields with an API-shaped JSON document."""
    emit(state, state.get_client().put(f"/v2/hosts/{host_id}", json=document))


@hosts.command("delete")
@click.option("--host-id", required=True)
@click.pass_obj
def delete_host(state: CLIState, host_id: str) -> None:
    """Delete a host without prompting."""
    emit(state, state.get_client().hosts.delete(host_id))


def _host_action(
    name: str, help_text: str
) -> Callable[[Callable[..., Any]], click.Command]:
    def decorator(function: Callable[..., Any]) -> click.Command:
        return hosts.command(name, help=help_text)(
            click.option("--host-id", required=True)(click.pass_obj(function))
        )

    return decorator


@_host_action("block", "Block a host.")
def block_host(state: CLIState, host_id: str) -> None:
    emit(state, state.get_client().hosts.block(host_id))


@_host_action("unblock", "Unblock a host.")
def unblock_host(state: CLIState, host_id: str) -> None:
    emit(state, state.get_client().hosts.unblock(host_id))


@_host_action("create-enrollment-code", "Create a one-time host enrollment code.")
def create_enrollment_code(state: CLIState, host_id: str) -> None:
    emit(state, state.get_client().hosts.create_enrollment_code(host_id))


_DEBUG_COMMANDS = [
    "StreamLogs",
    "CreateTunnel",
    "PrintTunnel",
    "PrintCert",
    "QueryLighthouse",
    "DebugStack",
]
_TARGET_COMMANDS = {"CreateTunnel", "PrintTunnel", "PrintCert", "QueryLighthouse"}
_LOG_LEVELS = {"panic", "fatal", "error", "warning", "info", "debug"}


def _validate_debug_args(command: str, args: dict[str, Any]) -> None:
    if command in _TARGET_COMMANDS:
        if not isinstance(args.get("target"), str) or not args["target"]:
            raise click.UsageError(
                f"{command} requires a string target in --command-args"
            )
    elif command == "StreamLogs":
        duration = args.get("durationSeconds")
        level = args.get("level")
        if isinstance(duration, bool) or not isinstance(duration, (int, float)):
            raise click.UsageError(
                "StreamLogs requires numeric durationSeconds in --command-args"
            )
        if not 0 <= duration <= 600:
            raise click.UsageError(
                "StreamLogs durationSeconds must be between 0 and 600"
            )
        if level not in _LOG_LEVELS:
            raise click.UsageError(
                "StreamLogs level must be panic, fatal, error, warning, info, or debug"
            )
    elif command == "DebugStack" and args:
        raise click.UsageError("DebugStack does not accept nonempty --command-args")


@hosts.command("debug-command")
@click.option("--host-id", required=True)
@click.option(
    "--command", "command_type", type=click.Choice(_DEBUG_COMMANDS), required=True
)
@click.option("--command-args", type=JSON_OBJECT, metavar="JSON|file://PATH")
@click.pass_obj
def debug_host(
    state: CLIState,
    host_id: str,
    command_type: str,
    command_args: dict[str, Any] | None,
) -> None:
    """Run a validated debug command on a connected host."""
    args = command_args or {}
    _validate_debug_args(command_type, args)
    body = {"command": command_type, "args": args}
    timeout = state.timeout
    if command_type == "StreamLogs":
        timeout = max(timeout, float(args["durationSeconds"]) + 30.0)
    result = state.get_client().post(
        f"/v1/hosts/{host_id}/command", json=body, timeout=timeout
    )
    emit(state, result)


@hosts.command("update-tags")
@click.option("--host-id", required=True)
@click.option("--tag", "tags", multiple=True)
@click.option("--clear-tags", is_flag=True)
@click.pass_obj
def update_host_tags(
    state: CLIState, host_id: str, tags: tuple[str, ...], clear_tags: bool
) -> None:
    """Replace all tags on a host."""
    tag_values = repeated_or_clear(
        tags, clear_tags, option_name="tag", clear_option_name="clear-tags"
    )
    if tag_values is None:
        raise click.UsageError("provide --tag or --clear-tags")
    emit(
        state,
        HostService(state.get_client()).update_tags(host_id, tag_values),
        helper=True,
    )


@hosts.command("add-tag")
@click.option("--host-id", required=True)
@click.option("--tag", required=True)
@click.pass_obj
def add_host_tag(state: CLIState, host_id: str, tag: str) -> None:
    """Add one host tag idempotently."""
    emit(
        state,
        HostService(state.get_client()).add_tag(host_id, tag),
        helper=True,
    )


@hosts.command("remove-tag")
@click.option("--host-id", required=True)
@click.option("--tag", required=True)
@click.pass_obj
def remove_host_tag(state: CLIState, host_id: str, tag: str) -> None:
    """Remove one host tag."""
    emit(
        state,
        HostService(state.get_client()).remove_tag(host_id, tag),
        helper=True,
    )
