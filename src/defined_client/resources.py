"""Resource classes for API endpoints"""

from typing import Optional, Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .client import DefinedClient


class BaseResource:
    """Base resource class with common functionality.

    Provides a small helper to build query parameters and stores a reference
    to the :class:`DefinedClient` used to perform HTTP requests.
    """

    def __init__(self, client: "DefinedClient") -> None:
        """Create a new resource wrapper.

        Args:
            client: The :class:`DefinedClient` instance used to make requests.
        """
        self.client: "DefinedClient" = client

    def _build_params(self, **kwargs) -> Dict[str, Any]:
        """Build query parameters, filtering out None values"""
        return {k: v for k, v in kwargs.items() if v is not None}


class Hosts(BaseResource):
    """Host management endpoints"""

    def create(
        self,
        name: str,
        network_id: str,
        role_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        static_addresses: Optional[List[str]] = None,
        listen_port: int = 0,
        is_lighthouse: bool = False,
        is_relay: bool = False,
        tags: Optional[List[str]] = None,
        config_overrides: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Create a new host, lighthouse, or relay.

        Token scope required: ``hosts:create``.

        Args:
            name: Name of the host.
            network_id: Network ID to attach the host to.
            role_id: Optional role ID to assign.
            ip_address: Optional static IP to assign.
            static_addresses: Optional list of static addresses.
            listen_port: UDP port for nebula.
            is_lighthouse: True to create a lighthouse.
            is_relay: True to create a relay.
            tags: Optional list of tags.
            config_overrides: Optional config overrides for the host.

        Returns:
            The created host data as a dictionary (or empty dict if not provided).
        """
        body: Dict[str, Any] = {
            "name": name,
            "networkID": network_id,
            "listenPort": listen_port,
            "isLighthouse": is_lighthouse,
            "isRelay": is_relay,
        }

        if role_id:
            body["roleID"] = role_id
        if ip_address:
            body["ipAddress"] = ip_address
        if static_addresses:
            body["staticAddresses"] = static_addresses
        if tags:
            body["tags"] = tags
        if config_overrides:
            body["configOverrides"] = config_overrides

        response: Dict[str, Any] = self.client.post("/v1/hosts", json=body)
        return response.get("data", {})

    def list(
        self,
        include_counts: bool = False,
        cursor: Optional[str] = None,
        page_size: int = 25,
        filter_endpoint_oidc_user_id: Optional[str] = None,
        filter_is_blocked: Optional[bool] = None,
        filter_is_lighthouse: Optional[bool] = None,
        filter_is_relay: Optional[bool] = None,
        filter_metadata_last_seen_at: Optional[str] = None,
        filter_metadata_platform: Optional[str] = None,
        filter_metadata_update_available: Optional[bool] = None,
        filter_role_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get a paginated list of hosts.

        Token scope required: ``hosts:list``.

        Returns:
            Raw API response containing pagination metadata and host list.
        """
        params = self._build_params(
            includeCounts=include_counts,
            cursor=cursor,
            pageSize=page_size,
            **{
                "filter.endpointOIDCUserID": filter_endpoint_oidc_user_id,
                "filter.isBlocked": filter_is_blocked,
                "filter.isLighthouse": filter_is_lighthouse,
                "filter.isRelay": filter_is_relay,
                "filter.metadata.lastSeenAt": filter_metadata_last_seen_at,
                "filter.metadata.platform": filter_metadata_platform,
                "filter.metadata.updateAvailable": filter_metadata_update_available,
                "filter.roleID": filter_role_id,
            }
        )
        response: Dict[str, Any] = self.client.get("/v1/hosts", params=params)
        return response

    def get(self, host_id: str) -> Dict[str, Any]:
        """Get a specific host by ID.

        Token scope required: ``hosts:read``.

        Args:
            host_id: The host identifier.

        Returns:
            Host data as a dictionary (or empty dict if not provided).
        """
        response: Dict[str, Any] = self.client.get(f"/v1/hosts/{host_id}")
        return response.get("data", {})

    def delete(self, host_id: str) -> Dict[str, Any]:
        """Delete a host.

        Token scope required: ``hosts:delete``.

        Args:
            host_id: The host identifier.

        Returns:
            API response data (often empty dict).
        """
        response: Dict[str, Any] = self.client.delete(f"/v1/hosts/{host_id}")
        return response.get("data", {})

    def update(
        self,
        host_id: str,
        name: Optional[str] = None,
        role_id: Optional[str] = None,
        static_addresses: Optional[List[str]] = None,
        listen_port: Optional[int] = None,
        tags: Optional[List[str]] = None,
        config_overrides: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Edit a host.

        Token scope required: ``hosts:update``.

        Args:
            host_id: ID of the host to update.
            name: Optional new name.
            role_id: Optional role ID.
            static_addresses: Optional list of static addresses.
            listen_port: Optional listen port.
            tags: Optional list of tags.
            config_overrides: Optional config overrides.

        Returns:
            Updated host data as a dictionary (or empty dict if not provided).
        """
        body: Dict[str, Any] = {}

        if name is not None:
            body["name"] = name
        if role_id is not None:
            body["roleID"] = role_id
        if static_addresses is not None:
            body["staticAddresses"] = static_addresses
        if listen_port is not None:
            body["listenPort"] = listen_port
        if tags is not None:
            body["tags"] = tags
        if config_overrides is not None:
            body["configOverrides"] = config_overrides

        response: Dict[str, Any] = self.client.put(f"/v2/hosts/{host_id}", json=body)
        return response.get("data", {})

    def block(self, host_id: str) -> Dict[str, Any]:
        """Block a host.

        Token scope required: ``hosts:block``.

        Args:
            host_id: The host identifier.

        Returns:
            API response data.
        """
        response: Dict[str, Any] = self.client.post(f"/v1/hosts/{host_id}/block")
        return response.get("data", {})

    def unblock(self, host_id: str) -> Dict[str, Any]:
        """Unblock a host.

        Token scope required: ``hosts:unblock``.

        Args:
            host_id: The host identifier.

        Returns:
            API response data.
        """
        response: Dict[str, Any] = self.client.post(f"/v1/hosts/{host_id}/unblock")
        return response.get("data", {})

    def debug_command(
        self, host_id: str, command_type: str, **kwargs
    ) -> Dict[str, Any]:
        """Send debug commands to a host.

        Token scope required: ``hosts:debug``.

        Args:
            host_id: The host identifier.
            command_type: The debug command to run (e.g. ``StreamLogs``).
            **kwargs: Command-specific arguments passed under the ``args`` key.

        Returns:
            Command response data.
        """
        body: Dict[str, Any] = {"command": command_type}

        if kwargs:
            body["args"] = kwargs

        response: Dict[str, Any] = self.client.post(f"/v1/hosts/{host_id}/command", json=body)
        return response.get("data", {})

    def create_enrollment_code(self, host_id: str) -> Dict[str, Any]:
        """Create an enrollment code for a host.

        Token scope required: ``hosts:enroll``.

        Args:
            host_id: The host identifier.

        Returns:
            Enrollment code data.
        """
        response: Dict[str, Any] = self.client.post(f"/v1/hosts/{host_id}/enrollment-code")
        return response.get("data", {})

    def create_with_enrollment(
        self,
        name: str,
        network_id: str,
        role_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        static_addresses: Optional[List[str]] = None,
        listen_port: int = 0,
        is_lighthouse: bool = False,
        is_relay: bool = False,
        tags: Optional[List[str]] = None,
        config_overrides: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Create a host and an enrollment code in one request.

        Token scopes required: ``hosts:create``, ``hosts:enroll``.

        Returns:
            Created host and enrollment code data.
        """
        body: Dict[str, Any] = {
            "name": name,
            "networkID": network_id,
            "listenPort": listen_port,
            "isLighthouse": is_lighthouse,
            "isRelay": is_relay,
        }

        if role_id:
            body["roleID"] = role_id
        if ip_address:
            body["ipAddress"] = ip_address
        if static_addresses:
            body["staticAddresses"] = static_addresses
        if tags:
            body["tags"] = tags
        if config_overrides:
            body["configOverrides"] = config_overrides

        response: Dict[str, Any] = self.client.post("/v1/host-and-enrollment-code", json=body)
        return response.get("data", {})


class Roles(BaseResource):
    """Role management endpoints"""

    def create(
        self,
        name: str,
        description: Optional[str] = None,
        firewall_rules: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Create a new role.

        Token scope required: ``roles:create``.

        Args:
            name: Name of the role.
            description: Optional description.
            firewall_rules: Optional list of firewall rules.

        Returns:
            Created role data as a dictionary.
        """
        body: Dict[str, Any] = {"name": name}
        if description is not None:
            body["description"] = description
        if firewall_rules is not None:
            body["firewallRules"] = firewall_rules
        response: Dict[str, Any] = self.client.post("/v1/roles", json=body)
        return response.get("data", {})

    def list(
        self,
        include_counts: bool = False,
        cursor: Optional[str] = None,
        page_size: int = 25,
    ) -> Dict[str, Any]:
        """Get a paginated list of roles.

        Token scope required: ``roles:list``.

        Returns:
            Raw API response containing list and pagination metadata.
        """
        params = self._build_params(
            includeCounts=include_counts,
            cursor=cursor,
            pageSize=page_size,
        )
        response: Dict[str, Any] = self.client.get("/v1/roles", params=params)
        return response

    def get(self, role_id: str) -> Dict[str, Any]:
        """Get a specific role by ID.

        Token scope required: ``roles:read``.

        Args:
            role_id: The role identifier.

        Returns:
            Role data as a dictionary (or empty dict if not provided).
        """
        response: Dict[str, Any] = self.client.get(f"/v1/roles/{role_id}")
        return response.get("data", {})

    def update(
        self,
        role_id: str,
        description: Optional[str] = None,
        firewall_rules: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Edit a role.

        Token scope required: ``roles:update``.

        Returns:
            Updated role data as a dictionary.
        """
        body: Dict[str, Any] = {}
        if description is not None:
            body["description"] = description
        if firewall_rules is not None:
            body["firewallRules"] = firewall_rules

        response: Dict[str, Any] = self.client.put(f"/v1/roles/{role_id}", json=body)
        return response.get("data", {})

    def delete(self, role_id: str) -> Dict[str, Any]:
        """Delete a role.

        Token scope required: ``roles:delete``.

        Args:
            role_id: The role identifier.

        Returns:
            API response data.
        """
        response: Dict[str, Any] = self.client.delete(f"/v1/roles/{role_id}")
        return response.get("data", {})


class Routes(BaseResource):
    """Route management endpoints"""

    def create(
        self,
        name: str,
        description: Optional[str] = None,
        router_host_id: Optional[str] = None,
        routable_cidrs: Optional[Dict[str, Dict[str, bool]]] = None,
        firewall_rules: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Create a new route.

        Token scope required: ``routes:create``.

        Args:
            name: Name of the route (1-50 chars).
            description: Optional description (max 255 chars).
            router_host_id: Optional router host ID.
            routable_cidrs: Optional dict mapping IPv4 CIDR ranges to install flags.
            firewall_rules: Optional list of firewall rule objects.

        Returns:
            Created route data as a dictionary.
        """
        body: Dict[str, Any] = {"name": name}
        if description is not None:
            body["description"] = description
        if router_host_id is not None:
            body["routerHostID"] = router_host_id
        if routable_cidrs is not None:
            body["routableCIDRs"] = routable_cidrs
        if firewall_rules is not None:
            body["firewallRules"] = firewall_rules

        response: Dict[str, Any] = self.client.post("/v1/routes", json=body)
        return response.get("data", {})

    def list(
        self,
        include_counts: bool = False,
        cursor: Optional[str] = None,
        page_size: int = 25,
    ) -> Dict[str, Any]:
        """Get a paginated list of routes.

        Token scope required: ``routes:list``.

        Returns:
            Raw API response containing the list and pagination metadata.
        """
        params = self._build_params(
            includeCounts=include_counts,
            cursor=cursor,
            pageSize=page_size,
        )
        response: Dict[str, Any] = self.client.get("/v1/routes", params=params)
        return response

    def get(self, route_id: str) -> Dict[str, Any]:
        """Get a specific route by ID.

        Token scope required: ``routes:read``.

        Args:
            route_id: The route identifier.

        Returns:
            Route data as a dictionary (or empty dict if not provided).
        """
        response: Dict[str, Any] = self.client.get(f"/v1/routes/{route_id}")
        return response.get("data", {})

    def update(
        self,
        route_id: str,
        name: str,
        description: Optional[str] = None,
        router_host_id: Optional[str] = None,
        routable_cidrs: Optional[Dict[str, Dict[str, bool]]] = None,
        firewall_rules: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Edit a route.

        **Caution:** Any properties not provided in the request will be reset to
        their default values. If only changing one firewall rule, be sure to include
        the others as well, otherwise they will be removed.

        Token scope required: ``routes:update``.

        Args:
            route_id: ID of the route to update.
            name: Name of the route (required, max 50 chars).
            description: Optional description (max 255 chars).
            router_host_id: Optional router host ID.
            routable_cidrs: Optional dict mapping CIDR ranges to install flags.
            firewall_rules: Optional list of firewall rule objects.

        Returns:
            Updated route data as a dictionary.
        """
        body: Dict[str, Any] = {"name": name}
        if description is not None:
            body["description"] = description
        if router_host_id is not None:
            body["routerHostID"] = router_host_id
        if routable_cidrs is not None:
            body["routableCIDRs"] = routable_cidrs
        if firewall_rules is not None:
            body["firewallRules"] = firewall_rules

        response: Dict[str, Any] = self.client.put(f"/v1/routes/{route_id}", json=body)
        return response.get("data", {})

    def delete(self, route_id: str) -> Dict[str, Any]:
        """Delete a route.

        Token scope required: ``routes:delete``.

        Args:
            route_id: The route identifier.

        Returns:
            API response data.
        """
        response: Dict[str, Any] = self.client.delete(f"/v1/routes/{route_id}")
        return response.get("data", {})


class Tags(BaseResource):
    """Tag management endpoints"""

    def create(
        self,
        name: str,
        description: Optional[str] = None,
        config_overrides: Optional[List[Dict[str, Any]]] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
        route_subscriptions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a new tag.

        Token scope required: ``tags:create``.

        Args:
            name: Tag name in ``key:value`` format (max 20 chars for key, 50 for value).
            description: Optional description (max 255 chars).
            config_overrides: Optional config overrides.
            before: Optional tag name to insert before (lower priority).
            after: Optional tag name to insert after (higher priority).
            route_subscriptions: Optional list of route IDs to subscribe to.

        Returns:
            Created tag data as a dictionary.
        """
        body: Dict[str, Any] = {"name": name}
        if description is not None:
            body["description"] = description
        if config_overrides is not None:
            body["configOverrides"] = config_overrides
        if before is not None:
            body["before"] = before
        if after is not None:
            body["after"] = after
        if route_subscriptions is not None:
            body["routeSubscriptions"] = route_subscriptions

        response: Dict[str, Any] = self.client.post("/v1/tags", json=body)
        return response.get("data", {})

    def list(
        self,
        include_counts: bool = False,
        cursor: Optional[str] = None,
        page_size: int = 25,
    ) -> Dict[str, Any]:
        """Get a paginated list of tags.

        Token scope required: ``tags:list``.

        Returns:
            Raw API response containing tag list and pagination metadata.
        """
        params = self._build_params(
            includeCounts=include_counts,
            cursor=cursor,
            pageSize=page_size,
        )
        response: Dict[str, Any] = self.client.get("/v2/tags", params=params)
        return response

    def get(self, tag: str) -> Dict[str, Any]:
        """Get a specific tag.

        Token scope required: ``tags:read``.

        Args:
            tag: Tag name in format 'key:value'.

        Returns:
            Tag data as a dictionary (or empty dict if not provided).
        """
        response: Dict[str, Any] = self.client.get(f"/v1/tags/{tag}")
        return response.get("data", {})

    def update(
        self,
        tag: str,
        description: Optional[str] = None,
        config_overrides: Optional[List[Dict[str, Any]]] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
        route_subscriptions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Edit a tag.

        Token scope required: ``tags:update``.

        Args:
            tag: Tag name in format 'key:value'.
            description: Optional description (max 255 chars).
            config_overrides: Optional config overrides.
            before: Optional tag to move before (lower priority).
            after: Optional tag to move after (higher priority).
            route_subscriptions: Optional list of route IDs to subscribe to.

        Returns:
            Updated tag data as a dictionary.
        """
        body: Dict[str, Any] = {}
        if description is not None:
            body["description"] = description
        if config_overrides is not None:
            body["configOverrides"] = config_overrides
        if before is not None:
            body["before"] = before
        if after is not None:
            body["after"] = after
        if route_subscriptions is not None:
            body["routeSubscriptions"] = route_subscriptions

        response: Dict[str, Any] = self.client.put(f"/v1/tags/{tag}", json=body)
        return response.get("data", {})

    def delete(self, tag: str) -> Dict[str, Any]:
        """Delete a tag.

        Token scope required: ``tags:delete``.

        Args:
            tag: Tag name in format 'key:value'.

        Returns:
            API response data.
        """
        response: Dict[str, Any] = self.client.delete(f"/v1/tags/{tag}")
        return response.get("data", {})


class Networks(BaseResource):
    """Network management endpoints"""

    def create(self, name: str, cidr: str) -> Dict[str, Any]:
        """Create a new network.

        Token scope required: ``networks:create``.

        Args:
            name: Network name.
            cidr: Network CIDR in format like '100.100.0.0/24'.

        Returns:
            Created network data as a dictionary.
        """
        body: Dict[str, Any] = {"name": name, "cidr": cidr}
        response: Dict[str, Any] = self.client.post("/v1/networks", json=body)
        return response.get("data", {})

    def list(
        self,
        include_counts: bool = False,
        cursor: Optional[str] = None,
        page_size: int = 25,
    ) -> Dict[str, Any]:
        """Get a paginated list of networks.

        Token scope required: ``networks:list``.

        Returns:
            Raw API response containing networks and pagination metadata.
        """
        params = self._build_params(
            includeCounts=include_counts,
            cursor=cursor,
            pageSize=page_size,
        )
        response: Dict[str, Any] = self.client.get("/v1/networks", params=params)
        return response

    def get(self, network_id: str) -> Dict[str, Any]:
        """Get a specific network by ID.

        Token scope required: ``networks:read``.

        Args:
            network_id: The network identifier.

        Returns:
            Network data as a dictionary (or empty dict if not provided).
        """
        response: Dict[str, Any] = self.client.get(f"/v1/networks/{network_id}")
        return response.get("data", {})

    def update(
        self, network_id: str, name: Optional[str] = None, cidr: Optional[str] = None
    ) -> Dict[str, Any]:
        """Edit a network.

        Token scope required: ``networks:update``.

        Args:
            network_id: Network ID.
            name: Optional new network name.
            cidr: Optional new network CIDR.

        Returns:
            Updated network data as a dictionary.
        """
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if cidr is not None:
            body["cidr"] = cidr

        response: Dict[str, Any] = self.client.put(f"/v1/networks/{network_id}", json=body)
        return response.get("data", {})


class AuditLogs(BaseResource):
    """Audit log endpoints"""

    def list(
        self,
        include_counts: bool = False,
        cursor: Optional[str] = None,
        page_size: int = 25,
        filter_target_id: Optional[str] = None,
        filter_target_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get a paginated list of audit logs.

        Token scope required: ``audit-logs:list``.

        Args:
            filter_target_type: One of: apiKey, host, network, role, user, ca, oidcProvider.

        Returns:
            Raw API response containing audit log entries and pagination metadata.
        """
        params = self._build_params(
            includeCounts=include_counts,
            cursor=cursor,
            pageSize=page_size,
            **{
                "filter.targetID": filter_target_id,
                "filter.targetType": filter_target_type,
            }
        )
        response: Dict[str, Any] = self.client.get("/v1/audit-logs", params=params)
        return response


class Downloads(BaseResource):
    """Software downloads endpoint"""

    def list(self) -> Dict[str, Any]:
        """Get a list of software download links and info.

        This endpoint is unauthenticated.

        Returns:
            Download links and metadata as a dictionary.
        """
        response: Dict[str, Any] = self.client.get("/v1/downloads")
        return response
