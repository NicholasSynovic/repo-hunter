"""Constants and normalized models for the ``rh joss`` pipeline."""

from string import Template

from pydantic import BaseModel

GITHUB_REPO_OWNER: str = "openjournals"
GITHUB_REPO_PROJECT: str = "joss-reviews"

JOSS_ACTIVE_PAPERS_TEMPLATE: Template = Template(
    template="https://joss.theoj.org/papers/active.atom?page=$page"
)
JOSS_PUBLISHED_PAPERS_TEMPLATE: Template = Template(
    template="https://joss.theoj.org/papers/published.atom?page=$page"
)

HTTP_GET_TIMEOUT: int = 60
HTTP_HEAD_TIMEOUT: int = 60
HTTP_POST_TIMEOUT: int = 60


class JOSSGHIssue(BaseModel):
    """Normalized representation of a JOSS GitHub issue.

    Parameters
    ----------
    id : int
        GitHub issue number.
    is_pull_request : bool
        Whether the source record is a pull request.
    labels : str
        JSON-encoded list of label names.
    body : str
        Raw issue body text.
    creator : str
        Login of the issue creator.
    state : str
        GitHub issue state.
    json_str : str
        Full source issue payload serialized to JSON.
    """

    id: int
    is_pull_request: bool
    labels: str
    body: str
    creator: str
    state: str
    json_str: str


class JOSSPaperProjectIssue(BaseModel):
    """Mapping from accepted JOSS issue to paper project metadata.

    Parameters
    ----------
    id : int
        Synthetic row identifier assigned during transformation.
    joss_github_issue_id : int
        Source JOSS GitHub issue number.
    github_repo_url : str
        Repository URL extracted from the issue body.
    joss_url : str
        Canonical JOSS paper URL.
    joss_resolved_url : str
        Final redirect target for ``joss_url`` when URL resolution is enabled.
    journal : str, default="joss"
        Journal identifier for downstream analysis.
    """

    id: int
    joss_github_issue_id: int
    github_repo_url: str
    joss_url: str
    joss_resolved_url: str
    journal: str = "joss"
