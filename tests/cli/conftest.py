"""Shared fixtures for CLI tests."""

import pytest
from click.testing import CliRunner

from defined_client.cli import core

from .fakes import FakeClientFactory


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def fake_client(monkeypatch: pytest.MonkeyPatch) -> FakeClientFactory:
    monkeypatch.delenv("DEFINED_API_KEY", raising=False)
    monkeypatch.delenv("DEFINED_BASE_URL", raising=False)
    factory = FakeClientFactory()
    monkeypatch.setattr(core, "DefinedClient", factory.client_class())
    return factory
