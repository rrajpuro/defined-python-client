"""Main API Client for Defined Networking"""

import requests
from typing import Optional, Dict, Any

from .exceptions import (
    DefinedClientError,
    ValidationError,
    AuthenticationError,
    NotFoundError,
    PermissionDeniedError,
    ServerError,
)
from .resources import (
    Hosts,
    Roles,
    Routes,
    Tags,
    Networks,
    AuditLogs,
    Downloads,
)


class DefinedClient:
    """Main client for interacting with Defined Networking API.

    This client provides access to all Defined Networking API endpoints through
    intuitive resource interfaces. Each resource (hosts, roles, networks, etc.)
    has its own set of methods for create, read, update, delete, and list operations.

    The client handles authentication, error handling, and request/response
    serialization automatically.

    Attributes:
        hosts: Host, lighthouse, and relay management
        roles: Role and firewall rule management
        routes: Route management
        tags: Tag and config override management
        networks: Network management
        audit_logs: Audit log retrieval
        downloads: Software download links (unauthenticated)

    Example:
        >>> client = DefinedClient(api_key="dnkey-...")
        >>>
        >>> # List all hosts
        >>> response = client.hosts.list()
        >>> hosts = response["data"]
        >>>
        >>> # Create a new host
        >>> host = client.hosts.create(
        ...     name="my-host",
        ...     network_id="network-...",
        ...     role_id="role-..."
        ... )
        >>>
        >>> # Use as context manager (automatically closes session)
        >>> with DefinedClient(api_key="dnkey-...") as client:
        ...     networks = client.networks.list()

    For full API documentation, see: https://docs.defined.net/
    """

    BASE_URL = "https://api.defined.net"

    hosts: "Hosts"
    roles: "Roles"
    routes: "Routes"
    tags: "Tags"
    networks: "Networks"
    audit_logs: "AuditLogs"
    downloads: "Downloads"

    def __init__(self, api_key: str, base_url: Optional[str] = None) -> None:
        """
        Initialize the Defined Networking API client

        Args:
            api_key: API key from https://admin.defined.net/settings/api-keys
            base_url: Optional custom base URL (default: https://api.defined.net)
        """
        self.api_key: str = api_key
        self.base_url: str = base_url or self.BASE_URL
        self.session: requests.Session = requests.Session()

        # Import version here to avoid circular imports
        from . import __version__

        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": f"defined-client-python/{__version__}",
            }
        )

        # Initialize resource endpoints
        self.hosts = Hosts(self)
        self.roles = Roles(self)
        self.routes = Routes(self)
        self.tags = Tags(self)
        self.networks = Networks(self)
        self.audit_logs = AuditLogs(self)
        self.downloads = Downloads(self)


    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint path (e.g., "/v1/hosts")
            params: Query parameters
            json: JSON request body
            timeout: Request timeout in seconds

        Returns:
            Response data

        Raises:
            ValidationError: If validation fails (400)
            AuthenticationError: If authentication fails (401)
            NotFoundError: If resource not found (404)
            ServerError: If server returns 5xx error
            DefinedClientError: For other API errors
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        # Convert json=None to {} for POST/PUT/PATCH to ensure valid JSON body
        # is sent with Content-Type: application/json header
        if method in ("POST", "PUT", "PATCH") and json is None:
            json = {}

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                timeout=timeout,
            )
        except requests.exceptions.RequestException as exc:
            raise DefinedClientError("Network error") from exc

        return self._handle_response(response)


    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle the API response and raise errors if needed.

        Parses JSON responses and maps HTTP status codes to specific
        exception types defined in :mod:`defined_client.exceptions`.

        Args:
            response: The HTTP response object from ``requests``.

        Returns:
            Parsed JSON payload as a dictionary for successful responses.

        Raises:
            DefinedClientError or a subclass when the API indicates an error.
        """

        # Treat successful responses with no content as an empty dict
        if response.ok:
            # Some endpoints may legitimately return no content (204)
            if response.status_code == 204 or not response.content:
                return {}
            try:
                return response.json()
            except ValueError:
                raise DefinedClientError(
                    "Invalid JSON response",
                    status_code=response.status_code,
                    response=response,
                )

        # Parse error payload safely
        try:
            payload = response.json()
        except ValueError:
            payload = {}

        errors = payload.get("errors")

        status = response.status_code

        if status == 400:
            raise ValidationError(
                "Validation error",
                status_code=status,
                errors=errors,
                response=response,
            )
        if status == 401:
            raise AuthenticationError(
                "Authentication failed",
                status_code=status,
                response=response,
            )
        if status == 403:
            raise PermissionDeniedError(
                "Permission denied",
                status_code=status,
                response=response,
            )
        if status == 404:
            raise NotFoundError(
                "Resource not found",
                status_code=status,
                response=response,
            )
        if 500 <= status < 600:
            raise ServerError(
                "Server error",
                status_code=status,
                response=response,
            )

        raise DefinedClientError(
            f"Unexpected API error ({status})",
            status_code=status,
            response=response,
        )


    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """Make a GET request.

        Args:
            endpoint: API endpoint path (e.g., "/v1/hosts").
            params: Optional query parameters.
            timeout: Request timeout in seconds.

        Returns:
            Parsed response as a dictionary.
        """
        return self._request("GET", endpoint, params=params, timeout=timeout)

    def post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """Make a POST request.

        Args:
            endpoint: API endpoint path.
            json: Optional JSON body to send.
            params: Optional query parameters.
            timeout: Request timeout in seconds.

        Returns:
            Parsed response as a dictionary.
        """
        return self._request("POST", endpoint, params=params, json=json, timeout=timeout)

    def put(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """Make a PUT request.

        Args:
            endpoint: API endpoint path.
            json: Optional JSON body to send.
            params: Optional query parameters.
            timeout: Request timeout in seconds.

        Returns:
            Parsed response as a dictionary.
        """
        return self._request("PUT", endpoint, params=params, json=json, timeout=timeout)

    def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """Make a DELETE request.

        Args:
            endpoint: API endpoint path.
            params: Optional query parameters.
            timeout: Request timeout in seconds.

        Returns:
            Parsed response as a dictionary.
        """
        return self._request("DELETE", endpoint, params=params, timeout=timeout)

    def close(self) -> None:
        """Close the underlying HTTP session.

        This releases network resources held by the :class:`requests.Session`.
        """
        self.session.close()

    def __enter__(self) -> "DefinedClient":
        """Enter context manager and return client instance.

        Returns:
            The client instance (self).
        """
        return self

    def __exit__(
        self, exc_type: Optional[type], exc_val: Optional[BaseException], exc_tb: Optional[Any]
    ) -> None:
        """Exit context manager and close the session.

        Any exception raised inside the context is propagated after
        closing the session.
        """
        self.close()
