"""Extract JOSS issue records from the GitHub API."""

from logging import Logger

from fastcore.foundation import AttrDict, L
from ghapi.all import GhApi
from progress.spinner import Spinner

from rh.interfaces import ExtractInterface
from rh.joss import GITHUB_REPO_OWNER, GITHUB_REPO_PROJECT, HTTP_POST_TIMEOUT
from rh.logger import JOSSLogger


class JOSSExtract(ExtractInterface):
    """Extractor for JOSS review issues hosted on GitHub.

    Parameters
    ----------
    joss_logger : JOSSLogger
        Application logger wrapper used to emit progress and diagnostics.
    """

    def __init__(self, joss_logger: JOSSLogger) -> None:
        """Initialize API client and extraction settings."""
        self._per_page: int = 100

        self.logger: Logger = joss_logger.get_logger()
        # Assumes setting the `GITHUB_TOKEN` environment variable
        self.gh: GhApi = GhApi(
            owner=GITHUB_REPO_OWNER,
            repo=GITHUB_REPO_PROJECT,
        )

    def __distill_fastcore(self, obj):
        """Recursively convert Fastcore containers into plain Python values.

        Parameters
        ----------
        obj : Any
            Value that may contain nested ``AttrDict`` or ``L`` containers.

        Returns
        -------
        Any
            Equivalent structure composed only of built-in ``dict`` and ``list``
            containers where possible.
        """
        # Handle AttrDict (or any dict-like object)
        if isinstance(obj, (dict, AttrDict)):
            return {k: self.__distill_fastcore(v) for k, v in obj.items()}

        # Handle L (or any list/tuple)
        elif isinstance(obj, (list, L, tuple)):
            return [self.__distill_fastcore(v) for v in obj]

        # Return everything else as-is
        return obj

    def _query_api(self, page: int = 1) -> list[AttrDict]:
        """Request one issues page from the JOSS GitHub repository.

        Parameters
        ----------
        page : int, default=1
            One-indexed issue page to request.

        Returns
        -------
        list[AttrDict]
            Distilled issue payloads for the requested page.
        """
        self.logger.info(
            "Logging page %d of %s/%s",
            page,
            GITHUB_REPO_OWNER,
            GITHUB_REPO_PROJECT,
        )
        issues: L = self.gh.issues.list_for_repo(
            page=page,
            per_page=self._per_page,
            state="all",
            sort="created",
            direction="asc",
        )

        return [self.__distill_fastcore(issue) for issue in issues]

    def download_data(self) -> list[dict]:
        """Download all issues for the configured GitHub repository.

        Returns
        -------
        list[dict]
            Complete issue list across all fetched pages.
        """
        page_counter: int = 1
        data: list[dict] = []

        with Spinner(
            message=f"Getting issues for {GITHUB_REPO_OWNER}/{GITHUB_REPO_PROJECT}... ",
        ) as spinner:
            while True:
                issues: list[dict] = self._query_api(page=page_counter)
                data.extend(issues)

                if len(issues) < self._per_page:
                    break

                page_counter += 1
                spinner.next()

        self.logger.info("Number of issues collected: %d", len(data))

        return data
