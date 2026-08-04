"""High-level host operations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..exceptions import NotFoundError
from ._common import resource_data
from .pagination import list_all

if TYPE_CHECKING:
    from ..client import DefinedClient


class HostService:
    """Convenience methods that compose low-level host API calls.

    Example::

        from defined_client import DefinedClient
        from defined_client.services import HostService

        with DefinedClient(api_key="...") as client:
            hosts = HostService(client)
            host = hosts.find_by_name("clab-lab01")
            hosts.update_tags(host["id"], ["lab:prod", "role:router"])
    """

    def __init__(self, client: DefinedClient) -> None:
        self.client = client

    # ------------------------------------------------------------------
    # Lookup helpers
    # ------------------------------------------------------------------

    def find_by_name(self, name: str) -> dict[str, Any] | None:
        """Find a host by its name.

        Iterates through all pages because the API has no name filter.

        Returns:
            The host dict, or ``None`` if not found.
        """
        for host in list_all(self.client.hosts.list):
            if host.get("name") == name:
                return host
        return None

    def get_by_name(self, name: str) -> dict[str, Any]:
        """Find a host by name, raising :class:`NotFoundError` if missing."""
        host = self.find_by_name(name)
        if host is None:
            raise NotFoundError(f"Host with name '{name}' not found")
        return host

    # ------------------------------------------------------------------
    # Safe update (GET-merge-PUT)
    # ------------------------------------------------------------------

    def safe_update(
        self,
        host_id: str,
        *,
        name: str | None = None,
        role_id: str | None = None,
        static_addresses: list[str] | None = None,
        listen_port: int | None = None,
        tags: list[str] | None = None,
        config_overrides: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Update a host without resetting omitted fields.

        Fetches the current host state, merges in the provided values,
        and sends the full object back to the API.
        """
        data = resource_data(self.client.hosts.get(host_id), "host")

        return self.client.hosts.update(
            host_id,
            name=name if name is not None else data.get("name"),
            role_id=role_id if role_id is not None else data.get("roleID"),
            static_addresses=(
                static_addresses
                if static_addresses is not None
                else data.get("staticAddresses")
            ),
            listen_port=(
                listen_port if listen_port is not None else data.get("listenPort")
            ),
            tags=tags if tags is not None else data.get("tags"),
            config_overrides=(
                config_overrides
                if config_overrides is not None
                else data.get("configOverrides")
            ),
        )

    # ------------------------------------------------------------------
    # Tag helpers
    # ------------------------------------------------------------------

    def update_tags(self, host_id: str, tags: list[str]) -> dict[str, Any]:
        """Replace a host's tags without touching other fields."""
        return self.safe_update(host_id, tags=tags)

    def add_tag(self, host_id: str, tag: str) -> dict[str, Any]:
        """Add a single tag to a host (deduplicated)."""
        data = resource_data(self.client.hosts.get(host_id), "host")
        current_tags: list[str] = data.get("tags", [])
        if tag not in current_tags:
            current_tags = current_tags + [tag]
        return self.safe_update(host_id, tags=current_tags)

    def remove_tag(self, host_id: str, tag: str) -> dict[str, Any]:
        """Remove a single tag from a host."""
        data = resource_data(self.client.hosts.get(host_id), "host")
        current_tags: list[str] = data.get("tags", [])
        return self.safe_update(host_id, tags=[t for t in current_tags if t != tag])
