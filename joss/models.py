from pydantic import BaseModel


class JOSSGHIssue(BaseModel):
    id: int
    labels: str
    body: str
    creator: str
    state: str
    json_str: str


class JOSSPaperProjectIssue(BaseModel):
    id: int
    github_issue_id: int
    github_repo_url: str
    joss_url: str
    joss_resolved_url: str
