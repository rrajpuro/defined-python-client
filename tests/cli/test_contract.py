"""Public command-tree and local-validation tests for ``definedcli``."""

from __future__ import annotations

import re

import pytest
from click.testing import CliRunner

from defined_client.cli import main


EXPECTED_COMMANDS = {
    "hosts": {
        "create",
        "create-with-enrollment",
        "list",
        "get",
        "get-by-name",
        "find-by-name",
        "update",
        "replace",
        "delete",
        "block",
        "unblock",
        "debug-command",
        "create-enrollment-code",
        "update-tags",
        "add-tag",
        "remove-tag",
    },
    "roles": {"create", "list", "get", "update", "replace", "delete"},
    "routes": {
        "create",
        "list",
        "get",
        "get-by-name",
        "find-by-name",
        "update",
        "replace",
        "delete",
        "update-router-host",
    },
    "tags": {
        "create",
        "list",
        "get",
        "find-by-key",
        "update",
        "replace",
        "delete",
        "subscribe-route",
        "unsubscribe-route",
    },
    "networks": {"create", "list", "get", "update", "replace"},
    "audit-logs": {"list"},
    "downloads": {"list"},
}


def test_complete_command_inventory() -> None:
    assert set(main.commands) == set(EXPECTED_COMMANDS)
    for group_name, command_names in EXPECTED_COMMANDS.items():
        assert set(main.commands[group_name].commands) == command_names


HELP_INVOCATIONS = (
    [["--help"]]
    + [[group_name, "--help"] for group_name in EXPECTED_COMMANDS]
    + [
        [group_name, command_name, "--help"]
        for group_name, command_names in EXPECTED_COMMANDS.items()
        for command_name in sorted(command_names)
    ]
)


@pytest.mark.parametrize("args", HELP_INVOCATIONS)
def test_help_does_not_require_credentials(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, args: list[str]
) -> None:
    monkeypatch.delenv("DEFINED_API_KEY", raising=False)
    result = runner.invoke(main, args)
    assert result.exit_code == 0, result.output
    assert "Usage:" in result.output


def test_version_does_not_require_credentials(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("DEFINED_API_KEY", raising=False)
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0, result.output
    assert re.search(r"\b\d+\.\d+\.\d+\b", result.output)


def test_authenticated_command_requires_environment_key(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("DEFINED_API_KEY", raising=False)
    result = runner.invoke(main, ["hosts", "list"])
    assert result.exit_code == 2
    assert result.stdout == ""
    assert "DEFINED_API_KEY" in result.stderr
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("page_size", ["0", "501", "not-a-number"])
def test_invalid_page_size_is_a_usage_error(
    runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
    page_size: str,
) -> None:
    monkeypatch.setenv("DEFINED_API_KEY", "test-key")
    result = runner.invoke(main, ["hosts", "list", "--page-size", page_size])
    assert result.exit_code == 2
    assert result.stdout == ""
    assert "page-size" in result.stderr.lower()
    assert "Traceback" not in result.stderr
