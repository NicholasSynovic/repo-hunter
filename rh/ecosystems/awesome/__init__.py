from pydantic import BaseModel


class AwesomeList(BaseModel):
    id: int
    projects_url: str
    repository_url: str = ""
    json_str: str


class ListProject(BaseModel):
    id: int
    list_id: int
    repository_url: str = ""
    json_str: str
