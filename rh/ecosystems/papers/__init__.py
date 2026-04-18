"""Normalized models for Ecosyste.ms Papers ETL outputs."""

from pydantic import BaseModel


class PapersProject(BaseModel):
    """Normalized Ecosyste.ms Papers project record.

    Parameters
    ----------
    id : int
        Unique project identifier from the source API.
    project_url : str
        Canonical project URL in the Papers ecosystem.
    repository_url : str, default=""
        Associated repository URL when available.
    json_str : str
        Full source payload serialized as JSON.
    """

    id: int
    project_url: str
    repository_url: str = ""
    json_str: str


class PapersMention(BaseModel):
    """Normalized mention record linked to a Papers project.

    Parameters
    ----------
    id : int
        Unique mention identifier from the source API.
    project_url : str
        URL of the project referenced by the mention.
    doi : str
        DOI extracted from the mention paper URL.
    """

    id: int
    project_url: str
    doi: str
