"""Tag commands."""

from __future__ import annotations

from typing import Any

import click

from defined_client.services import TagService

from .core import (
    JSON_ARRAY,
    JSON_OBJECT,
    CLIState,
    emit,
    list_options,
    paginate,
    repeated_or_clear,
    require_changes,
    validate_tag_position,
)


@click.group()
def tags() -> None:
    """Create, inspect, and manage tags."""


@tags.command("create")
@click.option("--name", required=True, help="Tag in key:value form.")
@click.option("--description")
@click.option("--config-overrides", type=JSON_ARRAY, metavar="JSON|file://PATH")
@click.option("--before", help="Insert before this tag.")
@click.option("--after", help="Insert after this tag.")
@click.option("--route-subscription", "route_subscriptions", multiple=True)
@click.pass_obj
def create_tag(
    state: CLIState,
    name: str,
    description: str | None,
    config_overrides: list[dict[str, Any]] | None,
    before: str | None,
    after: str | None,
    route_subscriptions: tuple[str, ...],
) -> None:
    """Create a tag."""
    validate_tag_position(before, after)
    emit(
        state,
        state.get_client().tags.create(
            name=name,
            description=description,
            config_overrides=config_overrides,
            before=before,
            after=after,
            route_subscriptions=list(route_subscriptions) or None,
        ),
    )


@tags.command("list")
@list_options
@click.pass_obj
def list_tags(
    state: CLIState,
    page_size: int,
    starting_token: str | None,
    no_paginate: bool,
    include_counts: bool,
) -> None:
    """List tags, automatically following pagination cursors."""
    emit(
        state,
        paginate(
            state.get_client().tags.list,
            page_size=page_size,
            starting_token=starting_token,
            no_paginate=no_paginate,
            include_counts=include_counts,
        ),
    )


@tags.command("get")
@click.option("--tag", required=True)
@click.pass_obj
def get_tag(state: CLIState, tag: str) -> None:
    """Get one tag."""
    emit(state, state.get_client().tags.get(tag))


@tags.command("find-by-key")
@click.option("--key", required=True)
@click.pass_obj
def find_tags_by_key(state: CLIState, key: str) -> None:
    """Find all tags with the given key prefix."""
    emit(state, TagService(state.get_client()).find_by_key(key), helper=True)


@tags.command("update")
@click.option("--tag", required=True)
@click.option("--description")
@click.option("--config-overrides", type=JSON_ARRAY, metavar="JSON|file://PATH")
@click.option("--before")
@click.option("--after")
@click.option("--route-subscription", "route_subscriptions", multiple=True)
@click.option("--clear-route-subscriptions", is_flag=True)
@click.pass_obj
def update_tag(
    state: CLIState,
    tag: str,
    description: str | None,
    config_overrides: list[dict[str, Any]] | None,
    before: str | None,
    after: str | None,
    route_subscriptions: tuple[str, ...],
    clear_route_subscriptions: bool,
) -> None:
    """Safely update fields while preserving omitted tag values."""
    validate_tag_position(before, after)
    subscription_values = repeated_or_clear(
        route_subscriptions,
        clear_route_subscriptions,
        option_name="route-subscription",
        clear_option_name="clear-route-subscriptions",
    )
    require_changes(
        description=description,
        config_overrides=config_overrides,
        before=before,
        after=after,
        route_subscriptions=subscription_values,
    )
    emit(
        state,
        TagService(state.get_client()).safe_update(
            tag,
            description=description,
            config_overrides=config_overrides,
            before=before,
            after=after,
            route_subscriptions=subscription_values,
        ),
    )


@tags.command("replace")
@click.option("--tag", required=True)
@click.option("--document", required=True, type=JSON_OBJECT, metavar="JSON|file://PATH")
@click.pass_obj
def replace_tag(state: CLIState, tag: str, document: dict[str, Any]) -> None:
    """Replace tag fields with an API-shaped JSON document."""
    emit(state, state.get_client().put(f"/v1/tags/{tag}", json=document))


@tags.command("delete")
@click.option("--tag", required=True)
@click.pass_obj
def delete_tag(state: CLIState, tag: str) -> None:
    """Delete a tag without prompting."""
    emit(state, state.get_client().tags.delete(tag))


@tags.command("subscribe-route")
@click.option("--tag", required=True)
@click.option("--route-id", required=True)
@click.pass_obj
def subscribe_route(state: CLIState, tag: str, route_id: str) -> None:
    """Subscribe a tag to a route idempotently."""
    emit(
        state,
        TagService(state.get_client()).subscribe_route(tag, route_id),
        helper=True,
    )


@tags.command("unsubscribe-route")
@click.option("--tag", required=True)
@click.option("--route-id", required=True)
@click.pass_obj
def unsubscribe_route(state: CLIState, tag: str, route_id: str) -> None:
    """Remove a route subscription from a tag."""
    emit(
        state,
        TagService(state.get_client()).unsubscribe_route(tag, route_id),
        helper=True,
    )
