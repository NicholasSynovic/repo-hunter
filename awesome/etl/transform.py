"""Transform Awesome API payloads into normalized table records."""

from collections import defaultdict
from json import dumps
from logging import Logger
from urllib.parse import unquote

from progress.bar import Bar

from awesome.etl import AwesomeMention, AwesomeProject, TransformInterface
from awesome.logger import AwesomeLogger


class AwesomeTransform(TransformInterface):
    """Transformer for Ecosyste.ms Awesome extract payloads.

    Parameters
    ----------
    logger : AwesomeLogger
        Application logger wrapper.
    """

    def __init__(
        self,
        logger: AwesomeLogger,
    ) -> None:
        """Initialize the transformer logger."""
        self.logger: Logger = logger.get_logger()

    def normalize_paper_projects(
        self,
        projects: list[dict],
    ) -> list[AwesomeProject]:
        """Normalize list-project payloads for ``_ecosystems_projects``.

        Parameters
        ----------
        projects : list[dict]
            Raw list-project records returned by the Awesome API.

        Returns
        -------
        list[AwesomeProject]
            Normalized project rows.
        """
        data: list[AwesomeProject] = []

        with Bar(
            "Normalizing projects for the `_ecosystems_projects` table... ",
            max=len(projects),
        ) as bar:
            project: dict
            for project in projects:
                repository_url: str = ""
                try:
                    repository_url = project["package"]["repository_url"]
                except TypeError:
                    pass

                datum: AwesomeProject = AwesomeProject(
                    id=project["id"],
                    project_url=project["project_url"],
                    repository_url=repository_url,
                    json_str=dumps(obj=project, indent=4),
                )

                data.append(datum)
                bar.next()

        self.logger.info(
            "Normalized %d issues for the `_ecosystems_projects` table",
            len(data),
        )
        return data

    def normalize_paper_project_mentions(
        self,
        mentions: list[dict],
    ) -> list[AwesomeMention]:
        """Normalize mention-like payloads for ``_ecosystems_mentions``.

        Parameters
        ----------
        mentions : list[dict]
            Raw mention records associated with Awesome projects.

        Returns
        -------
        list[AwesomeMention]
            Normalized mention rows with DOI values.
        """
        data: list[AwesomeMention] = []

        with Bar(
            "Normalizing issues for the `_ecosystems_mentions` table... ",
            max=len(mentions),
        ) as bar:
            mention: dict
            for mention in mentions:
                doi: str = unquote(string=mention["paper_url"].split("papers/")[1])

                datum: AwesomeMention = AwesomeMention(
                    id=mention["id"],
                    project_url=mention["project_url"],
                    doi=doi,
                )

                data.append(datum)
                bar.next()

        self.logger.info(
            "Normalized %d issues for the `_ecosystems_mentions` table",
            len(data),
        )
        return data

    def transform_data(self, data: list[dict]) -> dict[str, list]:
        """Transform extracted payload bundle into table-keyed row mappings.

        Parameters
        ----------
        data : list[dict]
            Extractor payload list containing ``projects`` and ``mentions``.

        Returns
        -------
        dict[str, list]
            Mapping from table names to normalized row dictionaries.
        """
        normalized_data: dict[str, list] = defaultdict(list)

        def dict_tool(rows: list) -> list[dict]:
            return [row.model_dump() for row in rows]

        normalized_data["_ecosystems_projects"] = self.normalize_paper_projects(
            projects=data[0]["projects"],
        )
        normalized_data["_ecosystems_mentions"] = self.normalize_paper_project_mentions(
            mentions=data[0]["mentions"],
        )

        normalized_data["_ecosystems_projects"] = dict_tool(
            normalized_data["_ecosystems_projects"]
        )
        normalized_data["_ecosystems_mentions"] = dict_tool(
            normalized_data["_ecosystems_mentions"]
        )

        return normalized_data
