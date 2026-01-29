"""Resource classes for API endpoints"""

from typing import Optional, Dict, Any, List


class BaseResource:
    """Base resource class with common functionality"""

    def __init__(self, client):
        self.client = client

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
        """
        Create a new host, lighthouse, or relay

        Token scope required: hosts:create
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

        response = self.client.post("/v1/hosts", json=body)
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
        """
        Get a paginated list of hosts

        Token scope required: hosts:list
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
        response = self.client.get("/v1/hosts", params=params)
        return response

    def get(self, host_id: str) -> Dict[str, Any]:
        """
        Get a specific host

        Token scope required: hosts:read
        """
        response = self.client.get(f"/v1/hosts/{host_id}")
        return response.get("data", {})

    def delete(self, host_id: str) -> Dict[str, Any]:
        """
        Delete a host

        Token scope required: hosts:delete
        """
        response = self.client.delete(f"/v1/hosts/{host_id}")
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
        """
        Edit a host

        Token scope required: hosts:update
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

        response = self.client.put(f"/v2/hosts/{host_id}", json=body)
        return response.get("data", {})

    def block(self, host_id: str) -> Dict[str, Any]:
        """
        Block a host

        Token scope required: hosts:block
        """
        response = self.client.post(f"/v1/hosts/{host_id}/block")
        return response.get("data", {})

    def unblock(self, host_id: str) -> Dict[str, Any]:
        """
        Unblock a host

        Token scope required: hosts:unblock
        """
        response = self.client.post(f"/v1/hosts/{host_id}/unblock")
        return response.get("data", {})

    def debug_command(
        self, host_id: str, command_type: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Send debug commands to a host

        Token scope required: hosts:debug

        command_type can be: StreamLogs, CreateTunnel, PrintTunnel, PrintCert, QueryLighthouse, DebugStack
        """
        body: Dict[str, Any] = {"command": command_type}

        if kwargs:
            body["args"] = kwargs

        response = self.client.post(f"/v1/hosts/{host_id}/command", json=body)
        return response.get("data", {})

    def create_enrollment_code(self, host_id: str) -> Dict[str, Any]:
        """
        Create an enrollment code for a host

        Token scope required: hosts:enroll
        """
        response = self.client.post(f"/v1/hosts/{host_id}/enrollment-code")
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
        """
        Create a host and enrollment code in one request

        Token scopes required: hosts:create, hosts:enroll
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

        response = self.client.post("/v1/host-and-enrollment-code", json=body)
        return response.get("data", {})


class Roles(BaseResource):
    """Role management endpoints"""

    def create(self, name: str) -> Dict[str, Any]:
        """
        Create a new role

        Token scope required: roles:create
        """
        body: Dict[str, Any] = {"name": name}
        response = self.client.post("/v1/roles", json=body)
        return response.get("data", {})

    def list(
        self,
        include_counts: bool = False,
        cursor: Optional[str] = None,
        page_size: int = 25,
    ) -> Dict[str, Any]:
        """
        Get a paginated list of roles

        Token scope required: roles:list
        """
        params = self._build_params(
            includeCounts=include_counts,
            cursor=cursor,
            pageSize=page_size,
        )
        response = self.client.get("/v1/roles", params=params)
        return response

    def get(self, role_id: str) -> Dict[str, Any]:
        """
        Get a specific role

        Token scope required: roles:read
        """
        response = self.client.get(f"/v1/roles/{role_id}")
        return response.get("data", {})

    def update(
        self, role_id: str, name: Optional[str] = None, description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Edit a role

        Token scope required: roles:update
        """
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description

        response = self.client.put(f"/v1/roles/{role_id}", json=body)
        return response.get("data", {})

    def delete(self, role_id: str) -> Dict[str, Any]:
        """
        Delete a role

        Token scope required: roles:delete
        """
        response = self.client.delete(f"/v1/roles/{role_id}")
        return response.get("data", {})


class Routes(BaseResource):
    """Route management endpoints"""

    def create(self, name: str) -> Dict[str, Any]:
        """
        Create a new route

        Token scope required: routes:create
        """
        body: Dict[str, Any] = {"name": name}
        response = self.client.post("/v1/routes", json=body)
        return response.get("data", {})

    def list(
        self,
        include_counts: bool = False,
        cursor: Optional[str] = None,
        page_size: int = 25,
    ) -> Dict[str, Any]:
        """
        Get a paginated list of routes

        Token scope required: routes:list
        """
        params = self._build_params(
            includeCounts=include_counts,
            cursor=cursor,
            pageSize=page_size,
        )
        response = self.client.get("/v1/routes", params=params)
        return response

    def get(self, route_id: str) -> Dict[str, Any]:
        """
        Get a specific route

        Token scope required: routes:read
        """
        response = self.client.get(f"/v1/routes/{route_id}")
        return response.get("data", {})

    def update(
        self, route_id: str, name: Optional[str] = None, description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Edit a route

        Token scope required: routes:update
        """
        body: Dict[str, Any] = {"name": name} if name else {}
        if description is not None:
            body["description"] = description

        response = self.client.put(f"/v1/routes/{route_id}", json=body)
        return response.get("data", {})

    def delete(self, route_id: str) -> Dict[str, Any]:
        """
        Delete a route

        Token scope required: routes:delete
        """
        response = self.client.delete(f"/v1/routes/{route_id}")
        return response.get("data", {})


class Tags(BaseResource):
    """Tag management endpoints"""

    def create(
        self,
        name: str,
        description: Optional[str] = None,
        config_overrides: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new tag

        Token scope required: tags:create
        """
        body: Dict[str, Any] = {"name": name}
        if description:
            body["description"] = description
        if config_overrides:
            body["configOverrides"] = config_overrides

        response = self.client.post("/v1/tags", json=body)
        return response.get("data", {})

    def list(
        self,
        include_counts: bool = False,
        cursor: Optional[str] = None,
        page_size: int = 25,
    ) -> Dict[str, Any]:
        """
        Get a paginated list of tags

        Token scope required: tags:list
        """
        params = self._build_params(
            includeCounts=include_counts,
            cursor=cursor,
            pageSize=page_size,
        )
        response = self.client.get("/v2/tags", params=params)
        return response

    def get(self, tag: str) -> Dict[str, Any]:
        """
        Get a specific tag

        Token scope required: tags:read

        Args:
            tag: Tag name in format 'key:value'
        """
        response = self.client.get(f"/v1/tags/{tag}")
        return response.get("data", {})

    def update(
        self,
        tag: str,
        description: Optional[str] = None,
        config_overrides: Optional[List[Dict[str, Any]]] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Edit a tag

        Token scope required: tags:update

        Args:
            tag: Tag name in format 'key:value'
            description: Tag description
            config_overrides: Config overrides for the tag
            before: Tag name to insert this tag before (for priority ordering)
            after: Tag name to insert this tag after (for priority ordering)
        """
        body: Dict[str, Any] = {}
        if description is not None:
            body["description"] = description
        if config_overrides is not None:
            body["configOverrides"] = config_overrides
        if before:
            body["before"] = before
        if after:
            body["after"] = after

        response = self.client.put(f"/v1/tags/{tag}", json=body)
        return response.get("data", {})

    def delete(self, tag: str) -> Dict[str, Any]:
        """
        Delete a tag

        Token scope required: tags:delete

        Args:
            tag: Tag name in format 'key:value'
        """
        response = self.client.delete(f"/v1/tags/{tag}")
        return response.get("data", {})


class Networks(BaseResource):
    """Network management endpoints"""

    def create(self, name: str, cidr: str) -> Dict[str, Any]:
        """
        Create a new network

        Token scope required: networks:create

        Args:
            name: Network name
            cidr: Network CIDR in format like '100.100.0.0/24'
        """
        body: Dict[str, Any] = {"name": name, "cidr": cidr}
        response = self.client.post("/v1/networks", json=body)
        return response.get("data", {})

    def list(
        self,
        include_counts: bool = False,
        cursor: Optional[str] = None,
        page_size: int = 25,
    ) -> Dict[str, Any]:
        """
        Get a paginated list of networks

        Token scope required: networks:list
        """
        params = self._build_params(
            includeCounts=include_counts,
            cursor=cursor,
            pageSize=page_size,
        )
        response = self.client.get("/v1/networks", params=params)
        return response

    def get(self, network_id: str) -> Dict[str, Any]:
        """
        Get a specific network

        Token scope required: networks:read
        """
        response = self.client.get(f"/v1/networks/{network_id}")
        return response.get("data", {})

    def update(
        self, network_id: str, name: Optional[str] = None, cidr: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Edit a network

        Token scope required: networks:update

        Args:
            network_id: Network ID
            name: Network name
            cidr: Network CIDR
        """
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if cidr is not None:
            body["cidr"] = cidr

        response = self.client.put(f"/v1/networks/{network_id}", json=body)
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
        """
        Get a paginated list of audit logs

        Token scope required: audit-logs:list

        Args:
            filter_target_type: One of: apiKey, host, network, role, user, ca, oidcProvider
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
        response = self.client.get("/v1/audit-logs", params=params)
        return response


class Downloads(BaseResource):
    """Software downloads endpoint"""

    def list(self) -> Dict[str, Any]:
        """
        Get a list of software download links and info

        This endpoint is unauthenticated.
        """
        response = self.client.get("/v1/downloads")
        return response.get("data", {})
