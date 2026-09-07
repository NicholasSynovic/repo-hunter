import re
from json import dumps
from re import Match

from loguru import logger
from requests import Response, Session
from requests.adapters import HTTPAdapter, Retry

from awesome import HTTP_GET_TIMEOUT
from awesome.etl import AwesomeList, ListProject, TransformInterface


class Transform(TransformInterface):
    def __init__(
        self,
        email: str,
        per_page: int = 100,
    ) -> None:
        self.email: str = email
        self.per_page: int = per_page

        # Define exponential backoff strategy
        # backoff_factor=1 means sleep for [0s, 2s, 4s, 8s, ...] between retries
        retry_strategy: Retry = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[403, 429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET"],
        )

        adapter: HTTPAdapter = HTTPAdapter(max_retries=retry_strategy)
        self.session: Session = Session()
        self.session.mount(prefix="http://", adapter=adapter)
        self.session.mount(prefix="https://", adapter=adapter)

    @staticmethod
    def _get_last_page(resp: Response) -> int:
        # Subroutine to extract the last page number from the Link header
        last_page: int = -1
        pattern: str = r"[?&]page=(\d+).*?rel=\"last\""

        link_last_page: str = resp.headers["link"].split(sep=",")[-1].strip()
        match: Match[str] | None = re.search(pattern, link_last_page)
        if match:
            last_page = int(match.group(1))

        return last_page

    @staticmethod
    def _extract_repository_url(node: dict) -> str:
        # Top-level repository URL from a list project record
        repository_url: str | None = node.get("repository_url")

        # Fallback to the nested package repository URL
        if repository_url is None:
            package: dict | None = node.get("package")
            if package is not None:
                repository_url = package.get("repository_url")

        if repository_url is not None:
            logger.debug("Found repository url")
            return repository_url

        logger.warning("No repository url found")
        return ""

    def _fetch_list_projects(self, list_record: AwesomeList) -> list[dict]:
        projects: list[dict] = []
        page: int = 1

        # Loop until the current page reaches the last page reported by the
        # API's Link header
        while True:
            logger.debug(f"Sending GET request to {list_record.projects_url} ...")
            resp: Response = self.session.get(
                url=list_record.projects_url,
                params={
                    "page": page,
                    "per_page": self.per_page,
                    "mailto": self.email,
                },
                timeout=HTTP_GET_TIMEOUT,
            )

            # Error out of this list if the resp code is not 200
            if resp.status_code != 200:
                logger.error(
                    f"GET request failed (Status {resp.status_code}): {resp.text})"
                )
                break

            nodes: list[dict] = resp.json()
            if not nodes:
                break

            projects.extend(nodes)

            # If there is no next page, break out of the loop
            last_page: int = self._get_last_page(resp=resp)
            if last_page == -1 or page >= last_page:
                logger.debug("Exiting pagination loop")
                break

            page += 1

        return projects

    def normalize_list_projects(
        self,
        lists: list[AwesomeList],
    ) -> list[ListProject]:
        project_id: int = 0
        data: list[ListProject] = []

        # Leverage a sieve to filter out lists
        logger.info("Normalizing lists...")

        filtered_lists: filter[AwesomeList] = filter(
            lambda x: x.projects_url != "", lists
        )
        logger.debug("Filtered on `.projects_url` for project fetching")

        list_record: AwesomeList
        for list_record in filtered_lists:
            nodes: list[dict] = self._fetch_list_projects(list_record=list_record)

            node: dict
            for node in nodes:
                repository_url: str = self._extract_repository_url(node=node)

                datum: ListProject = ListProject(
                    id=project_id,
                    list_id=list_record.id,
                    repository_url=repository_url,
                    json_str=dumps(node),
                )

                data.append(datum)
                project_id += 1

        logger.info(f"Normalized {len(data)} list projects")
        return data

    def transform(self, data: list[AwesomeList]) -> list[ListProject]:
        # Build list-project mappings from the fetched lists
        list_projects: list[ListProject] = self.normalize_list_projects(lists=data)

        logger.info(
            f"Transformed {len(data)} lists into "
            f"{len(list_projects)} list project mappings"
        )
        return list_projects
