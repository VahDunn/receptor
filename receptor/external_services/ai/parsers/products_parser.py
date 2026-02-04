import json
from dataclasses import dataclass
from typing import Any

from receptor.external_services.ai.response_schemas.products_schema import (
    ProductsResponseDTO,
)
from receptor.utils.errors import ValidationError, AiResponseParseError


@dataclass(frozen=True)
class ProductsAiResponseParser:
    strict_json_only: bool = True

    def parse(self, raw: str) -> ProductsResponseDTO:
        raw = raw.strip()

        if self.strict_json_only:
            data = self._loads_json(raw)
        else:
            data = self._loads_json(self._extract_json_object(raw))

        try:
            return ProductsResponseDTO.model_validate(data)
        except ValidationError as e:
            raise AiResponseParseError(f"Invalid products schema: {e}") from e

    @staticmethod
    def _loads_json(s: str) -> Any:
        try:
            return json.loads(s)
        except json.JSONDecodeError as e:
            raise AiResponseParseError(f"Invalid JSON: {e}") from e

    @staticmethod
    def _extract_json_object(text: str) -> str:
        """
        Фоллбек: вырезаем первый JSON-объект по балансировке скобок.
        Полезно, если модель иногда добавляет текст вокруг JSON.
        """
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
