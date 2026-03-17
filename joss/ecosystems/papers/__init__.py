from pydantic import BaseModel


class PapersProject(BaseModel):
    id: int
    project_url: str
    repository_url: str = ""
    json_str: str


class PapersMention(BaseModel):
    id: int
    project_url: str
    doi: str
