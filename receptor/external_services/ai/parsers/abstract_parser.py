from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from receptor.core.errors import AiResponseParseError

R = TypeVar("R")


@dataclass(frozen=True)
class AbstractAiParser(ABC, Generic[R]):
    @abstractmethod
    def parse(self, raw: str) -> R: ...

    @staticmethod
    def _extract_json_object(text: str) -> str:
        start = text.find("{")
        if start == -1:
            raise AiResponseParseError("No '{' found in response")

        depth = 0
        for i in range(start, len(text)):
            ch = text[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start : i + 1]

        raise AiResponseParseError("Unbalanced braces; can't extract JSON")
