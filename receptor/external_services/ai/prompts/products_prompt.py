import json

from receptor.core.domain.product_categories import ProductCategory
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
        "created_at": "",
        "version": "",
    },
    "items": [{field: None for field in RESPONSE_FIELDS}],
}

POSITIONS_NUMBER = 150

CALORIES_AMOUNT = 2500

PROMPT = f"""
Жёсткие правила:
- Верни ТОЛЬКО валидный JSON. Никакого текста вне JSON.
- Вывод начинается с {{ и заканчивается }}.
- Все ключи в двойных кавычках.
- Строго следуй заданной схеме, не добавляй и не удаляй ключи.
- Если информации не хватает — используй null, но не пропускай ключи.
- Позиции должны быть типовыми для Москвы и сети "Перекрёсток".
- Цель каталога: поддержать недельное меню 2500 ккал/день.
- Держи каталог в диапазоне 120–180 позиций.
- Не дублируй одинаковые товары в разных фасовках без необходимости.
- Избегай брендов, используй обобщённые названия.

Сформируй каталог продуктов для кэширования цен для магазина "Перекрёсток", город Москва.

Требования:
- Количество позиций: {POSITIONS_NUMBER}
- Каталог должен покрывать типичное недельное меню (3 приёма пищи в день) на {
    CALORIES_AMOUNT
} ккал/день
- Сделай упор на белок, крупы, овощи, фрукты, молочку, масла
- Используй универсальные позиции без привязки к брендам

Для каждой позиции укажи: {json.dumps(RESPONSE_FIELDS, ensure_ascii=False)}

Категории (строго из списка): {
    json.dumps(
        [category.code for category in ProductCategory],
        ensure_ascii=False,
    )
}

Формат ответа (строго по схеме): {
    json.dumps(RESPONSE_FORMAT, ensure_ascii=False, indent=2)
}
"""
