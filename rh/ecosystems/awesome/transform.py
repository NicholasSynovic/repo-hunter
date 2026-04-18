from collections import defaultdict
from json import dumps
from logging import Logger
from urllib.parse import unquote

from rh.ecosystems.papers import PapersMention, PapersProject
from rh.interfaces import TransformInterface
from rh.logger import JOSSLogger
from progress.bar import Bar


class PapersTransform(TransformInterface):
    def __init__(
        self,
        joss_logger: JOSSLogger,
    ) -> None:
        self.logger: Logger = joss_logger.get_logger()

    def normalize_paper_projects(
        self,
        projects: list[dict],
    ) -> list[PapersProject]:
        data: list[PapersProject] = []

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

                datum: PapersProject = PapersProject(
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
    ) -> list[PapersMention]:
        data: list[PapersMention] = []

        with Bar(
            "Normalizing issues for the `_ecosystems_mentions` table... ",
            max=len(mentions),
        ) as bar:
            mention: dict
            for mention in mentions:
                doi: str = unquote(string=mention["paper_url"].split("papers/")[1])

                datum: PapersMention = PapersMention(
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
        normalized_data: dict[str, list] = defaultdict(list)
        dict_tool = lambda foo: [bar.model_dump() for bar in foo]

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
