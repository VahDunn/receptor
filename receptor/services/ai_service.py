import asyncio
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
        self._semaphore = asyncio.Semaphore(50)


    async def get(self, prompt: str, parser: AbstractAiParser[R]) -> R:
        async with self._semaphore:
            raw_response = await self.ai_client.send_prompt(prompt)
            print(raw_response)
        return parser.parse(raw_response)
