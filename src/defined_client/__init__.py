"""Defined Networking API Client

This package provides a Python client for the Defined Networking API,
allowing you to programmatically manage hosts, roles, routes, tags,
networks, and audit logs in your Managed Nebula networks.

Quick Start:
    >>> from defined_client import DefinedClient
    >>> client = DefinedClient(api_key="your-api-key")
    >>> hosts = client.hosts.list()

For more information, visit: https://github.com/rrajpuro/defined-python-client
"""

from importlib.metadata import PackageNotFoundError, version

from .client import DefinedClient
from .exceptions import (
    AuthenticationError,
    DefinedClientError,
    NotFoundError,
    PermissionDeniedError,
    ServerError,
    ValidationError,
)
from .services import (
    HostService,
    NetworkService,
    RoleService,
    RouteService,
    TagService,
    list_all,
)

try:
    __version__ = version("defined-client")
except PackageNotFoundError:
    __version__: str = "0.0.0"

__all__ = [
    "AuthenticationError",
    "DefinedClient",
    "DefinedClientError",
    "HostService",
    "NetworkService",
    "NotFoundError",
    "PermissionDeniedError",
    "RoleService",
    "RouteService",
    "ServerError",
    "TagService",
    "ValidationError",
    "list_all",
]
