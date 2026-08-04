"""Internal validation helpers shared by high-level services."""

from __future__ import annotations

from typing import Any

from ..exceptions import DefinedClientError


def resource_data(response: Any, resource: str) -> dict[str, Any]:
    """Return a resource payload or fail before a replacement update.

    Safe updates must never turn a malformed or incomplete GET envelope into an
    empty PUT body. Every managed resource returned by this API has a name, so
    it is used as the minimum signal that the payload is the requested object.
    """
    if not isinstance(response, dict):
        raise DefinedClientError(
            f"Cannot safely update {resource}: GET returned an invalid response"
        )

    data = response.get("data")
    if (
        not isinstance(data, dict)
        or not isinstance(data.get("name"), str)
        or not data["name"]
    ):
        raise DefinedClientError(
            f"Cannot safely update {resource}: GET response is missing resource data"
        )
    return data
