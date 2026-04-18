"""Extraction logic for the Ecosyste.ms Papers dataset."""

# Copyright (c) 2026 Nicholas M. Synovic

from logging import Logger

from rh.ecosystems.api.papers import PapersAPI
from rh.interfaces import ExtractInterface
from rh.logger import JOSSLogger
from progress.bar import Bar


class PapersExtract(ExtractInterface):
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

        self.projects: list[dict] = []
        self.mentions: list[dict] = []

    def get_projects(self) -> None:
        """Fetch all projects from the Papers API."""
        with Bar(
            "Getting projects from Ecosyste.ms Papers API...",
            max=self._api.total_project_pages,
        ) as bar:
            while True:
                projects: list[dict] = self._api.get_projects()
                if not projects:
                    break

                self.projects.extend(projects)
                bar.max = self._api.total_project_pages
                bar.next()

        self.logger.info("Number of papers projects collected: %d", len(self.projects))

    def get_mentions(self) -> None:
        """Fetch all mentions for projects that have mention records."""
        project: dict

        with Bar(
            "Getting project mentions from Ecosyste.ms Papers API...",
            max=len(self.projects),
        ) as bar:
            for project in self.projects:
                if project.get("mentions_count", 0) > 0:
                    project_mention_url: str = project["mentions_url"]

                    # Reset mention pagination per project to avoid state
                    # carry-over between project mention streams.
                    self._api.mention_page = 1
                    self._api.total_mention_pages = 100

                    while self._api.mention_page <= self._api.total_mention_pages:
                        mentions: list[dict] | None = (
                            self._api.get_mentions_from_project(
                                project_mention_url=project_mention_url,
                            )
                        )

                        if not mentions:
                            break

                        self.mentions.extend(mentions)
                        self._api.mention_page += 1

                bar.next()

        self.logger.info("Number of papers mentions collected: %d", len(self.mentions))

    def download_data(self) -> list[dict[str, list[dict]]]:
        """
        Download all projects and mentions from the Papers API.

        Returns:
            A single-item list containing ``projects`` and ``mentions`` payloads.

        """
        # Reset local and API state so repeated runs on the same extractor
        # instance do not carry stale pagination/data forward.
        self.projects = []
        self.mentions = []
        self._api.project_page = 1
        self._api.total_project_pages = 100
        self._api.mention_page = 1
        self._api.total_mention_pages = 100

        self.get_projects()
        self.get_mentions()

        return [
            {
                "projects": self.projects,
                "mentions": self.mentions,
            },
        ]
