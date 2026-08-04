"""In-memory client fake shared by CLI tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


_MISSING = object()


@dataclass
class Call:
    scope: str
    method: str
    args: tuple[Any, ...]
    kwargs: dict[str, Any]


class FakeResource:
    def __init__(self, factory: "FakeClientFactory", name: str) -> None:
        self.factory = factory
        self.name = name

    def __getattr__(self, method: str) -> Callable[..., Any]:
        def invoke(*args: Any, **kwargs: Any) -> Any:
            return self.factory.dispatch(self.name, method, args, kwargs)

        return invoke


class FakeClientFactory:
    """Configure responses for clients constructed by the CLI."""

    resource_names = (
        "hosts",
        "roles",
        "routes",
        "tags",
        "networks",
        "audit_logs",
        "downloads",
    )

    def __init__(self) -> None:
        self.handlers: dict[tuple[str, str], Any] = {}
        self.calls: list[Call] = []
        self.instances: list[Any] = []
        self.constructor_calls: list[dict[str, Any]] = []

    def respond(self, scope: str, method: str, response: Any) -> None:
        self.handlers[(scope, method)] = response

    def dispatch(
        self,
        scope: str,
        method: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        self.calls.append(Call(scope, method, args, kwargs))
        handler = self.handlers.get((scope, method), _MISSING)
        if handler is _MISSING:
            if method == "list":
                return {
                    "data": [],
                    "metadata": {"hasNextPage": False, "hasPrevPage": False},
                }
            return {"data": {}, "metadata": {}}
        if isinstance(handler, list):
            handler = handler.pop(0)
        if isinstance(handler, BaseException):
            raise handler
        if callable(handler):
            return handler(*args, **kwargs)
        return handler

    def client_class(self) -> type[Any]:
        factory = self

        class FakeClient:
            def __init__(
                self,
                api_key: str | None = None,
                base_url: str | None = None,
                timeout: float = 30,
            ) -> None:
                self.closed = False
                factory.instances.append(self)
                factory.constructor_calls.append(
                    {
                        "api_key": api_key,
                        "base_url": base_url,
                        "timeout": timeout,
                    }
                )
                for name in factory.resource_names:
                    setattr(self, name, FakeResource(factory, name))

            def get(self, *args: Any, **kwargs: Any) -> Any:
                return factory.dispatch("client", "get", args, kwargs)

            def post(self, *args: Any, **kwargs: Any) -> Any:
                return factory.dispatch("client", "post", args, kwargs)

            def put(self, *args: Any, **kwargs: Any) -> Any:
                return factory.dispatch("client", "put", args, kwargs)

            def delete(self, *args: Any, **kwargs: Any) -> Any:
                return factory.dispatch("client", "delete", args, kwargs)

            def close(self) -> None:
                self.closed = True

        return FakeClient
