from abc import ABC, abstractmethod


class AbstractAiClient(ABC):
    @abstractmethod
    def send_prompt(self, prompt):
        pass
