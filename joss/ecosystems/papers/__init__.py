from pydantic import BaseModel


class PapersProjects(BaseModel):
    id: int
    is_pull_request: bool
    labels: str
    body: str
    creator: str
    state: str
    json_str: str


class PapersMentions(BaseModel):
    id: int
    joss_github_issue_id: int
    github_repo_url: str
    joss_url: str
    joss_resolved_url: str
    journal: str = "joss"
