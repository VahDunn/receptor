import json
import logging
from typing import Any

import httpx

from receptor.external_services.ai.clients.abstract_ai_client import AbstractAiClient

logger = logging.getLogger(__name__)


class ChadAIClient(AbstractAiClient):
    def __init__(self, client: httpx.AsyncClient, api_key: str, url: str):
        self.api_key = api_key
        self.client = client
        self.url = url

    async def send_prompt(self, prompt_text: str) -> str:
        request_json = {
            "message": prompt_text,
            "api_key": self.api_key,
        }

        logger.info("ChadAIClient -> POST %s", self.url)

        resp = await self.client.post(self.url, json=request_json)
        text = resp.text

        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code}: {text[:1000]}")

        try:
            envelope: dict[str, Any] = resp.json()
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"AI returned invalid JSON envelope: {text[:1000]}"
            ) from e

        is_success = envelope.get("is_success")
        used_words = envelope.get("used_words_count")

        logger.info(
            "ChadAIClient meta: is_success=%s, used_words_count=%s",
            is_success,
            used_words,
        )

        if is_success is False:
            raise RuntimeError(
                f"AI returned is_success=false, envelope={str(envelope)[:1000]}"
            )

        if "response" not in envelope:
            raise RuntimeError(
                f"AI envelope missing 'response': {str(envelope)[:1000]}"
            )

        response = envelope["response"]

        if isinstance(response, dict):
            response = json.dumps(response, ensure_ascii=False)

        if not isinstance(response, str):
            raise RuntimeError(
                f"Unexpected envelope['response'] type: {type(response)!r}"
            )

        return response