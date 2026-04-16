"""High-level route operations."""

from __future__ import annotations

from typing import Any, Dict, Optional, TYPE_CHECKING

from ..exceptions import NotFoundError
from .pagination import list_all

if TYPE_CHECKING:
    from ..client import DefinedClient


class RouteService:
    """Convenience methods that compose low-level route API calls.

    Example::

        from defined_client import DefinedClient
        from defined_client.services import RouteService

        with DefinedClient(api_key="...") as client:
            routes = RouteService(client)
            route = routes.get_by_name("route-clab-lab01")
            routes.update_router_host(route["id"], new_host_id)
    """

    def __init__(self, client: "DefinedClient") -> None:
        self.client = client

    # ------------------------------------------------------------------
    # Lookup helpers
    # ------------------------------------------------------------------

    def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find a route by its name.

        Iterates through all pages because the API has no name filter.

        Returns:
            The route dict, or ``None`` if not found.
        """
        for route in list_all(self.client.routes.list):
            if route.get("name") == name:
                return route
        return None

    def get_by_name(self, name: str) -> Dict[str, Any]:
        """Find a route by name, raising :class:`NotFoundError` if missing."""
        route = self.find_by_name(name)
        if route is None:
            raise NotFoundError(f"Route with name '{name}' not found")
        return route

    # ------------------------------------------------------------------
    # Safe update (GET-merge-PUT)
    # ------------------------------------------------------------------

    def safe_update(
        self,
        route_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        router_host_id: Optional[str] = None,
        routable_cidrs: Optional[Dict] = None,
        firewall_rules: Optional[list] = None,
    ) -> Dict[str, Any]:
        """Update a route without resetting omitted fields.

        Fetches the current route state, merges in the provided values,
        and sends the full object back to the API.
        """
        data = self.client.routes.get(route_id).get("data", {})

        return self.client.routes.update(
            route_id,
            name=name if name is not None else data.get("name"),
            description=(
                description if description is not None else data.get("description")
            ),
            router_host_id=(
                router_host_id
                if router_host_id is not None
                else data.get("routerHostID")
            ),
            routable_cidrs=(
                routable_cidrs
                if routable_cidrs is not None
                else data.get("routableCIDRs")
            ),
            firewall_rules=(
                firewall_rules
                if firewall_rules is not None
                else data.get("firewallRules")
            ),
        )

    # ------------------------------------------------------------------
    # Targeted helpers
    # ------------------------------------------------------------------

    def update_router_host(
        self, route_id: str, host_id: str
    ) -> Dict[str, Any]:
        """Change which host a route points to, preserving all other fields."""
        return self.safe_update(route_id, router_host_id=host_id)
