"""Audit-log and download commands."""

from __future__ import annotations

import click

from .core import CLIState, emit, list_options, paginate


@click.group("audit-logs")
def audit_logs() -> None:
    """Inspect organization audit logs."""


@audit_logs.command("list")
@list_options
@click.option("--filter-target-id")
@click.option(
    "--filter-target-type",
    type=click.Choice(
        ["apiKey", "host", "network", "role", "user", "ca", "oidcProvider"]
    ),
)
@click.pass_obj
def list_audit_logs(
    state: CLIState,
    page_size: int,
    starting_token: str | None,
    no_paginate: bool,
    include_counts: bool,
    filter_target_id: str | None,
    filter_target_type: str | None,
) -> None:
    """List logs, automatically following pagination cursors."""
    emit(
        state,
        paginate(
            state.get_client().audit_logs.list,
            page_size=page_size,
            starting_token=starting_token,
            no_paginate=no_paginate,
            include_counts=include_counts,
            filter_target_id=filter_target_id,
            filter_target_type=filter_target_type,
        ),
    )


@click.group()
def downloads() -> None:
    """Inspect public software downloads."""


@downloads.command("list")
@click.pass_obj
def list_downloads(state: CLIState) -> None:
    """List software downloads without requiring an API key."""
    emit(state, state.get_client(require_auth=False).downloads.list())
