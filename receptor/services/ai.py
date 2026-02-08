from receptor.external_services.ai.clients.abstract_ai_client import AbstractAiClient
from receptor.external_services.ai.parsers.abstract_parser import AbstractAiParser
from receptor.utils.types import T


class AIService:
    def __init__(
        self,
        ai_client: AbstractAiClient,
        parser: AbstractAiParser,
    ):
        self.ai_client = ai_client
        self.parser = parser

    async def get(self, prompt: str) -> T:
        ai_response = await self.ai_client.send_prompt(prompt)
        return self.parser.parse(ai_response)
