from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Self

from pydantic import BaseModel

from receptor.core.types import UNSET


@dataclass(slots=True, kw_only=True)
class DTO:
    @classmethod
    def from_schema(cls, schema: BaseModel) -> Self:
        if not is_dataclass(cls):
            raise TypeError(f"{cls.__name__} must be a dataclass")

        schema_data = schema.model_dump(exclude_unset=False)
        provided_fields = schema.model_fields_set

        dto_kwargs: dict[str, Any] = {}

        for field in fields(cls):
            if field.name in provided_fields:
                dto_kwargs[field.name] = schema_data[field.name]
            else:
                dto_kwargs[field.name] = UNSET

        return cls(**dto_kwargs)
