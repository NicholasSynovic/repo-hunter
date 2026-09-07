"""Normalized models and abstract ETL interfaces for the Awesome pipeline."""

from abc import ABC, abstractmethod

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


class AwesomeProject(BaseModel):
    """Normalized Ecosyste.ms Awesome project record.

    Parameters
    ----------
    id : int
        Unique project identifier from the source API.
    project_url : str
        Canonical project URL in the Awesome ecosystem.
    repository_url : str, default=""
        Associated repository URL when available.
    json_str : str
        Full source payload serialized as JSON.
    """

    id: int
    project_url: str
    repository_url: str = ""
    json_str: str


class AwesomeMention(BaseModel):
    """Normalized mention record linked to an Awesome project.

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


class ExtractInterface(ABC):
    """Interface for extract-phase components."""

    @abstractmethod
    def download_data(self) -> list[dict]:
        """Download raw records from an upstream source.

        Returns
        -------
        list[dict]
            Raw records returned by the source API.
        """


class TransformInterface(ABC):
    """Interface for transform-phase components."""

    @abstractmethod
    def transform_data(self, data: list[dict]) -> dict[str, list]:
        """Transform extracted records into loader-ready table payloads.

        Parameters
        ----------
        data : list[dict]
            Raw or partially normalized records from an extractor.

        Returns
        -------
        dict[str, list]
            Mapping of destination table names to row dictionaries.
        """


class LoadInterface(ABC):
    """Interface for load-phase components."""

    @abstractmethod
    def load_data(self, data: dict[str, list]) -> bool:
        """Write transformed table payloads to a target datastore.

        Parameters
        ----------
        data : dict[str, list]
            Mapping of destination table names to row dictionaries.

        Returns
        -------
        bool
            ``True`` if the write operation completes successfully.
        """
