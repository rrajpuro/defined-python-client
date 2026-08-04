"""CLI workflow tests using an in-memory client fake."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner

from defined_client import DefinedClientError
from defined_client.cli import core
from defined_client.cli import main

from .fakes import Call, FakeClientFactory


def test_global_configuration_reaches_one_closed_client(
    runner: CliRunner,
    fake_client: FakeClientFactory,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEFINED_API_KEY", "dnkey-test")
    monkeypatch.setenv("DEFINED_BASE_URL", "https://ignored.example")
    payload = {"data": {"id": "host-one"}, "metadata": {}}
    fake_client.respond("hosts", "get", payload)

    result = runner.invoke(
        main,
        [
            "--base-url",
            "https://api.example.test",
            "--timeout",
            "12.5",
            "hosts",
            "get",
            "--host-id",
            "host-one",
        ],
    )

    assert result.exit_code == 0, result.output
    assert fake_client.constructor_calls == [
        {
            "api_key": "dnkey-test",
            "base_url": "https://api.example.test",
            "timeout": 12.5,
        }
    ]
    assert len(fake_client.instances) == 1
    assert fake_client.instances[0].closed is True


def test_downloads_are_unauthenticated(
    runner: CliRunner,
    fake_client: FakeClientFactory,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEFINED_API_KEY", "dnkey-ignored-for-public-downloads")
    payload = {"data": [{"platform": "linux"}], "metadata": {}}
    fake_client.respond("downloads", "list", payload)

    result = runner.invoke(main, ["downloads", "list"])

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == payload
    assert fake_client.constructor_calls[0]["api_key"] is None
    assert fake_client.instances[0].closed is True


def test_invalid_base_url_is_rejected_before_client_creation(
    runner: CliRunner, fake_client: FakeClientFactory
) -> None:
    result = runner.invoke(
        main, ["--base-url", "api.example.test", "downloads", "list"]
    )

    assert result.exit_code == 2
    assert result.stdout == ""
    assert "absolute http:// or https:// URL" in result.stderr
    assert fake_client.instances == []


def test_json_output_is_the_exact_api_envelope(
    runner: CliRunner,
    fake_client: FakeClientFactory,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEFINED_API_KEY", "dnkey-test")
    payload = {
        "data": {"id": "host-one", "name": "edge"},
        "metadata": {"requestID": "request-one"},
    }
    fake_client.respond("hosts", "get", payload)

    result = runner.invoke(main, ["hosts", "get", "--host-id", "host-one"])

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == payload
    assert "ok" not in json.loads(result.stdout)
    assert "result" not in json.loads(result.stdout)
    assert result.stderr == ""


def test_table_output_handles_nested_values(
    runner: CliRunner,
    fake_client: FakeClientFactory,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEFINED_API_KEY", "dnkey-test")
    fake_client.respond(
        "hosts",
        "get",
        {
            "data": {
                "id": "host-one",
                "name": "edge",
                "tags": ["env:prod"],
            },
            "metadata": {},
        },
    )

    result = runner.invoke(
        main,
        ["--output", "table", "hosts", "get", "--host-id", "host-one"],
    )

    assert result.exit_code == 0, result.output
    assert "key" in result.stdout
    assert "value" in result.stdout
    assert "host-one" in result.stdout
    assert '["env:prod"]' in result.stdout
    assert "{" not in result.stdout


def test_api_error_is_redacted_and_emitted_only_on_stderr(
    runner: CliRunner,
    fake_client: FakeClientFactory,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    api_key = "dnkey-super-secret"
    monkeypatch.setenv("DEFINED_API_KEY", api_key)
    fake_client.respond(
        "hosts", "get", DefinedClientError(f"request rejected for {api_key}")
    )

    result = runner.invoke(main, ["hosts", "get", "--host-id", "host-one"])

    assert result.exit_code == 1
    assert result.stdout == ""
    assert "[REDACTED]" in result.stderr
    assert api_key not in result.stderr
    assert "Traceback" not in result.stderr
    assert fake_client.instances[0].closed is True


def test_auto_pagination_combines_pages(
    runner: CliRunner,
    fake_client: FakeClientFactory,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEFINED_API_KEY", "dnkey-test")

    def pages(**kwargs: Any) -> dict[str, Any]:
        if kwargs["cursor"] is None:
            return {
                "data": [{"id": "host-one"}],
                "metadata": {
                    "hasNextPage": True,
                    "hasPrevPage": False,
                    "nextCursor": "cursor-two",
                    "totalCount": 2,
                    "page": {"count": 1},
                },
            }
        assert kwargs["cursor"] == "cursor-two"
        return {
            "data": [{"id": "host-two"}],
            "metadata": {
                "hasNextPage": False,
                "hasPrevPage": True,
                "prevCursor": "cursor-one",
                "totalCount": 2,
                "page": {"count": 1},
            },
        }

    fake_client.respond("hosts", "list", pages)

    result = runner.invoke(main, ["hosts", "list", "--page-size", "1"])

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == {
        "data": [{"id": "host-one"}, {"id": "host-two"}],
        "metadata": {
            "hasNextPage": False,
            "hasPrevPage": False,
            "totalCount": 2,
            "page": {"count": 2},
        },
    }
    calls = [call for call in fake_client.calls if call.method == "list"]
    assert [call.kwargs["cursor"] for call in calls] == [None, "cursor-two"]
    assert all(call.kwargs["page_size"] == 1 for call in calls)


def test_no_paginate_returns_one_page_unchanged(
    runner: CliRunner,
    fake_client: FakeClientFactory,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEFINED_API_KEY", "dnkey-test")
    page = {
        "data": [{"id": "host-two"}],
        "metadata": {"hasNextPage": True, "nextCursor": "cursor-three"},
    }
    fake_client.respond("hosts", "list", page)

    result = runner.invoke(
        main,
        [
            "hosts",
            "list",
            "--starting-token",
            "cursor-two",
            "--no-paginate",
        ],
    )

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == page
    call = next(call for call in fake_client.calls if call.method == "list")
    assert call.kwargs["cursor"] == "cursor-two"
    assert call.kwargs["page_size"] == 100


def test_auto_pagination_from_token_marks_combined_result_complete(
    runner: CliRunner,
    fake_client: FakeClientFactory,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEFINED_API_KEY", "dnkey-test")
    page = {
        "data": [{"id": "host-two"}],
        "metadata": {
            "hasNextPage": False,
            "hasPrevPage": True,
            "prevCursor": "cursor-one",
        },
    }
    fake_client.respond("hosts", "list", page)

    result = runner.invoke(
        main,
        ["hosts", "list", "--starting-token", "cursor-two"],
    )

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == {
        "data": [{"id": "host-two"}],
        "metadata": {"hasNextPage": False, "hasPrevPage": False},
    }


def test_later_pagination_failure_never_emits_partial_output(
    runner: CliRunner,
    fake_client: FakeClientFactory,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEFINED_API_KEY", "dnkey-test")
    responses: list[Any] = [
        {
            "data": [{"id": "host-one"}],
            "metadata": {"hasNextPage": True, "nextCursor": "cursor-two"},
        },
        DefinedClientError("second page failed"),
    ]
    fake_client.respond("hosts", "list", responses)

    result = runner.invoke(main, ["hosts", "list"])

    assert result.exit_code == 1
    assert result.stdout == ""
    assert "second page failed" in result.stderr


def test_repeated_pagination_cursor_fails_without_partial_output(
    runner: CliRunner,
    fake_client: FakeClientFactory,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEFINED_API_KEY", "dnkey-test")
    fake_client.respond(
        "hosts",
        "list",
        [
            {
                "data": [{"id": "host-one"}],
                "metadata": {"hasNextPage": True, "nextCursor": "repeat"},
            },
            {
                "data": [{"id": "host-two"}],
                "metadata": {"hasNextPage": True, "nextCursor": "repeat"},
            },
        ],
    )

    result = runner.invoke(main, ["hosts", "list"])

    assert result.exit_code == 1
    assert result.stdout == ""
    assert "repeated next cursor" in result.stderr


def test_inline_json_is_decoded_before_resource_dispatch(
    runner: CliRunner,
    fake_client: FakeClientFactory,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEFINED_API_KEY", "dnkey-test")
    fake_client.respond("roles", "create", {"data": {"id": "role-one"}})
    rules = [
        {
            "protocol": "TCP",
            "allowedRoleID": "role-client",
            "portRange": {"from": 443, "to": 443},
        }
    ]

    result = runner.invoke(
        main,
        [
            "roles",
            "create",
            "--name",
            "web",
            "--firewall-rules",
            json.dumps(rules),
        ],
    )

    assert result.exit_code == 0, result.output
    call = next(call for call in fake_client.calls if call.scope == "roles")
    assert call.method == "create"
    assert call.kwargs["firewall_rules"] == rules


@pytest.mark.parametrize(
    "args, scope, method, expected_kwargs",
    [
        (
            [
                "routes",
                "create",
                "--name",
                "office",
                "--router-host-id",
                "host-router",
            ],
            "routes",
            "create",
            {
                "name": "office",
                "description": None,
                "router_host_id": "host-router",
                "routable_cidrs": None,
                "firewall_rules": None,
            },
        ),
        (
            [
                "tags",
                "create",
                "--name",
                "env:prod",
                "--route-subscription",
                "route-one",
            ],
            "tags",
            "create",
            {
                "name": "env:prod",
                "description": None,
                "config_overrides": None,
                "before": None,
                "after": None,
                "route_subscriptions": ["route-one"],
            },
        ),
        (
            [
                "networks",
                "create",
                "--name",
                "production",
                "--cidr",
                "100.64.0.0/24",
                "--no-lighthouses-as-relays",
            ],
            "networks",
            "create",
            {
                "name": "production",
                "cidr": "100.64.0.0/24",
                "description": None,
                "lighthouses_as_relays": False,
            },
        ),
        (
            [
                "audit-logs",
                "list",
                "--no-paginate",
                "--filter-target-id",
                "host-one",
                "--filter-target-type",
                "host",
            ],
            "audit_logs",
            "list",
            {
                "cursor": None,
                "page_size": 100,
                "include_counts": False,
                "filter_target_id": "host-one",
                "filter_target_type": "host",
            },
        ),
    ],
)
def test_representative_resource_commands_dispatch_named_options(
    runner: CliRunner,
    fake_client: FakeClientFactory,
    monkeypatch: pytest.MonkeyPatch,
    args: list[str],
    scope: str,
    method: str,
    expected_kwargs: dict[str, Any],
) -> None:
    monkeypatch.setenv("DEFINED_API_KEY", "dnkey-test")

    result = runner.invoke(main, args)

    assert result.exit_code == 0, result.output
    call = next(call for call in fake_client.calls if call.scope == scope)
    assert call.method == method
    assert call.args == ()
    assert call.kwargs == expected_kwargs


def test_file_json_replace_is_raw_and_performs_no_get(
    runner: CliRunner,
    fake_client: FakeClientFactory,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("DEFINED_API_KEY", "dnkey-test")
    document = {"name": "edge", "tags": [], "listenPort": 0}
    document_path = tmp_path / "host replacement.json"
    document_path.write_text(json.dumps(document), encoding="utf-8")
    response = {"data": {"id": "host-one", **document}, "metadata": {}}
    fake_client.respond("client", "put", response)

    result = runner.invoke(
        main,
        [
            "hosts",
            "replace",
            "--host-id",
            "host-one",
            "--document",
            f"file://{document_path}",
        ],
    )

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == response
    assert fake_client.calls == [
        Call("client", "put", ("/v2/hosts/host-one",), {"json": document})
    ]


@pytest.mark.parametrize(
    "document",
    ["not-json", "[]", '{"listenPort": NaN}'],
)
def test_invalid_replace_document_is_a_usage_error_without_a_client(
    runner: CliRunner,
    fake_client: FakeClientFactory,
    monkeypatch: pytest.MonkeyPatch,
    document: str,
) -> None:
    monkeypatch.setenv("DEFINED_API_KEY", "dnkey-test")

    result = runner.invoke(
        main,
        [
            "hosts",
            "replace",
            "--host-id",
            "host-one",
            "--document",
            document,
        ],
    )

    assert result.exit_code == 2
    assert result.stdout == ""
    assert "JSON" in result.stderr
    assert "Traceback" not in result.stderr
    assert fake_client.instances == []


def test_safe_update_preserves_omitted_values_and_accepts_empty_values(
    runner: CliRunner,
    fake_client: FakeClientFactory,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEFINED_API_KEY", "dnkey-test")
    current = {
        "name": "edge",
        "roleID": "role-one",
        "staticAddresses": ["203.0.113.10:4242"],
        "listenPort": 4242,
        "tags": ["env:prod"],
        "configOverrides": [{"key": "value"}],
    }
    fake_client.respond("hosts", "get", {"data": current, "metadata": {}})
    fake_client.respond("hosts", "update", {"data": {**current, "tags": []}})

    result = runner.invoke(
        main,
        [
            "hosts",
            "update",
            "--host-id",
            "host-one",
            "--listen-port",
            "0",
            "--clear-tags",
        ],
    )

    assert result.exit_code == 0, result.output
    update_call = next(
        call
        for call in fake_client.calls
        if call.scope == "hosts" and call.method == "update"
    )
    assert update_call.args == ("host-one",)
    assert update_call.kwargs == {
        "name": "edge",
        "role_id": "role-one",
        "static_addresses": ["203.0.113.10:4242"],
        "listen_port": 0,
        "tags": [],
        "config_overrides": [{"key": "value"}],
    }
    assert len(fake_client.instances) == 1


@pytest.mark.parametrize(
    "args, expected_message",
    [
        (["hosts", "update", "--host-id", "host-one"], "at least one"),
        (
            [
                "hosts",
                "update",
                "--host-id",
                "host-one",
                "--tag",
                "env:prod",
                "--clear-tags",
            ],
            "cannot be used",
        ),
    ],
)
def test_invalid_update_is_rejected_before_client_creation(
    runner: CliRunner,
    fake_client: FakeClientFactory,
    monkeypatch: pytest.MonkeyPatch,
    args: list[str],
    expected_message: str,
) -> None:
    monkeypatch.setenv("DEFINED_API_KEY", "dnkey-test")

    result = runner.invoke(main, args)

    assert result.exit_code == 2
    assert result.stdout == ""
    assert expected_message in result.stderr
    assert fake_client.instances == []


def test_stream_logs_validates_args_and_extends_request_timeout(
    runner: CliRunner,
    fake_client: FakeClientFactory,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEFINED_API_KEY", "dnkey-test")
    fake_client.respond("client", "post", {"data": {"accepted": True}})
    command_args = {"durationSeconds": 60, "level": "info"}

    result = runner.invoke(
        main,
        [
            "hosts",
            "debug-command",
            "--host-id",
            "host-one",
            "--command",
            "StreamLogs",
            "--command-args",
            json.dumps(command_args),
        ],
    )

    assert result.exit_code == 0, result.output
    assert fake_client.calls == [
        Call(
            "client",
            "post",
            ("/v1/hosts/host-one/command",),
            {
                "json": {"command": "StreamLogs", "args": command_args},
                "timeout": 90.0,
            },
        )
    ]


def test_malformed_stream_logs_args_are_rejected_locally(
    runner: CliRunner,
    fake_client: FakeClientFactory,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEFINED_API_KEY", "dnkey-test")

    result = runner.invoke(
        main,
        [
            "hosts",
            "debug-command",
            "--host-id",
            "host-one",
            "--command",
            "StreamLogs",
            "--command-args",
            '{"durationSeconds":60}',
        ],
    )

    assert result.exit_code == 2
    assert result.stdout == ""
    assert "level" in result.stderr
    assert fake_client.instances == []


def test_idempotent_tag_subscription_gets_complete_envelope(
    runner: CliRunner,
    fake_client: FakeClientFactory,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEFINED_API_KEY", "dnkey-test")
    current = {
        "name": "env:prod",
        "routeSubscriptions": ["route-one"],
    }
    fake_client.respond("tags", "get", {"data": current})

    result = runner.invoke(
        main,
        [
            "tags",
            "subscribe-route",
            "--tag",
            "env:prod",
            "--route-id",
            "route-one",
        ],
    )

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == {"data": current, "metadata": {}}


def test_resource_metadata_is_not_mistaken_for_response_metadata() -> None:
    resource = {
        "id": "host-one",
        "metadata": {"platform": "dnclient"},
    }

    assert core.ensure_envelope(resource) == {
        "data": resource,
        "metadata": {},
    }
