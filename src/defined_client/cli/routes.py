"""Route commands."""

from __future__ import annotations

from typing import Any

import click

from defined_client.services import RouteService

from .core import (
    JSON_ARRAY,
    JSON_OBJECT,
    CLIState,
    emit,
    list_options,
    paginate,
    require_changes,
)


@click.group()
def routes() -> None:
    """Create, inspect, and manage routes."""


def _write_route(
    state: CLIState,
    *,
    name: str,
    description: str | None,
    router_host_id: str | None,
    routable_cidrs: dict[str, Any] | None,
    firewall_rules: list[dict[str, Any]] | None,
) -> None:
    emit(
        state,
        state.get_client().routes.create(
            name=name,
            description=description,
            router_host_id=router_host_id,
            routable_cidrs=routable_cidrs,
            firewall_rules=firewall_rules,
        ),
    )


@routes.command("create")
@click.option("--name", required=True)
@click.option("--description")
@click.option("--router-host-id")
@click.option("--routable-cidrs", type=JSON_OBJECT, metavar="JSON|file://PATH")
@click.option("--firewall-rules", type=JSON_ARRAY, metavar="JSON|file://PATH")
@click.pass_obj
def create_route(
    state: CLIState,
    name: str,
    description: str | None,
    router_host_id: str | None,
    routable_cidrs: dict[str, Any] | None,
    firewall_rules: list[dict[str, Any]] | None,
) -> None:
    """Create a route."""
    _write_route(
        state,
        name=name,
        description=description,
        router_host_id=router_host_id,
        routable_cidrs=routable_cidrs,
        firewall_rules=firewall_rules,
    )


@routes.command("list")
@list_options
@click.pass_obj
def list_routes(
    state: CLIState,
    page_size: int,
    starting_token: str | None,
    no_paginate: bool,
    include_counts: bool,
) -> None:
    """List routes, automatically following pagination cursors."""
    emit(
        state,
        paginate(
            state.get_client().routes.list,
            page_size=page_size,
            starting_token=starting_token,
            no_paginate=no_paginate,
            include_counts=include_counts,
        ),
    )


@routes.command("get")
@click.option("--route-id", required=True)
@click.pass_obj
def get_route(state: CLIState, route_id: str) -> None:
    """Get a route by identifier."""
    emit(state, state.get_client().routes.get(route_id))


@routes.command("get-by-name")
@click.option("--name", required=True)
@click.pass_obj
def get_route_by_name(state: CLIState, name: str) -> None:
    """Get a route by exact name, failing when it does not exist."""
    emit(
        state,
        RouteService(state.get_client()).get_by_name(name),
        helper=True,
    )


@routes.command("find-by-name")
@click.option("--name", required=True)
@click.pass_obj
def find_route_by_name(state: CLIState, name: str) -> None:
    """Find a route by exact name, returning null when it does not exist."""
    emit(
        state,
        RouteService(state.get_client()).find_by_name(name),
        helper=True,
    )


@routes.command("update")
@click.option("--route-id", required=True)
@click.option("--name")
@click.option("--description")
@click.option("--router-host-id")
@click.option("--routable-cidrs", type=JSON_OBJECT, metavar="JSON|file://PATH")
@click.option("--firewall-rules", type=JSON_ARRAY, metavar="JSON|file://PATH")
@click.pass_obj
def update_route(
    state: CLIState,
    route_id: str,
    name: str | None,
    description: str | None,
    router_host_id: str | None,
    routable_cidrs: dict[str, Any] | None,
    firewall_rules: list[dict[str, Any]] | None,
) -> None:
    """Safely update fields while preserving omitted route values."""
    require_changes(
        name=name,
        description=description,
        router_host_id=router_host_id,
        routable_cidrs=routable_cidrs,
        firewall_rules=firewall_rules,
    )
    emit(
        state,
        RouteService(state.get_client()).safe_update(
            route_id,
            name=name,
            description=description,
            router_host_id=router_host_id,
            routable_cidrs=routable_cidrs,
            firewall_rules=firewall_rules,
        ),
    )


@routes.command("replace")
@click.option("--route-id", required=True)
@click.option("--document", required=True, type=JSON_OBJECT, metavar="JSON|file://PATH")
@click.pass_obj
def replace_route(state: CLIState, route_id: str, document: dict[str, Any]) -> None:
    """Replace route fields with an API-shaped JSON document."""
    emit(state, state.get_client().put(f"/v1/routes/{route_id}", json=document))


@routes.command("delete")
@click.option("--route-id", required=True)
@click.pass_obj
def delete_route(state: CLIState, route_id: str) -> None:
    """Delete a route without prompting."""
    emit(state, state.get_client().routes.delete(route_id))


@routes.command("update-router-host")
@click.option("--route-id", required=True)
@click.option("--host-id", required=True)
@click.pass_obj
def update_router_host(state: CLIState, route_id: str, host_id: str) -> None:
    """Change a route's router host while preserving every other field."""
    emit(
        state,
        RouteService(state.get_client()).update_router_host(route_id, host_id),
        helper=True,
    )
