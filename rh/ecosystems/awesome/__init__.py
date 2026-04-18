"""Normalized models for Ecosyste.ms Awesome ETL outputs."""

from pydantic import BaseModel


class AwesomeList(BaseModel):
    """Normalized Awesome list record.

    Parameters
    ----------
    id : int
        Unique list identifier from the source API.
    projects_url : str
        API URL used to fetch projects for this list.
    repository_url : str, default=""
        Repository URL of the list when provided.
    json_str : str
        Full source payload serialized as JSON.
    """

    id: int
    projects_url: str
    repository_url: str = ""
    json_str: str


class ListProject(BaseModel):
    """Normalized project record associated with an Awesome list.

    Parameters
    ----------
    id : int
        Unique project identifier from the source API.
    list_id : int
        Parent list identifier.
    repository_url : str, default=""
        Repository URL when available.
    json_str : str
        Full source payload serialized as JSON.
    """

    id: int
    list_id: int
    repository_url: str = ""
    json_str: str
