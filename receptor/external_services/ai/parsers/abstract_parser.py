from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic


from receptor.utils.types import T


@dataclass(frozen=True)
class AbstractAiParser(ABC, Generic[T]):
    @abstractmethod
    def parse(self, raw: str) -> T: ...
