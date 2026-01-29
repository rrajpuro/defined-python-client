"""Main API Client for Defined Networking"""

import requests
from typing import Optional, Dict, Any

from .exceptions import (
    DefinedClientError,
    ValidationError,
    AuthenticationError,
    NotFoundError,
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
    """Main client for interacting with Defined Networking API"""

    BASE_URL = "https://api.defined.net"

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        Initialize the Defined Networking API client

        Args:
            api_key: API key from https://admin.defined.net/settings/api-keys
            base_url: Optional custom base URL (default: https://api.defined.net)
        """
        self.api_key = api_key
        self.base_url = base_url or self.BASE_URL
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
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
        """Handle the API response and raise errors if needed"""

        if response.ok:
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
        """Make a GET request"""
        return self._request("GET", endpoint, params=params, timeout=timeout)

    def post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """Make a POST request"""
        return self._request("POST", endpoint, params=params, json=json, timeout=timeout)

    def put(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """Make a PUT request"""
        return self._request("PUT", endpoint, params=params, json=json, timeout=timeout)

    def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """Make a DELETE request"""
        return self._request("DELETE", endpoint, params=params, timeout=timeout)

    def close(self):
        """Close the session"""
        self.session.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
