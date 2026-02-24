from receptor.external_services.ai.parsers.menu_parser import MenuAiParser
from receptor.external_services.ai.parsers.products_parser import ProductsAiParser


def get_products_parser() -> ProductsAiParser:
    return ProductsAiParser(strict_json_only=True)


def get_menu_parser() -> MenuAiParser:
    return MenuAiParser()
