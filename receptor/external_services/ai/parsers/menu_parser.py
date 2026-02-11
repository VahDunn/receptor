from receptor.external_services.ai.parsers.abstract_parser import AbstractAiParser


class MenuAiResponseParser(AbstractAiParser):
    def parse(self, raw: str):
        return raw
