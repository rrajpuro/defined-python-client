"""Custom exceptions for the Defined Networking API.

This module provides a small hierarchy of exceptions raised by the
client when API calls fail. Applications can catch :class:`DefinedClientError`
to handle any client-related error or catch specific subclasses such as
:class:`ValidationError`.
"""

from typing import Any, Dict, List, Optional


class DefinedClientError(Exception):
    """Base exception for all Defined Networking API errors.

    Args:
        message: Human-readable message describing the error.
        status_code: Optional HTTP status code associated with the error.
        errors: Optional structured error details returned by the API.
        response: Optional raw HTTP response object.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        response: Any = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.errors = errors or []
        self.response = response
        super().__init__(message)

    def __str__(self) -> str:
        if self.errors:
            details = "; ".join(e.get("message", str(e)) for e in self.errors if e)
            return f"{self.message} ({details})"
        return self.message

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(status_code={self.status_code}, message={self.message!r})"
        )


# -------------------------
# Client / Request errors
# -------------------------

class ValidationError(DefinedClientError):
    """Request validation failed (HTTP 400)."""


class AuthenticationError(DefinedClientError):
    """Authentication failed or token is invalid (HTTP 401)."""


class PermissionDeniedError(DefinedClientError):
    """Authenticated but not authorized (HTTP 403)."""


class NotFoundError(DefinedClientError):
    """Requested resource was not found (HTTP 404)."""


# -------------------------
# Server errors
# -------------------------

class ServerError(DefinedClientError):
    """Server-side error (HTTP 5xx)."""
