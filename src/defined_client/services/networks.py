"""High-level network operations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from ._common import resource_data

if TYPE_CHECKING:
    from ..client import DefinedClient


class NetworkService:
    """Convenience methods that compose low-level network API calls."""

    def __init__(self, client: DefinedClient) -> None:
        self.client = client

    def safe_update(
        self,
        network_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        lighthouses_as_relays: bool | None = None,
    ) -> dict[str, Any]:
        """Update a network without resetting omitted fields.

        Fetches the current network state, merges in the provided values,
        and sends the full mutable object back to the API.
        """
        data = resource_data(self.client.networks.get(network_id), "network")
        current_name = cast(str, data["name"])

        return self.client.networks.update(
            network_id,
            name=name if name is not None else current_name,
            description=(
                description if description is not None else data.get("description")
            ),
            lighthouses_as_relays=(
                lighthouses_as_relays
                if lighthouses_as_relays is not None
                else data.get("lighthousesAsRelays")
            ),
        )
