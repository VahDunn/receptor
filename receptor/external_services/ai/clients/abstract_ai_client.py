from abc import ABC, abstractmethod


class AbstractAiClient(ABC):
    """Отправить промпт и получить ответ."""
    @abstractmethod
    async def send_prompt(self, prompt) -> str:
        pass
