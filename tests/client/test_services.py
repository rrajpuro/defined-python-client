"""High-level service behavior tests."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from defined_client import DefinedClientError
from defined_client.services import (
    HostService,
    NetworkService,
    RoleService,
    RouteService,
    TagService,
)


def test_role_safe_update_preserves_omitted_values() -> None:
    roles = Mock()
    roles.get.return_value = {
        "data": {
            "name": "existing role",
            "description": "existing description",
            "firewallRules": [{"direction": "inbound"}],
        }
    }
    roles.update.return_value = {"data": {"id": "role-1"}}
    service = RoleService(SimpleNamespace(roles=roles))

    result = service.safe_update("role-1")

    roles.get.assert_called_once_with("role-1")
    roles.update.assert_called_once_with(
        "role-1",
        description="existing description",
        firewall_rules=[{"direction": "inbound"}],
    )
    assert result == {"data": {"id": "role-1"}}


def test_role_safe_update_applies_empty_values() -> None:
    roles = Mock()
    roles.get.return_value = {
        "data": {
            "name": "existing role",
            "description": "existing description",
            "firewallRules": [{"direction": "inbound"}],
        }
    }
    service = RoleService(SimpleNamespace(roles=roles))

    service.safe_update("role-1", description="", firewall_rules=[])

    roles.update.assert_called_once_with(
        "role-1",
        description="",
        firewall_rules=[],
    )


def test_network_safe_update_preserves_omitted_values() -> None:
    networks = Mock()
    networks.get.return_value = {
        "data": {
            "name": "existing network",
            "description": "existing description",
            "lighthousesAsRelays": True,
        }
    }
    networks.update.return_value = {"data": {"id": "network-1"}}
    service = NetworkService(SimpleNamespace(networks=networks))

    result = service.safe_update("network-1")

    networks.get.assert_called_once_with("network-1")
    networks.update.assert_called_once_with(
        "network-1",
        name="existing network",
        description="existing description",
        lighthouses_as_relays=True,
    )
    assert result == {"data": {"id": "network-1"}}


def test_network_safe_update_applies_empty_and_false_values() -> None:
    networks = Mock()
    networks.get.return_value = {
        "data": {
            "name": "existing network",
            "description": "existing description",
            "lighthousesAsRelays": True,
        }
    }
    service = NetworkService(SimpleNamespace(networks=networks))

    service.safe_update(
        "network-1",
        name="",
        description="",
        lighthouses_as_relays=False,
    )

    networks.update.assert_called_once_with(
        "network-1",
        name="",
        description="",
        lighthouses_as_relays=False,
    )


@pytest.mark.parametrize(
    ("service_type", "resource_name", "resource_id"),
    [
        (HostService, "hosts", "host-1"),
        (RoleService, "roles", "role-1"),
        (RouteService, "routes", "route-1"),
        (TagService, "tags", "env:prod"),
        (NetworkService, "networks", "network-1"),
    ],
)
def test_safe_update_aborts_when_get_lacks_resource_data(
    service_type: type,
    resource_name: str,
    resource_id: str,
) -> None:
    resource = Mock()
    resource.get.return_value = {"metadata": {}}
    service = service_type(SimpleNamespace(**{resource_name: resource}))

    with pytest.raises(DefinedClientError, match="missing resource data"):
        service.safe_update(resource_id)

    resource.update.assert_not_called()
