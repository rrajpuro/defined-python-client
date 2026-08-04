"""Root command for ``definedcli``."""

from __future__ import annotations

import os

import click

from defined_client import __version__

from .core import (
    CLIState,
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT,
    ErrorHandlingGroup,
    validate_base_url,
)


@click.group(cls=ErrorHandlingGroup)
@click.option(
    "--base-url",
    envvar="DEFINED_BASE_URL",
    default=DEFAULT_BASE_URL,
    show_default=True,
    callback=validate_base_url,
    help="Defined API base URL.",
)
@click.option(
    "--timeout",
    type=click.FloatRange(min=0, min_open=True),
    default=DEFAULT_TIMEOUT,
    show_default=True,
    help="Default request timeout in seconds.",
)
@click.option(
    "--output",
    type=click.Choice(["json", "table"], case_sensitive=False),
    default="json",
    show_default=True,
    help="Output format.",
)
@click.version_option(version=__version__, prog_name="definedcli")
@click.pass_context
def main(ctx: click.Context, base_url: str, timeout: float, output: str) -> None:
    """Manage Defined Networking resources from the command line."""
    ctx.obj = CLIState(
        ctx,
        api_key=os.environ.get("DEFINED_API_KEY"),
        base_url=base_url,
        timeout=timeout,
        output=output.lower(),
    )


# Imported after ``main`` is defined so resource modules can register cleanly.
from .hosts import hosts  # noqa: E402
from .misc import audit_logs, downloads  # noqa: E402
from .networks import networks  # noqa: E402
from .roles import roles  # noqa: E402
from .routes import routes  # noqa: E402
from .tags import tags  # noqa: E402

main.add_command(hosts)
main.add_command(roles)
main.add_command(routes)
main.add_command(tags)
main.add_command(networks)
main.add_command(audit_logs)
main.add_command(downloads)
