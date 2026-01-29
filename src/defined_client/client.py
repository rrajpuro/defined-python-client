"""Main API Client for Defined Networking"""

import requests
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin

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

    def request(
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
        url = urljoin(self.base_url, endpoint)

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                timeout=timeout,
            )

            # Handle errors based on status code
            if response.status_code == 400:
                error_data = response.json()
                errors = error_data.get("errors", [])
                raise ValidationError(
                    "Validation error",
                    status_code=400,
                    errors=errors,
                )
            elif response.status_code == 401:
                raise AuthenticationError(
                    "Authentication failed. Check your API key.",
                    status_code=401,
                )
            elif response.status_code == 404:
                raise NotFoundError(
                    "Resource not found",
                    status_code=404,
                )
            elif 500 <= response.status_code < 600:
                raise ServerError(
                    f"Server error: {response.status_code}",
                    status_code=response.status_code,
                )
            elif not response.ok:
                raise DefinedClientError(
                    f"API request failed with status {response.status_code}",
                    status_code=response.status_code,
                )

            # Return response data
            try:
                return response.json()
            except ValueError:
                # Handle responses with no JSON content
                return {}

        except requests.exceptions.Timeout:
            raise DefinedClientError("Request timeout")
        except requests.exceptions.ConnectionError:
            raise DefinedClientError("Connection error")
        except requests.exceptions.RequestException as e:
            raise DefinedClientError(f"Request failed: {str(e)}")

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """Make a GET request"""
        return self.request("GET", endpoint, params=params, timeout=timeout)

    def post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """Make a POST request"""
        return self.request("POST", endpoint, params=params, json=json, timeout=timeout)

    def put(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """Make a PUT request"""
        return self.request("PUT", endpoint, params=params, json=json, timeout=timeout)

    def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """Make a DELETE request"""
        return self.request("DELETE", endpoint, params=params, timeout=timeout)

    def close(self):
        """Close the session"""
        self.session.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
