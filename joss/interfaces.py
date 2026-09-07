from abc import ABC, abstractmethod

from joss.models import JOSSGHIssue, JOSSPaperProjectIssue


class ExtractInterface(ABC):
    @abstractmethod
    def extract(self) -> list[JOSSGHIssue]: ...


class TransformInterface(ABC):
    @abstractmethod
    def transform(self, data: list[JOSSGHIssue]) -> list[JOSSPaperProjectIssue]: ...


class LoadInterface(ABC):
    @abstractmethod
    def load_data(
        self,
        issues: list[JOSSGHIssue],
        ppi: list[JOSSPaperProjectIssue],
    ) -> None: ...
