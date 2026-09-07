from collections.abc import Generator
from json import dumps

from requests import Response, post
from tqdm import tqdm

from joss import GITHUB_REPO_OWNER, GITHUB_REPO_PROJECT, HTTP_POST_TIMEOUT
from joss.interfaces import ExtractInterface
from joss.logger import JOSSLogger


class Extract(ExtractInterface):
    def __init__(
        self,
        github_token: str,
        logger: JOSSLogger,
        github_owner: str = GITHUB_REPO_OWNER,
        github_repo: str = GITHUB_REPO_PROJECT,
    ) -> None:
        self.responses: list[Response] = []
        self.api_endpoint: str = "https://api.github.com/graphql"
        self.logger: JOSSLogger = JOSSLogger()

        self.static_variables: dict[str, str | None] = {
            "owner": github_owner,
            "name": github_repo,
            "cursor": None,
        }

        self.headers: dict[str, str] = {
            "Authorization": f"Bearer {github_token}",
            "Content-Type": "application/json",
        }

        self.query: str = """
        query($owner: String!, $name: String!, $cursor: String) {
          repository(owner: $owner, name: $name) {
            issues(first: 100, after: $cursor, states: [OPEN, CLOSED]) {
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                databaseId
                body
                state
                author {
                  login
                }
                labels(first: 100) {
                  nodes {
                    name
                  }
                }
              }
            }
          }
        }
        """

    @staticmethod
    def _get_resp_page_information(resp: Response) -> tuple[bool, str]:
        page_info: dict = resp.json()["data"]["repository"]["issues"]["pageInfo"]
        return (page_info["hasNextPage"], page_info["endCursor"])

    def recursive_query_graphql(
        self,
        cursor: str | None = None,
        has_next_page: bool = True,
    ) -> None:
        if cursor is None:
            self.logger.info("Querying GitHub GraphQL issue endpoint...")
        # If there is no next page, break out of the recursion tree
        if has_next_page is False:
            return

        # Update the variables to the GraphQL query with the cursor to the next
        # page
        self.static_variables["cursor"] = cursor

        # Make the HTTP POST request
        self.logger.debug("POST: %s", cursor)
        resp: Response = post(
            url=self.api_endpoint,
            json={"query": self.query, "variables": self.static_variables},
            headers=self.headers,
            timeout=HTTP_POST_TIMEOUT,
        )

        # Error out if the resp code is not 200
        if resp.status_code != 200:
            raise RuntimeError(
                f"GraphQL request failed (Status {resp.status_code}): {resp.text}"
            )

        # Append the respone to the global responses list
        self.responses.append(resp)

        # Get the status of the next page
        has_next_page, cursor = self._get_resp_page_information(resp=resp)

        # Run the recursion again with updated parameters
        self.recursive_query_graphql(
            cursor=cursor,
            has_next_page=has_next_page,
        )

    def extract(self) -> list[dict]:
        # Subroutine to extract fields from a requests.Response.json() object
        def _normalize_node(node: dict) -> dict:
            # Map fields to requested database columns
            github_issue_id = node.get("databaseId")
            body = node.get("body", "")
            state = node.get("state")
            author_obj = node.get("author")
            creator = author_obj.get("login") if author_obj else None

            # Extract label names and serialize to string format for SQLite
            labels_nodes = node.get("labels", {}).get("nodes", [])
            label_names = [l["name"] for l in labels_nodes if l and "name" in l]
            labels_str = dumps(label_names)

            return {
                "github_issue_id": github_issue_id,
                "body": body,
                "creator": creator,
                "state": state,
                "labels": labels_str,
            }

        # If the POST requests have not been made and responses collected, run
        if len(self.responses) == 0:
            self.recursive_query_graphql()

        # Create an empty list to store data
        data: list[dict] = []

        # Create a Generator of lists of nodes from each requests.Response.json object
        nodes_generator: Generator = (
            resp.json()["data"]["repository"]["issues"]["nodes"]
            for resp in self.responses
        )

        # For each list of nodes, normalize the content and write to a dictionary
        nodes: list[dict]
        for nodes in tqdm(
            iterable=nodes_generator,
            desc="Normalizing JOSS review responses... ",
            unit=" responses",
        ):
            data.extend(map(_normalize_node, nodes))

        return data
