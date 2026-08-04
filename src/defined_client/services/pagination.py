"""Auto-pagination helper for any list endpoint."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


def list_all(
    list_func: Callable[..., dict[str, Any]],
    **kwargs: Any,
) -> list[dict[str, Any]]:
    """Exhaust all pages of a paginated list endpoint and return every item.

    Args:
        list_func: A bound list method from a resource class
            (e.g. ``client.hosts.list``).
        **kwargs: Keyword arguments forwarded to *list_func* on every call.
            ``cursor`` and ``page_size`` are managed automatically but can
            be overridden.

    Returns:
        A flat list of all resource items across every page.

    Example::

        from defined_client.services import list_all
        all_hosts = list_all(client.hosts.list)
    """
    kwargs.setdefault("page_size", 100)
    items: list[dict[str, Any]] = []
    cursor = None

    while True:
        kwargs["cursor"] = cursor
        response = list_func(**kwargs)
        items.extend(response.get("data", []))

        metadata = response.get("metadata", {})
        if not metadata.get("hasNextPage"):
            break
        cursor = metadata.get("nextCursor")
        if not cursor:
            break

    return items
