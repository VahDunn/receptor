from abc import ABC, abstractmethod
from typing import Any


class AbstractAIClient(ABC):

    @abstractmethod
    async def send_prompt(self, prompt: str) -> dict[str, Any]:
        pass