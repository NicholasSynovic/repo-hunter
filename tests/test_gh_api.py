"""Tests for GitHub GraphQL API wrapper."""

from __future__ import annotations

import logging

import pytest

from rh.gh.api import GitHubGraphQLAPI


class _FakeResponse:
    """Minimal fake response object for API tests."""

    def __init__(self, status_code: int, json_data: dict | None = None, text: str = ""):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text

    def raise_for_status(self) -> None:
        """Raise an exception when status is non-2xx."""
        if self.status_code >= 400:
            raise RuntimeError(f"status {self.status_code}")

    def json(self) -> dict:
        """Return configured JSON payload."""
        if self._json_data is None:
            raise ValueError("invalid json")
        return self._json_data


class _FakeSession:
    """Minimal fake session object for API tests."""

    def __init__(self, response: _FakeResponse):
        self._response = response
        self.last_url: str | None = None
        self.last_json: dict[str, object] | None = None
        self.last_timeout: int | None = None

    def post(self, url: str, json: dict[str, object], timeout: int) -> _FakeResponse:
        """Capture request payload and return configured response."""
        self.last_url = url
        self.last_json = json
        self.last_timeout = timeout
        return self._response


def _api() -> GitHubGraphQLAPI:
    """Create API client instance for tests."""
    return GitHubGraphQLAPI(token="ghp_test", logger=logging.getLogger("test"))


def test_build_query_uses_non_none_filters() -> None:
    """Query builder should include enabled filter qualifiers."""
    api = _api()
    api._months_ago_iso = lambda months: "2024-01-01T00:00:00Z"  # type: ignore[method-assign]

    payload = api.build_query(
        star_count=10,
        fork_count=5,
        watcher_count=2,
        issue_count=1,
        age_months=12,
        pr_count=3,
        first=50,
    )

    variables = payload["variables"]
    assert isinstance(variables, dict)
    query_string = variables["queryString"]
    assert isinstance(query_string, str)
    assert "stars:>=10" in query_string
    assert "forks:>=5" in query_string
    assert "watchers:>=2" in query_string
    assert "good-first-issues:>=1" in query_string
    assert "good-first-issues:>=3" in query_string
    assert "created:>=2024-01-01T00:00:00Z" in query_string
    assert variables["first"] == 50


def test_build_query_omits_none_filters() -> None:
    """Query builder should omit disabled filter qualifiers."""
    api = _api()

    payload = api.build_query(
        star_count=None,
        fork_count=None,
        watcher_count=None,
        issue_count=None,
        age_months=None,
        pr_count=None,
    )

    variables = payload["variables"]
    assert isinstance(variables, dict)
    query_string = variables["queryString"]
    assert isinstance(query_string, str)
    assert "stars:>=" not in query_string
    assert "forks:>=" not in query_string
    assert "watchers:>=" not in query_string
    assert "created:>=" not in query_string


def test_execute_query_raises_on_http_error() -> None:
    """HTTP failures should raise runtime errors."""
    api = _api()
    api.session = _FakeSession(
        _FakeResponse(status_code=500, json_data={"message": "boom"}, text="boom")
    )

    with pytest.raises(RuntimeError, match="HTTP request failed"):
        api.execute_query(payload={"query": "query { viewer { login } }"})


def test_execute_query_raises_on_graphql_errors() -> None:
    """GraphQL errors field should raise runtime errors."""
    api = _api()
    api.session = _FakeSession(
        _FakeResponse(status_code=200, json_data={"errors": [{"message": "bad"}]})
    )

    with pytest.raises(RuntimeError, match="returned errors"):
        api.execute_query(payload={"query": "query { viewer { login } }"})


def test_execute_query_returns_data_on_success() -> None:
    """Successful GraphQL response should be returned as parsed JSON."""
    api = _api()
    response_payload = {"data": {"search": {"repositoryCount": 1, "nodes": []}}}
    fake_session = _FakeSession(
        _FakeResponse(status_code=200, json_data=response_payload)
    )
    api.session = fake_session

    payload = {"query": "query { viewer { login } }", "variables": {"first": 1}}
    result = api.execute_query(payload=payload)

    assert result == response_payload
    assert fake_session.last_json == payload
