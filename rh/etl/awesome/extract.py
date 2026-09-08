import re
import sys
from collections.abc import Generator
from json import dumps
from re import Match

from loguru import logger
from requests import Response, Session
from requests.adapters import HTTPAdapter, Retry

from rh import HTTP_GET_TIMEOUT
from rh.etl import ExtractInterface
from rh.etl.awesome import AWESOME_API_BASE_URL, AwesomeList


class Extract(ExtractInterface):
    def __init__(
        self,
        email: str,
        api_base_url: str = AWESOME_API_BASE_URL,
        per_page: int = 100,
    ) -> None:
        self.responses: list[Response] = []
        self.api_endpoint: str = f"{api_base_url}/lists"

        self.static_variables: dict[str, str | int] = {
            "page": 1,
            "per_page": per_page,
            "mailto": email,
        }

        # Define exponential backoff strategy
        # backoff_factor=1 means sleep for [0s, 2s, 4s, 8s, ...] between retries
        retry_strategy: Retry = Retry(
            total=10,
            backoff_factor=1,
            status_forcelist=[402, 403, 429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
        )

        adapter: HTTPAdapter = HTTPAdapter(max_retries=retry_strategy)
        self.headers: dict[str, str] = {
            "User-Agent": "nicholassynovic/awesome-dataset",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }
        self.session: Session = Session()
        self.session.mount(prefix="https://", adapter=adapter)
        self.session.mount(prefix="http://", adapter=adapter)
        self.session.headers.update(self.headers)

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

    def _fetch_all_lists(self) -> None:
        # Loop until the current page reaches the next page reported by the
        # API's Link header
        while True:
            logger.info(f"Sending GET request: page {self.static_variables['page']}")
            resp: Response = self.session.get(
                url=self.api_endpoint,
                params=self.static_variables,
                timeout=HTTP_GET_TIMEOUT,
            )

            # Error out if the resp code is not 200
            if resp.status_code != 200:
                logger.error(
                    f"GET request failed (Status {resp.status_code}): {resp.text})"
                )
                sys.exit(2)

            # Append the response to the global responses list
            self.responses.append(resp)

            # If there is no next page, break out of the loop
            next_page: int = self._get_next_page(resp=resp)
            if next_page == -1 or self.static_variables["page"] >= next_page:
                logger.debug("Exiting pagination loop")
                break

            self.static_variables["page"] += 1

    @staticmethod
    def _normalize_list(node: dict) -> AwesomeList:
        # Subroutine to extract fields from a requests.Response.json() object
        # Map fields to requested database columns
        list_id: int = node.get("id", -1)
        projects_url: str = node.get("projects_url", "")

        # The API can emit explicit nulls, so fall back to safe defaults
        url: str = node.get("url") or ""
        name: str = node.get("name") or ""
        description: str = node.get("description") or ""
        projects_count: int = node.get("projects_count") or 0
        list_of_lists: bool = node.get("list_of_lists") or False
        primary_language: str | None = node.get("primary_language")

        # Nested repository record; nil when the list has not been synced yet
        repository: dict = node.get("repository") or {}
        repository_url: str = repository.get("html_url") or ""
        stars: int = repository.get("stargazers_count") or 0

        return AwesomeList(
            id=list_id,
            url=url,
            name=name,
            description=description,
            projects_count=projects_count,
            stars=stars,
            primary_language=primary_language,
            list_of_lists=list_of_lists,
            projects_url=projects_url,
            repository_url=repository_url,
            json_str=dumps(node),
        )

    def extract(self) -> list[AwesomeList]:
        # If the GET requests have not been made and responses collected, run
        if len(self.responses) == 0:
            self._fetch_all_lists()

        # Create an empty list to store data
        data: list[AwesomeList] = []

        # Create a Generator of list payloads from each requests.Response object
        lists_generator: Generator = (resp.json() for resp in self.responses)

        # For each page of lists, normalize the content and write to a list
        logger.info("Extracting Awesome lists...")
        lists: list[dict]
        for lists in lists_generator:
            data.extend(map(self._normalize_list, lists))

        logger.info(f"Extracted {len(data)} Awesome lists")
        return data
