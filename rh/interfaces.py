"""Abstract ETL interfaces shared across dataset pipelines."""

from abc import ABC, abstractmethod


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
