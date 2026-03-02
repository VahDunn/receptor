import json

from receptor.core.domain.product_categories import ProductTypeCode
from receptor.core.domain.units import UNITS
from receptor.core.domain.marketplaces import Marketplace


PRODUCTS_PROMPT_TEMPLATE = """
Жёсткие правила:
- Верни ТОЛЬКО валидный JSON. Никакого текста вне JSON.
- Вывод начинается с { и заканчивается }.
- Все ключи в двойных кавычках.
- Строго следуй заданной схеме, не добавляй и не удаляй ключи.
- Если информации не хватает — используй null, но не пропускай ключи.
- Позиции должны быть типовыми для Москвы и сети "__MARKETPLACE__".
- Цель каталога: поддержать различные недельные меню с калоражем от 1500 до 3000 ккал/день.
- Держи каталог в диапазоне 180–220 позиций.
- Не дублируй одинаковые товары в разных фасовках без необходимости.
- Избегай брендов, используй обобщённые названия.

Сформируй каталог продуктов для кэширования цен для магазина "__MARKETPLACE__", город Москва.

Категории (строго из списка): __CATEGORIES_JSON__
Поле unit (строго из списка): __UNITS_JSON__

Правила для calories_per_unit (целое число):
- если unit == "g": calories_per_unit = ккал на 100 g
- если unit == "kg": calories_per_unit = ккал на 1 kg
- если unit == "ml": calories_per_unit = ккал на 100 ml
- если unit == "l": calories_per_unit = ккал на 1 l
- если unit == "pcs": calories_per_unit = ккал на 1 штуку

Требования:
- Количество позиций: __POSITIONS_NUMBER__
- Каталог должен покрывать типичное недельное меню (3 приёма пищи в день) на __CALORIES_AMOUNT__ ккал/день
- Сделай упор на белок, крупы, овощи, фрукты, молочку, масла
- Используй универсальные позиции без привязки к брендам

Поля каждой позиции (строго): __RESPONSE_FIELDS_JSON__

Формат ответа (строго по схеме — подставить значения вместо null):
__RESPONSE_FORMAT_JSON__
"""


def build_products_prompt(
    marketplace: Marketplace,
    positions_number: int,
    calories_amount: int,
    response_fields: list[str],
) -> str:
    response_format = {
        "meta": {
            "store": marketplace.value,
            "city": "Москва",
            "catalog_size": positions_number,
            "created_at": None,
            "version": None,
        },
        "items": [{field: None for field in response_fields}],
    }

    return (
        PRODUCTS_PROMPT_TEMPLATE.replace("__MARKETPLACE__", marketplace.value)
        .replace(
            "__CATEGORIES_JSON__",
            json.dumps([c.code for c in ProductTypeCode], ensure_ascii=False),
        )
        .replace("__UNITS_JSON__", json.dumps(UNITS, ensure_ascii=False))
        .replace("__POSITIONS_NUMBER__", str(positions_number))
        .replace("__CALORIES_AMOUNT__", str(calories_amount))
        .replace(
            "__RESPONSE_FIELDS_JSON__",
            json.dumps(response_fields, ensure_ascii=False),
        )
        .replace(
            "__RESPONSE_FORMAT_JSON__",
            json.dumps(response_format, ensure_ascii=False, indent=2),
        )
    )