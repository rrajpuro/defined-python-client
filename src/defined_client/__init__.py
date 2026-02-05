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

from importlib.metadata import version, PackageNotFoundError

from .client import DefinedClient
from .exceptions import (
    DefinedClientError,
    ValidationError,
    NotFoundError,
    AuthenticationError,
    PermissionDeniedError,
    ServerError,
)

try:
    __version__ = version("defined-client")
except PackageNotFoundError:
    __version__: str = "0.0.0"

__all__ = [
    "DefinedClient",
    "DefinedClientError",
    "ValidationError",
    "NotFoundError",
    "AuthenticationError",
    "PermissionDeniedError",
    "ServerError",
]
