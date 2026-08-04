"""Role commands."""

from __future__ import annotations

from typing import Any

import click

from defined_client.services import RoleService

from .core import CLIState, JSON_ARRAY, JSON_OBJECT, emit, list_options, paginate, require_changes


@click.group()
def roles() -> None:
    """Create, inspect, and manage roles."""


@roles.command("create")
@click.option("--name", required=True)
@click.option("--description")
@click.option("--firewall-rules", type=JSON_ARRAY, metavar="JSON|file://PATH")
@click.pass_obj
def create_role(
    state: CLIState,
    name: str,
    description: str | None,
    firewall_rules: list[dict[str, Any]] | None,
) -> None:
    """Create a role."""
    emit(
        state,
        state.get_client().roles.create(
            name=name, description=description, firewall_rules=firewall_rules
        ),
    )


@roles.command("list")
@list_options
@click.pass_obj
def list_roles(
    state: CLIState,
    page_size: int,
    starting_token: str | None,
    no_paginate: bool,
    include_counts: bool,
) -> None:
    """List roles, automatically following pagination cursors."""
    emit(
        state,
        paginate(
            state.get_client().roles.list,
            page_size=page_size,
            starting_token=starting_token,
            no_paginate=no_paginate,
            include_counts=include_counts,
        ),
    )


@roles.command("get")
@click.option("--role-id", required=True)
@click.pass_obj
def get_role(state: CLIState, role_id: str) -> None:
    """Get a role by identifier."""
    emit(state, state.get_client().roles.get(role_id))


@roles.command("update")
@click.option("--role-id", required=True)
@click.option("--description")
@click.option("--firewall-rules", type=JSON_ARRAY, metavar="JSON|file://PATH")
@click.pass_obj
def update_role(
    state: CLIState,
    role_id: str,
    description: str | None,
    firewall_rules: list[dict[str, Any]] | None,
) -> None:
    """Safely update fields while preserving omitted role values."""
    require_changes(description=description, firewall_rules=firewall_rules)
    emit(
        state,
        RoleService(state.get_client()).safe_update(
            role_id, description=description, firewall_rules=firewall_rules
        ),
    )


@roles.command("replace")
@click.option("--role-id", required=True)
@click.option("--document", required=True, type=JSON_OBJECT, metavar="JSON|file://PATH")
@click.pass_obj
def replace_role(state: CLIState, role_id: str, document: dict[str, Any]) -> None:
    """Replace role fields with an API-shaped JSON document."""
    emit(state, state.get_client().put(f"/v1/roles/{role_id}", json=document))


@roles.command("delete")
@click.option("--role-id", required=True)
@click.pass_obj
def delete_role(state: CLIState, role_id: str) -> None:
    """Delete a role without prompting."""
    emit(state, state.get_client().roles.delete(role_id))
