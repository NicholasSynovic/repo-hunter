import re
from re import Match

from loguru import logger
from requests import Response
from requests.adapters import HTTPAdapter, Retry
from requests.exceptions import RequestException
from requests.sessions import Session

from joss import HTTP_HEAD_TIMEOUT
from joss.interfaces import TransformInterface
from joss.models import JOSSGHIssue, JOSSPaperProjectIssue


class Transform(TransformInterface):
    def __init__(
        self,
        resolve_joss_url: bool = False,
    ) -> None:
        self.resolve_joss_url: bool = resolve_joss_url

    @staticmethod
    def _extract_repo_url(body: str) -> str:
        base_repo_match: Match[str] | None = re.search(
            pattern=r"<!--target-repository-->(.*?)<!--end-target-repository-->",
            string=body,
        )
        backup_repo_match: Match[str | None] = re.search(
            pattern=r"\*\*Repository:\*\*.*?(https?://[^\s\"<>]+)",
            string=body,
        )

        if base_repo_match is not None:
            logger.debug("Found repo url via base regex")
            return base_repo_match.group(1).strip()

        if backup_repo_match is not None:
            logger.debug("Found repo url via backup regex")
            return backup_repo_match.group(1).strip()

        logger.warning("No repo url found")
        return ""

    @staticmethod
    def _extract_joss_url(body: str) -> str:
        # JOSS URL from status badge: [![status](...)](URL)
        joss_url_match: Match[str] | None = re.search(
            pattern=r"\[!\[status\]\([^)]+\)\]\((https?://joss\.theoj\.org/papers/[^)]+)\)",
            string=body,
        )
        if joss_url_match is not None:
            logger.debug("Found paper status")
            return joss_url_match.group(1)

        logger.warning("No paper status found")
        return ""

    @staticmethod
    def _resolve_joss_url(url: str) -> str:
        session: Session = Session()

        # Define exponential backoff strategy
        # backoff_factor=1 means sleep for [0s, 2s, 4s, 8s, ...] between retries
        retry_strategy: Retry = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[403, 429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET"],
        )

        adapter: HTTPAdapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount(prefix="http://", adapter=adapter)
        session.mount(prefix="https://", adapter=adapter)

        try:
            logger.debug(f"Sending HEAD request to {url} ...")
            response: Response = session.head(
                url=url,
                timeout=HTTP_HEAD_TIMEOUT,
                allow_redirects=True,
            )
            logger.debug(f"Resolved {url} -> {response.url}")
            url = response.url
        except RequestException:
            logger.error(f"Failed to resolve {url}")

        return url

    def normalize_joss_paper_project_issues(
        self,
        issues: list[JOSSGHIssue],
    ) -> list[JOSSPaperProjectIssue]:
        paper_project_id: int = 0
        data: list[JOSSPaperProjectIssue] = []

        # Leverage a sieve to filter out issues
        logger.info("Normalizing issues...")

        filtered_issues: filter[JOSSGHIssue] = filter(
            lambda x: self._extract_repo_url(body=x.body), issues
        )
        logger.debug("Filtered on `.body` for source code project")

        issue: JOSSGHIssue
        for issue in filtered_issues:
            github_repo_url: str = self._extract_repo_url(body=issue.body)
            joss_url: str = self._extract_joss_url(body=issue.body)
            joss_resolved_url: str = ""

            if joss_url != "":  # Positive case, all checks pass
                if self.resolve_joss_url:
                    joss_resolved_url = self._resolve_joss_url(url=joss_url)
            else:
                logger.warning(
                    f"Skipped issue #{issue.id} because no JOSS URL is present"
                )
                continue

            datum: JOSSPaperProjectIssue = JOSSPaperProjectIssue(
                id=paper_project_id,
                github_issue_id=issue.id,
                joss_url=joss_url,
                joss_resolved_url=joss_resolved_url,
                github_repo_url=github_repo_url,
            )

            data.append(datum)
            paper_project_id += 1

        logger.info(f"Normalized {len(data)} issues")
        return data

    def transform(self, data: list[JOSSGHIssue]) -> list[JOSSPaperProjectIssue]:
        # Build paper-project mappings from the normalized issues
        paper_project_issues: list[JOSSPaperProjectIssue] = (
            self.normalize_joss_paper_project_issues(issues=data)
        )

        logger.info(
            f"Transformed {len(data)} issues into "
            f"{len(paper_project_issues)} paper project mappings"
        )
        return paper_project_issues
