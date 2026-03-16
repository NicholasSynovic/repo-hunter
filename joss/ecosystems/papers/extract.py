"""Extraction logic for the Ecosyste.ms Papers dataset."""

# Copyright (c) 2026 Nicholas M. Synovic

from logging import Logger

from joss.ecosystems.api.papers import PapersAPI
from joss.interfaces import ExtractInterface
from joss.logger import JOSSLogger
from progress.bar import Bar


class PaperExtractor(ExtractInterface):
    """Extractor for project responses from the Ecosyste.ms Papers API."""

    def __init__(
        self,
        joss_logger: JOSSLogger,
        email: str,
        per_page: int = 100,
    ) -> None:
        """
        Initialize the papers extractor.

        Args:
            joss_logger: Logger wrapper used by the application.
            email: Contact email sent to the Papers API via ``mailto``.
            per_page: Number of records requested per API page.

        """
        self.logger: Logger = joss_logger.get_logger()
        self._api: PapersAPI = PapersAPI(
            email=email,
            logger=self.logger,
            per_page=per_page,
        )

    def download_data(self) -> list[dict]:
        """
        Download all project responses from the Papers API.

        Returns:
            A list of raw project response dictionaries.

        """
        data: list[dict] = []

        with Bar("Getting projects from Ecosyste.ms Papers API...", max=self._api.total_project_pages,) as bar:
            while True:
                projects: list[dict] = self._api.get_projects()
                if not projects:
                    break

                data.extend(projects)
                bar.max = self._api.total_project_pages
                bar.next()

        self.logger.info("Number of papers projects collected: %d", len(data))

        return data
