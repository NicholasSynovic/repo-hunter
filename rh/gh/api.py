"""GitHub GraphQL API wrapper for repository search."""

from __future__ import annotations

from datetime import UTC, datetime
from logging import Logger

from requests import Response, Session
from requests.adapters import HTTPAdapter, Retry

from rh.gh import GITHUB_GRAPHQL_URL, HTTP_POST_TIMEOUT


class GitHubGraphQLAPI:
    """Client for executing repository search queries over GitHub GraphQL.

    Parameters
    ----------
    token : str
        GitHub personal access token used for API authorization.
    logger : Logger
        Logger instance used for request diagnostics.
    endpoint : str, default=GITHUB_GRAPHQL_URL
        GraphQL endpoint URL.
    timeout : int, default=HTTP_POST_TIMEOUT
        Request timeout in seconds.
    """

    def __init__(
        self,
        token: str,
        logger: Logger,
        endpoint: str = GITHUB_GRAPHQL_URL,
        timeout: int = HTTP_POST_TIMEOUT,
    ) -> None:
        """Initialize session, headers, and retry behavior."""
        self.logger: Logger = logger
        self.endpoint: str = endpoint
        self.timeout: int = timeout

        self.headers: dict[str, str] = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        self.adapter: HTTPAdapter = HTTPAdapter(
            max_retries=Retry(
                total=5,
                backoff_factor=1,
                status_forcelist=[403, 429, 500, 502, 503, 504],
                allowed_methods=["POST"],
            ),
        )

        self.session: Session = Session()
        self.session.mount("https://", self.adapter)
        self.session.mount("http://", self.adapter)
        self.session.headers.update(self.headers)

    @staticmethod
    def _months_ago_iso(months: int) -> str:
        """Approximate a timestamp N months ago in UTC ISO-8601 format.

        Parameters
        ----------
        months : int
            Number of months to subtract from the current UTC timestamp.

        Returns
        -------
        str
            ISO-8601 UTC timestamp formatted as ``YYYY-MM-DDTHH:MM:SSZ``.
        """
        # Keep implementation dependency-free by approximating one month as 30 days.
        days: int = months * 30
        timestamp = datetime.now(tz=UTC).timestamp() - (days * 24 * 60 * 60)
        return datetime.fromtimestamp(timestamp, tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    def build_query(
        self,
        *,
        star_count: int | None,
        fork_count: int | None,
        watcher_count: int | None,
        issue_count: int | None,
        age_months: int | None,
        pr_count: int | None,
        first: int = 25,
    ) -> dict[str, object]:
        """Build GraphQL query and variables from optional repository filters.

        Parameters
        ----------
        star_count : int | None
            Minimum stargazer threshold.
        fork_count : int | None
            Minimum fork threshold.
        watcher_count : int | None
            Minimum watcher threshold.
        issue_count : int | None
            Minimum issue threshold.
        age_months : int | None
            Maximum repository age in months.
        pr_count : int | None
            Minimum pull request threshold.
        first : int, default=25
            Number of repositories to fetch.

        Returns
        -------
        dict[str, object]
            GraphQL payload containing ``query`` and ``variables`` keys.
        """
        qualifiers: list[str] = ["is:public", "archived:false"]

        if star_count is not None:
            qualifiers.append(f"stars:>={star_count}")
        if fork_count is not None:
            qualifiers.append(f"forks:>={fork_count}")
        if watcher_count is not None:
            qualifiers.append(f"watchers:>={watcher_count}")
        if issue_count is not None:
            qualifiers.append(f"good-first-issues:>={issue_count}")
        if pr_count is not None:
            qualifiers.append(f"good-first-issues:>={pr_count}")
        if age_months is not None:
            created_after: str = self._months_ago_iso(months=age_months)
            qualifiers.append(f"created:>={created_after}")

        search_query: str = " ".join(qualifiers)

        query: str = """
query SearchRepositories($queryString: String!, $first: Int!) {
  search(query: $queryString, type: REPOSITORY, first: $first) {
    repositoryCount
    nodes {
      ... on Repository {
        nameWithOwner
        stargazerCount
        forkCount
        watchers {
          totalCount
        }
        issues(states: OPEN) {
          totalCount
        }
        pullRequests(states: OPEN) {
          totalCount
        }
        createdAt
        url
      }
    }
  }
}
""".strip()

        return {
            "query": query,
            "variables": {
                "queryString": search_query,
                "first": first,
            },
        }

    def execute_query(self, payload: dict[str, object]) -> dict:
        """Execute a GraphQL request and raise on HTTP or GraphQL errors.

        Parameters
        ----------
        payload : dict[str, object]
            GraphQL request body containing ``query`` and optional variables.

        Returns
        -------
        dict
            Parsed JSON response body.

        Raises
        ------
        RuntimeError
            If HTTP request fails or GraphQL ``errors`` are returned.
        """
        self.logger.info("Sending GraphQL request to %s", self.endpoint)
        response: Response = self.session.post(
            url=self.endpoint,
            json=payload,
            timeout=self.timeout,
        )
        self.logger.debug("GraphQL response status code: %d", response.status_code)

        try:
            response.raise_for_status()
        except Exception as exc:
            body: str = response.text[:1000]
            self.logger.error(
                "HTTP error from GitHub GraphQL API: %s | body=%s",
                exc,
                body,
            )
            raise RuntimeError("GitHub GraphQL HTTP request failed") from exc

        try:
            data: dict = response.json()
        except ValueError as exc:
            self.logger.error("GitHub GraphQL response was not valid JSON")
            raise RuntimeError("GitHub GraphQL response JSON parsing failed") from exc

        if data.get("errors"):
            self.logger.error("GraphQL errors returned: %s", data["errors"])
            raise RuntimeError("GitHub GraphQL returned errors")

        return data
