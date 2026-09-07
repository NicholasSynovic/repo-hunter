import sys
from collections.abc import Generator
from json import dumps

from loguru import logger
from requests import Response, post

from rh import HTTP_POST_TIMEOUT
from rh.etl import ExtractInterface
from rh.etl.joss import GITHUB_REPO_OWNER, GITHUB_REPO_PROJECT, JOSSGHIssue


class Extract(ExtractInterface):
    def __init__(
        self,
        github_token: str,
        github_owner: str = GITHUB_REPO_OWNER,
        github_repo: str = GITHUB_REPO_PROJECT,
    ) -> None:
        self.responses: list[Response] = []
        self.api_endpoint: str = "https://api.github.com/graphql"

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
        # If there is no next page, break out of the recursion tree
        if has_next_page is False:
            logger.debug("Exiting recursion tree")
            return

        # Update the variables to the GraphQL query with the cursor to the next
        # page
        self.static_variables["cursor"] = cursor

        # Make the HTTP POST request
        logger.info(f"Sending POST request: {str(cursor)[-10:]}")
        resp: Response = post(
            url=self.api_endpoint,
            json={"query": self.query, "variables": self.static_variables},
            headers=self.headers,
            timeout=HTTP_POST_TIMEOUT,
        )

        # Error out if the resp code is not 200
        if resp.status_code != 200:
            logger.error(
                f"POST request failed (Status {resp.status_code}): {resp.text})"
            )
            sys.exit(2)

        # Append the respone to the global responses list
        self.responses.append(resp)

        # Get the status of the next page
        has_next_page, cursor = self._get_resp_page_information(resp=resp)

        # Run the recursion again with updated parameters
        self.recursive_query_graphql(
            cursor=cursor,
            has_next_page=has_next_page,
        )

    @staticmethod
    def _normalize_node(node: dict) -> JOSSGHIssue:
        # Subroutine to extract fields from a requests.Response.json() object
        # Map fields to requested database columns
        github_issue_id: int = node.get("databaseId", -1)
        body: str = node.get("body", "")
        state: str = node.get("state", "")
        author_obj: dict | None = node.get("author")
        creator: str | None = author_obj.get("login") if author_obj else ""

        # Extract label names and serialize to string format for SQLite
        labels_nodes: list[dict] = node.get("labels", {}).get("nodes", [])
        label_names: list[str] = [l["name"] for l in labels_nodes if l and "name" in l]
        labels_str: str = dumps(label_names)

        return JOSSGHIssue(
            id=github_issue_id,
            labels=labels_str,
            body=body,
            creator=creator,
            state=state,
            json_str=dumps(node),
        )

    def extract(self) -> list[JOSSGHIssue]:
        # If the POST requests have not been made and responses collected, run
        if len(self.responses) == 0:
            self.recursive_query_graphql()

        # Create an empty list to store data
        data: list[JOSSGHIssue] = []

        # Create a Generator of lists of nodes from each requests.Response.json object
        nodes_generator: Generator = (
            resp.json()["data"]["repository"]["issues"]["nodes"]
            for resp in self.responses
        )

        # For each list of nodes, normalize the content and write to a dictionary
        logger.info("Extracting GitHub issues...")
        nodes: list[dict]
        for nodes in nodes_generator:
            data.extend(map(self._normalize_node, nodes))

        logger.info(f"Extracted {len(data)} GitHub issues")
        return data
