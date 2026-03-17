import re
from logging import Logger
from re import Match

from requests import Response, Session
from requests.adapters import HTTPAdapter, Retry

from joss.ecosystems.api import HTTP_GET_TIMEOUT


class PapersAPI:
    def __init__(
        self,
        email: str,
        logger: Logger,
        project_page: int = 1,
        mention_page: int = 1,
        per_page: int = 100,
    ) -> None:
        self.logger: Logger = logger

        self.email: str = email
        self.project_page: int = project_page
        self.mention_page: int = mention_page
        self.per_page: int = per_page

        # Used to keep track of the number total pages remaining
        self.total_project_pages: int = 100
        self.total_mention_pages: int = 100

        # Create the necessary request session
        self.headers = {
            "User-Agent": "nicholassynovic/joss-dataset",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }
        self.adapter: HTTPAdapter = HTTPAdapter(
            max_retries=Retry(
                total=10,
                backoff_factor=1,
                status_forcelist=[403, 429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
            ),
        )
        self.session: Session = Session()
        self.session.mount("https://", self.adapter)
        self.session.mount("http://", self.adapter)
        self.session.headers.update(self.headers)

    @staticmethod
    def _get_last_page(resp: Response) -> int:
        last_page: int = -1
        pattern: str = r"[?&]page=(\d+).*?rel=\"last\""

        link_last_page: str = resp.headers["link"].split(sep=",")[-1].strip()
        match: Match[str] | None = re.search(pattern, link_last_page)
        if match:
            last_page = int(match.group(1))

        return last_page

    def get_projects(self) -> list:
        # Shortcut to prohibit excessive API calling
        if self.project_page > self.total_project_pages:
            self.logger.error(
                "Project API page count exceeds that of the total number of pages: %d, %d",
                self.project_page,
                self.total_project_pages,
            )
            return []

        projects_api: str = f"https://papers.ecosyste.ms/api/v1/projects?page={self.project_page}&per_page={self.per_page}&mailto={self.email}"
        self.logger.info("Sending GET request to %s", projects_api)
        resp: Response = self.session.get(
            url=projects_api,
            timeout=HTTP_GET_TIMEOUT,
        )
        self.logger.debug("Response status code: %d", resp.status_code)

        self.total_project_pages = self._get_last_page(resp=resp)
        self.project_page += 1

        return resp.json()

    def get_mentions_from_project(self, project_mention_url: str) -> list:
        # Shortcut to prohibit excessive API calling
        if self.mention_page > self.total_mention_pages:
            self.logger.error(
                "Mentions API page count exceeds that of the total number of pages: %d, %d",
                self.mention_page,
                self.total_mention_pages,
            )
            return []

        mentions_api: str = f"{project_mention_url}?page={self.mention_page}&per_page={self.per_page}&mailto={self.email}"
        self.logger.info("Sending GET request to %s", mentions_api)
        resp: Response = self.session.get(
            url=mentions_api,
            timeout=HTTP_GET_TIMEOUT,
        )
        self.logger.debug("Response status code: %d", resp.status_code)

        if resp.status_code == 404:
            self.mention_page = self.total_mention_pages + 1
            # TODO: Does not return a list on this code path
        else:
            self.total_mention_pages = self._get_last_page(resp=resp)
            try:
                return resp.json()
            except:
                self.logger.error(resp.content)
                quit()

    def get_papers_from_mention(self, paper_mention_url: str) -> None:
        paper_api: str = f"{paper_mention_url}?mailto={self.email}"
        self.logger.info("Sending GET request to %s", paper_api)
        resp: Response = self.session.get(
            url=paper_api,
            timeout=HTTP_GET_TIMEOUT,
        )
        return resp.json()
