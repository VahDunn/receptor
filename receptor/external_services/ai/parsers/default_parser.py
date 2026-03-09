from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
import json
from typing import Any, Generic, Mapping, Type, TypeVar

from pydantic import BaseModel, ValidationError as PydanticValidationError

from receptor.external_services.ai.parsers.abstract_parser import AbstractAiParser
from receptor.core.errors import AiResponseParseError


T = TypeVar("T", bound=BaseModel)


_MIN_BY_UNIT = {
    "pcs": Decimal("1"),
    "g": Decimal("100"),
    "ml": Decimal("100"),
    "kg": Decimal("0.2"),
    "l": Decimal("0.2"),
}


def sanitize_products_with_quantities(data: Any) -> Any:
    if not isinstance(data, dict):
        return data

    pwq = data.get("products_with_quantities")
    if not isinstance(pwq, list):
        return data

    for item in pwq:
        if not isinstance(item, dict):
            continue
        unit = item.get("unit")
        q = item.get("quantity")
        try:
            qd = Decimal(str(q))
        except Exception:
            qd = Decimal("0")

        if qd <= 0 and unit in _MIN_BY_UNIT:
            item["quantity"] = _MIN_BY_UNIT[unit]

    return data


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
        # data = sanitize_products_with_quantities(data)
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