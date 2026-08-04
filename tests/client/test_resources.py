"""Request contract tests for the low-level resource wrappers."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest

from defined_client.resources import (
    AuditLogs,
    Downloads,
    Hosts,
    Networks,
    Roles,
    Routes,
    Tags,
)


class RecordingClient:
    """Record resource calls without making HTTP requests."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str, dict[str, Any]]] = []
        self.response = {"data": {"id": "result-one"}, "metadata": {}}

    def _record(self, method: str, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        self.calls.append((method, endpoint, kwargs))
        return self.response

    def get(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        return self._record("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        return self._record("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        return self._record("PUT", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        return self._record("DELETE", endpoint, **kwargs)


ResourceCall = Callable[[RecordingClient], dict[str, Any]]


@pytest.mark.parametrize(
    ("operation", "expected_call"),
    [
        pytest.param(
            lambda client: Hosts(client).get("host-one"),
            ("GET", "/v1/hosts/host-one", {}),
            id="get-host",
        ),
        pytest.param(
            lambda client: Hosts(client).delete("host-one"),
            ("DELETE", "/v1/hosts/host-one", {}),
            id="delete-host",
        ),
        pytest.param(
            lambda client: Hosts(client).block("host-one"),
            ("POST", "/v1/hosts/host-one/block", {}),
            id="block-host",
        ),
        pytest.param(
            lambda client: Hosts(client).unblock("host-one"),
            ("POST", "/v1/hosts/host-one/unblock", {}),
            id="unblock-host",
        ),
        pytest.param(
            lambda client: Hosts(client).create_enrollment_code("host-one"),
            ("POST", "/v1/hosts/host-one/enrollment-code", {}),
            id="create-enrollment-code",
        ),
        pytest.param(
            lambda client: Roles(client).get("role-one"),
            ("GET", "/v1/roles/role-one", {}),
            id="get-role",
        ),
        pytest.param(
            lambda client: Roles(client).delete("role-one"),
            ("DELETE", "/v1/roles/role-one", {}),
            id="delete-role",
        ),
        pytest.param(
            lambda client: Routes(client).get("route-one"),
            ("GET", "/v1/routes/route-one", {}),
            id="get-route",
        ),
        pytest.param(
            lambda client: Routes(client).delete("route-one"),
            ("DELETE", "/v1/routes/route-one", {}),
            id="delete-route",
        ),
        pytest.param(
            lambda client: Tags(client).get("env:prod"),
            ("GET", "/v1/tags/env:prod", {}),
            id="get-tag",
        ),
        pytest.param(
            lambda client: Tags(client).delete("env:prod"),
            ("DELETE", "/v1/tags/env:prod", {}),
            id="delete-tag",
        ),
        pytest.param(
            lambda client: Networks(client).get("network-one"),
            ("GET", "/v1/networks/network-one", {}),
            id="get-network",
        ),
        pytest.param(
            lambda client: Downloads(client).list(),
            ("GET", "/v1/downloads", {}),
            id="list-downloads",
        ),
    ],
)
def test_simple_resource_operations_dispatch_expected_request(
    operation: ResourceCall,
    expected_call: tuple[str, str, dict[str, Any]],
) -> None:
    client = RecordingClient()

    result = operation(client)

    assert result is client.response
    assert client.calls == [expected_call]


@pytest.mark.parametrize(
    ("operation", "expected_call"),
    [
        pytest.param(
            lambda client: Hosts(client).create(
                name="edge",
                network_id="network-one",
                role_id="role-one",
                static_addresses=["203.0.113.10:4242"],
                tags=["env:prod"],
            ),
            (
                "POST",
                "/v1/hosts",
                {
                    "json": {
                        "name": "edge",
                        "networkID": "network-one",
                        "listenPort": 0,
                        "isLighthouse": False,
                        "isRelay": False,
                        "roleID": "role-one",
                        "staticAddresses": ["203.0.113.10:4242"],
                        "tags": ["env:prod"],
                    }
                },
            ),
            id="create-host",
        ),
        pytest.param(
            lambda client: Hosts(client).create_with_enrollment(
                name="edge", network_id="network-one", is_lighthouse=True
            ),
            (
                "POST",
                "/v1/host-and-enrollment-code",
                {
                    "json": {
                        "name": "edge",
                        "networkID": "network-one",
                        "listenPort": 0,
                        "isLighthouse": True,
                        "isRelay": False,
                    }
                },
            ),
            id="create-host-with-enrollment",
        ),
        pytest.param(
            lambda client: Hosts(client).update(
                "host-one", listen_port=0, tags=[], config_overrides=[]
            ),
            (
                "PUT",
                "/v2/hosts/host-one",
                {"json": {"listenPort": 0, "tags": [], "configOverrides": []}},
            ),
            id="update-host-preserves-explicit-empty-values",
        ),
        pytest.param(
            lambda client: Hosts(client).debug_command(
                "host-one", "StreamLogs", durationSeconds=60, level="info"
            ),
            (
                "POST",
                "/v1/hosts/host-one/command",
                {
                    "json": {
                        "command": "StreamLogs",
                        "args": {"durationSeconds": 60, "level": "info"},
                    }
                },
            ),
            id="host-debug-command",
        ),
        pytest.param(
            lambda client: Roles(client).create(
                "web", description="", firewall_rules=[]
            ),
            (
                "POST",
                "/v1/roles",
                {"json": {"name": "web", "description": "", "firewallRules": []}},
            ),
            id="create-role",
        ),
        pytest.param(
            lambda client: Roles(client).update(
                "role-one", description="updated", firewall_rules=[]
            ),
            (
                "PUT",
                "/v1/roles/role-one",
                {
                    "json": {
                        "description": "updated",
                        "firewallRules": [],
                    }
                },
            ),
            id="update-role",
        ),
        pytest.param(
            lambda client: Routes(client).create(
                "office",
                router_host_id="host-one",
                routable_cidrs={"10.0.0.0/8": {"install": True}},
            ),
            (
                "POST",
                "/v1/routes",
                {
                    "json": {
                        "name": "office",
                        "routerHostID": "host-one",
                        "routableCIDRs": {"10.0.0.0/8": {"install": True}},
                    }
                },
            ),
            id="create-route",
        ),
        pytest.param(
            lambda client: Routes(client).update(
                "route-one", "office", description="", firewall_rules=[]
            ),
            (
                "PUT",
                "/v1/routes/route-one",
                {
                    "json": {
                        "name": "office",
                        "description": "",
                        "firewallRules": [],
                    }
                },
            ),
            id="update-route",
        ),
        pytest.param(
            lambda client: Tags(client).create(
                "env:prod", after="env:test", route_subscriptions=[]
            ),
            (
                "POST",
                "/v1/tags",
                {
                    "json": {
                        "name": "env:prod",
                        "after": "env:test",
                        "routeSubscriptions": [],
                    }
                },
            ),
            id="create-tag",
        ),
        pytest.param(
            lambda client: Tags(client).update(
                "env:prod", description="", config_overrides=[]
            ),
            (
                "PUT",
                "/v1/tags/env:prod",
                {"json": {"description": "", "configOverrides": []}},
            ),
            id="update-tag",
        ),
        pytest.param(
            lambda client: Networks(client).create(
                "production",
                "100.64.0.0/24",
                lighthouses_as_relays=False,
            ),
            (
                "POST",
                "/v1/networks",
                {
                    "json": {
                        "name": "production",
                        "cidr": "100.64.0.0/24",
                        "lighthousesAsRelays": False,
                    }
                },
            ),
            id="create-network",
        ),
        pytest.param(
            lambda client: Networks(client).update(
                "network-one", "production", description=""
            ),
            (
                "PUT",
                "/v1/networks/network-one",
                {"json": {"name": "production", "description": ""}},
            ),
            id="update-network",
        ),
    ],
)
def test_resource_writes_translate_arguments_to_api_fields(
    operation: ResourceCall,
    expected_call: tuple[str, str, dict[str, Any]],
) -> None:
    client = RecordingClient()

    result = operation(client)

    assert result is client.response
    assert client.calls == [expected_call]


@pytest.mark.parametrize(
    ("operation", "expected_endpoint", "expected_params"),
    [
        pytest.param(
            lambda client: Hosts(client).list(
                include_counts=True,
                cursor="cursor-two",
                page_size=50,
                filter_is_blocked=False,
                filter_is_lighthouse=True,
                filter_role_id="role-one",
            ),
            "/v1/hosts",
            {
                "includeCounts": True,
                "cursor": "cursor-two",
                "pageSize": 50,
                "filter.isBlocked": False,
                "filter.isLighthouse": True,
                "filter.roleID": "role-one",
            },
            id="hosts",
        ),
        pytest.param(
            lambda client: Roles(client).list(page_size=10),
            "/v1/roles",
            {"includeCounts": False, "pageSize": 10},
            id="roles",
        ),
        pytest.param(
            lambda client: Routes(client).list(cursor="cursor-two"),
            "/v1/routes",
            {"includeCounts": False, "cursor": "cursor-two", "pageSize": 25},
            id="routes",
        ),
        pytest.param(
            lambda client: Tags(client).list(include_counts=True),
            "/v2/tags",
            {"includeCounts": True, "pageSize": 25},
            id="tags",
        ),
        pytest.param(
            lambda client: Networks(client).list(),
            "/v1/networks",
            {"includeCounts": False, "pageSize": 25},
            id="networks",
        ),
        pytest.param(
            lambda client: AuditLogs(client).list(
                filter_target_id="host-one", filter_target_type="host"
            ),
            "/v1/audit-logs",
            {
                "includeCounts": False,
                "pageSize": 25,
                "filter.targetID": "host-one",
                "filter.targetType": "host",
            },
            id="audit-logs",
        ),
    ],
)
def test_list_operations_map_pagination_and_filters(
    operation: ResourceCall,
    expected_endpoint: str,
    expected_params: dict[str, Any],
) -> None:
    client = RecordingClient()

    result = operation(client)

    assert result is client.response
    assert client.calls == [("GET", expected_endpoint, {"params": expected_params})]
