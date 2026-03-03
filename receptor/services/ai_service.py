from typing import TYPE_CHECKING, TypeVar

from receptor.external_services.ai.parsers.abstract_parser import AbstractAiParser


if TYPE_CHECKING:
    from receptor.external_services.ai.clients.abstract_ai_client import (
        AbstractAiClient,
    )


R = TypeVar("R")


class AIService:
    def __init__(self, ai_client: "AbstractAiClient"):
        self.ai_client = ai_client

    async def get(self, prompt: str, parser: AbstractAiParser[R]) -> R:
        raw = await self.ai_client.send_prompt(prompt)
        print(raw)
        return parser.parse(raw)
