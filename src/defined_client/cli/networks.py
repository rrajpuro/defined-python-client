"""Network commands."""

from __future__ import annotations

from typing import Any

import click

from defined_client.services import NetworkService

from .core import JSON_OBJECT, CLIState, emit, list_options, paginate, require_changes


@click.group()
def networks() -> None:
    """Create, inspect, and manage networks."""


@networks.command("create")
@click.option("--name", required=True)
@click.option("--cidr", required=True)
@click.option("--description")
@click.option("--lighthouses-as-relays/--no-lighthouses-as-relays", default=None)
@click.pass_obj
def create_network(
    state: CLIState,
    name: str,
    cidr: str,
    description: str | None,
    lighthouses_as_relays: bool | None,
) -> None:
    """Create a network."""
    emit(
        state,
        state.get_client().networks.create(
            name=name,
            cidr=cidr,
            description=description,
            lighthouses_as_relays=lighthouses_as_relays,
        ),
    )


@networks.command("list")
@list_options
@click.pass_obj
def list_networks(
    state: CLIState,
    page_size: int,
    starting_token: str | None,
    no_paginate: bool,
    include_counts: bool,
) -> None:
    """List networks, automatically following pagination cursors."""
    emit(
        state,
        paginate(
            state.get_client().networks.list,
            page_size=page_size,
            starting_token=starting_token,
            no_paginate=no_paginate,
            include_counts=include_counts,
        ),
    )


@networks.command("get")
@click.option("--network-id", required=True)
@click.pass_obj
def get_network(state: CLIState, network_id: str) -> None:
    """Get a network by identifier."""
    emit(state, state.get_client().networks.get(network_id))


@networks.command("update")
@click.option("--network-id", required=True)
@click.option("--name")
@click.option("--description")
@click.option("--lighthouses-as-relays/--no-lighthouses-as-relays", default=None)
@click.pass_obj
def update_network(
    state: CLIState,
    network_id: str,
    name: str | None,
    description: str | None,
    lighthouses_as_relays: bool | None,
) -> None:
    """Safely update fields while preserving omitted network values."""
    require_changes(
        name=name,
        description=description,
        lighthouses_as_relays=lighthouses_as_relays,
    )
    emit(
        state,
        NetworkService(state.get_client()).safe_update(
            network_id,
            name=name,
            description=description,
            lighthouses_as_relays=lighthouses_as_relays,
        ),
    )


@networks.command("replace")
@click.option("--network-id", required=True)
@click.option("--document", required=True, type=JSON_OBJECT, metavar="JSON|file://PATH")
@click.pass_obj
def replace_network(state: CLIState, network_id: str, document: dict[str, Any]) -> None:
    """Replace network fields with an API-shaped JSON document."""
    emit(state, state.get_client().put(f"/v1/networks/{network_id}", json=document))
