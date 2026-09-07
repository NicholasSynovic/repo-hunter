from abc import ABC, abstractmethod

from pydantic import BaseModel


class ExtractInterface(ABC):
    @abstractmethod
    def extract(self) -> list[BaseModel]: ...


class TransformInterface(ABC):
    @abstractmethod
    def transform(self, data: list[BaseModel]) -> list[BaseModel]: ...


class LoadInterface(ABC):
    @abstractmethod
    def load_data(
        self,
        raw: list[BaseModel],
        derived: list[BaseModel],
    ) -> None: ...
