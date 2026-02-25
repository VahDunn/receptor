from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Generic, Mapping, Type, TypeVar

from pydantic import BaseModel, ValidationError as PydanticValidationError

from receptor.external_services.ai.parsers.abstract_parser import AbstractAiParser
from receptor.utils.errors import AiResponseParseError


T = TypeVar("T", bound=BaseModel)


@dataclass(frozen=True)
class DefaultJsonAiParser(AbstractAiParser[T], Generic[T]):
    schema: Type[T]
    strict_json_only: bool = True
    context: Mapping[str, Any] | None = None

    def parse(self, raw: str) -> T:
        raw = raw.strip()

        data = (
            self._loads_json(raw)
            if self.strict_json_only
            else self._loads_json(self._extract_json_object(raw))
        )

        try:
            return self.schema.model_validate(data, context=self.context)
        except PydanticValidationError as e:
            raise AiResponseParseError(
                f"Invalid {self.schema.__name__} schema: {e}"
            ) from e

    @staticmethod
    def _loads_json(s: str) -> Any:
        try:
            return json.loads(s)
        except json.JSONDecodeError as e:
            raise AiResponseParseError(f"Invalid JSON: {e}") from e
