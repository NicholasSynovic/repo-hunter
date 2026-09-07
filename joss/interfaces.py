from abc import ABC, abstractmethod

from joss.models import JOSSGHIssue


class ExtractInterface(ABC):
    @abstractmethod
    def extract(self) -> list[JOSSGHIssue]: ...


class TransformInterface(ABC):
    @abstractmethod
    def transform(self, data: list[dict]) -> dict[str, list]: ...


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
