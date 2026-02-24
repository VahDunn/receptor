from fastapi import Depends, Request

from receptor.external_services.ai.clients.abstract_ai_client import AbstractAiClient
from receptor.services.ai_service import AIService


def get_ai_client(request: Request) -> AbstractAiClient:
    return request.app.state.ai_client


def get_ai_service(
    ai_client: AbstractAiClient = Depends(get_ai_client),
) -> AIService:
    return AIService(ai_client=ai_client)
