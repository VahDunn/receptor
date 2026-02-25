import json

from receptor.core.domain.product_categories import ProductTypeCode
from receptor.core.domain.units import UNITS
from receptor.db.models import Product


RESPONSE_FIELDS = [
    column.key
    for column in [
        Product.name,
        Product.type_code,
        Product.unit,
        Product.calories_per_unit,
        Product.price_rub,
    ]
]

RESPONSE_FORMAT = {
    "meta": {
        "store": "Перекрёсток",
        "city": "Москва",
        "catalog_size": 150,
        "created_at": None,
        "version": None,
    },
    "items": [{field: None for field in RESPONSE_FIELDS}],
}

POSITIONS_NUMBER = 150
CALORIES_AMOUNT = 2500

PRODUCTS_PROMPT = f"""
Жёсткие правила:
- Верни ТОЛЬКО валидный JSON. Никакого текста вне JSON.
- Вывод начинается с {{ и заканчивается }}.
- Все ключи в двойных кавычках.
- Строго следуй заданной схеме, не добавляй и не удаляй ключи.
- Если информации не хватает — используй null, но не пропускай ключи.
- Позиции должны быть типовыми для Москвы и сети "Перекрёсток".
- Цель каталога: поддержать различные недельные меню с калоражем от 1500 до 3000 ккал/день.
- Держи каталог в диапазоне 180–220 позиций.
- Не дублируй одинаковые товары в разных фасовках без необходимости.
- Избегай брендов, используй обобщённые названия.

Сформируй каталог продуктов для кэширования цен для магазина "Перекрёсток", город Москва.

Категории (строго из списка): {json.dumps([c.code for c in ProductTypeCode], ensure_ascii=False)}
Поле unit (строго из списка): {json.dumps(UNITS, ensure_ascii=False)}

Правила для calories_per_unit (целое число):
- если unit == "g": calories_per_unit = ккал на 100 g
- если unit == "kg": calories_per_unit = ккал на 1 kg
- если unit == "ml": calories_per_unit = ккал на 100 ml
- если unit == "l": calories_per_unit = ккал на 1 l
- если unit == "pcs": calories_per_unit = ккал на 1 штуку

Требования:
- Количество позиций: {POSITIONS_NUMBER}
- Каталог должен покрывать типичное недельное меню (3 приёма пищи в день) на {CALORIES_AMOUNT} ккал/день
- Сделай упор на белок, крупы, овощи, фрукты, молочку, масла
- Используй универсальные позиции без привязки к брендам

Поля каждой позиции (строго): {json.dumps(RESPONSE_FIELDS, ensure_ascii=False)}

Формат ответа (строго по схеме — подставить значения вместо null):
{json.dumps(RESPONSE_FORMAT, ensure_ascii=False, indent=2)}
"""
