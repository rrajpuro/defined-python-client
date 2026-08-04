"""High-level network operations."""

from __future__ import annotations

from typing import Any, Dict, Optional, TYPE_CHECKING

from ._common import resource_data

if TYPE_CHECKING:
    from ..client import DefinedClient


class NetworkService:
    """Convenience methods that compose low-level network API calls."""

    def __init__(self, client: "DefinedClient") -> None:
        self.client = client

    def safe_update(
        self,
        network_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        lighthouses_as_relays: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Update a network without resetting omitted fields.

        Fetches the current network state, merges in the provided values,
        and sends the full mutable object back to the API.
        """
        data = resource_data(self.client.networks.get(network_id), "network")

        return self.client.networks.update(
            network_id,
            name=name if name is not None else data.get("name"),
            description=(
                description if description is not None else data.get("description")
            ),
            lighthouses_as_relays=(
                lighthouses_as_relays
                if lighthouses_as_relays is not None
                else data.get("lighthousesAsRelays")
            ),
        )
