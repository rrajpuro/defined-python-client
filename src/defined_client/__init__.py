"""Defined Networking API Client"""

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
