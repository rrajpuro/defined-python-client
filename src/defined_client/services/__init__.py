"""High-level service layer for the Defined Networking API.

These services compose the low-level client methods into convenient
operations that handle common patterns like name-based lookups,
safe updates (GET-merge-PUT), and auto-pagination.
"""

from .hosts import HostService
from .networks import NetworkService
from .roles import RoleService
from .routes import RouteService
from .tags import TagService
from .pagination import list_all

__all__ = [
    "HostService",
    "NetworkService",
    "RoleService",
    "RouteService",
    "TagService",
    "list_all",
]
