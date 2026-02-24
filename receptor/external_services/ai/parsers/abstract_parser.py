from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

R = TypeVar("R")


@dataclass(frozen=True)
class AbstractAiParser(ABC, Generic[R]):
    @abstractmethod
    def parse(self, raw: str) -> R: ...
