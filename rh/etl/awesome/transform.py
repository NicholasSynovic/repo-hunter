import re
from json import dumps
from re import Match

from loguru import logger
from requests import Response, Session
from requests.adapters import HTTPAdapter, Retry

from rh import HTTP_GET_TIMEOUT
from rh.etl import TransformInterface
from rh.etl.awesome import AwesomeList, ListProject


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
            status_forcelist=[402, 403, 429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET"],
        )

        adapter: HTTPAdapter = HTTPAdapter(max_retries=retry_strategy)
        self.session: Session = Session()
        self.session.mount(prefix="http://", adapter=adapter)
        self.session.mount(prefix="https://", adapter=adapter)

    @staticmethod
    def _get_next_page(resp: Response) -> int:
        # Subroutine to extract the next page number from the Link header
        next_page: int = -1
        url_pattern: str = r"<([^>]*)>;\s*rel=\"next\""
        page_pattern: str = r"[?&]page=(\d+)"

        link_header: str = resp.headers.get("link", "")
        link_match: Match[str] | None = re.search(url_pattern, link_header)
        if link_match is not None:
            page_match: Match[str] | None = re.search(page_pattern, link_match.group(1))
            if page_match is not None:
                next_page = int(page_match.group(1))

        return next_page

    @staticmethod
    def _extract_repository_url(node: dict) -> str:
        # Nested repository record; nil when the project is not synced yet
        repository: dict = node.get("repository") or {}
        repository_url: str = repository.get("html_url") or ""

        if repository_url != "":
            logger.debug("Found repository url")
            return repository_url

        logger.warning("No repository url found")
        return ""

    def _fetch_list_projects(self, list_record: AwesomeList) -> list[dict]:
        projects: list[dict] = []
        page: int = 1

        # Loop until the API's Link header reports no next page
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
            next_page: int = self._get_next_page(resp=resp)
            if next_page == -1 or page >= next_page:
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
