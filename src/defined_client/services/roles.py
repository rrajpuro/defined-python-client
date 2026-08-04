"""High-level role operations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._common import resource_data

if TYPE_CHECKING:
    from ..client import DefinedClient


class RoleService:
    """Convenience methods that compose low-level role API calls."""

    def __init__(self, client: DefinedClient) -> None:
        self.client = client

    def safe_update(
        self,
        role_id: str,
        *,
        description: str | None = None,
        firewall_rules: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Update a role without resetting omitted fields.

        Fetches the current role state, merges in the provided values,
        and sends the full mutable object back to the API.
        """
        data = resource_data(self.client.roles.get(role_id), "role")

        return self.client.roles.update(
            role_id,
            description=(
                description if description is not None else data.get("description")
            ),
            firewall_rules=(
                firewall_rules
                if firewall_rules is not None
                else data.get("firewallRules")
            ),
        )
