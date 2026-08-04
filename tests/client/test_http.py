"""HTTP session, authentication, and timeout tests."""

from unittest.mock import Mock, patch

from defined_client import DefinedClient


def test_client_omits_authorization_header_without_api_key() -> None:
    with patch("defined_client.client.requests.Session") as session_factory:
        DefinedClient(api_key=None)

    headers = session_factory.return_value.headers.update.call_args.args[0]
    assert "Authorization" not in headers


def test_client_omits_authorization_header_for_empty_api_key() -> None:
    with patch("defined_client.client.requests.Session") as session_factory:
        DefinedClient(api_key="")

    headers = session_factory.return_value.headers.update.call_args.args[0]
    assert "Authorization" not in headers


def test_client_adds_bearer_authorization_header_with_api_key() -> None:
    with patch("defined_client.client.requests.Session") as session_factory:
        DefinedClient(api_key="dnkey-test")

    headers = session_factory.return_value.headers.update.call_args.args[0]
    assert headers["Authorization"] == "Bearer dnkey-test"


def test_client_uses_default_timeout_and_allows_request_override() -> None:
    with patch("defined_client.client.requests.Session") as session_factory:
        response = Mock(ok=True, status_code=200, content=b"{}")
        response.json.return_value = {}
        session_factory.return_value.request.return_value = response
        client = DefinedClient(
            api_key=None,
            base_url="https://example.test/",
            timeout=12.5,
        )

        client.get("/default-timeout")
        assert session_factory.return_value.request.call_args.kwargs["timeout"] == 12.5

        client.get("/explicit-timeout", timeout=1.25)
        assert session_factory.return_value.request.call_args.kwargs["timeout"] == 1.25
