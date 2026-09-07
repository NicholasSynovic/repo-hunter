from abc import ABC, abstractmethod

from pydantic import BaseModel


class AwesomeList(BaseModel):
    id: int
    projects_url: str
    repository_url: str
    json_str: str


class ListProject(BaseModel):
    id: int
    list_id: int
    repository_url: str
    json_str: str


class ExtractInterface(ABC):
    @abstractmethod
    def extract(self) -> list[AwesomeList]: ...


class TransformInterface(ABC):
    @abstractmethod
    def transform(self, data: list[AwesomeList]) -> list[ListProject]: ...


class LoadInterface(ABC):
    @abstractmethod
    def load_data(
        self,
        lists: list[AwesomeList],
        projects: list[ListProject],
    ) -> None: ...
