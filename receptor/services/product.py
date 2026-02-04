from receptor.external_services.ai.clients.abstract_ai_client import AbstractAiClient
from receptor.external_services.ai.prompts.products_prompt import PROMPT


class ProductsService:
    def __init__(self, repo, ai_client: AbstractAiClient):
        self.prompt = PROMPT
        self.ai_client = ai_client
        self._repo = repo

    async def get_products(self):
        ai_response = await self.ai_client.send_prompt(self.prompt)
