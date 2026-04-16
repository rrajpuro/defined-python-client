"""High-level tag operations."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from .pagination import list_all

if TYPE_CHECKING:
    from ..client import DefinedClient


class TagService:
    """Convenience methods that compose low-level tag API calls.

    Example::

        from defined_client import DefinedClient
        from defined_client.services import TagService

        with DefinedClient(api_key="...") as client:
            tags = TagService(client)
            tags.subscribe_route("lab:prod", route_id)
            tags.unsubscribe_route("lab:prod", route_id)
    """

    def __init__(self, client: "DefinedClient") -> None:
        self.client = client

    # ------------------------------------------------------------------
    # Lookup helpers
    # ------------------------------------------------------------------

    def find_by_key(self, key: str) -> List[Dict[str, Any]]:
        """Find all tags with a given key prefix (e.g. ``"lab"``).

        Returns:
            List of tag dicts whose name starts with ``key:``.
        """
        return [
            tag
            for tag in list_all(self.client.tags.list)
            if tag.get("name", "").startswith(f"{key}:")
        ]

    # ------------------------------------------------------------------
    # Safe update (GET-merge-PUT)
    # ------------------------------------------------------------------

    def safe_update(
        self,
        tag: str,
        *,
        description: Optional[str] = None,
        config_overrides: Optional[List[Dict[str, Any]]] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
        route_subscriptions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Update a tag without resetting omitted fields.

        Fetches the current tag state, merges in the provided values,
        and sends the full object back to the API.

        Note: ``before`` and ``after`` are positional directives, not
        preserved state — they are only forwarded when explicitly provided.
        """
        data = self.client.tags.get(tag).get("data", {})

        return self.client.tags.update(
            tag,
            description=(
                description if description is not None else data.get("description")
            ),
            config_overrides=(
                config_overrides
                if config_overrides is not None
                else data.get("configOverrides")
            ),
            before=before,
            after=after,
            route_subscriptions=(
                route_subscriptions
                if route_subscriptions is not None
                else data.get("routeSubscriptions")
            ),
        )

    # ------------------------------------------------------------------
    # Route subscription helpers
    # ------------------------------------------------------------------

    def subscribe_route(self, tag: str, route_id: str) -> Dict[str, Any]:
        """Add a route subscription to a tag (idempotent)."""
        data = self.client.tags.get(tag).get("data", {})
        current = data.get("routeSubscriptions", [])
        if route_id in current:
            return {"data": data}
        return self.safe_update(tag, route_subscriptions=current + [route_id])

    def unsubscribe_route(self, tag: str, route_id: str) -> Dict[str, Any]:
        """Remove a route subscription from a tag."""
        data = self.client.tags.get(tag).get("data", {})
        current = data.get("routeSubscriptions", [])
        return self.safe_update(
            tag, route_subscriptions=[r for r in current if r != route_id]
        )
