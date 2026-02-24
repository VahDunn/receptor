import json
from receptor.external_services.ai.prompts.products_prompt import UNITS

MENU_FROM_PRODUCTS_PROMPT_TEMPLATE = """
Жёсткие правила:
- Верни ТОЛЬКО валидный JSON. Никакого текста вне JSON.
- Ответ начинается с {{ и заканчивается }}.
- Все ключи строго в двойных кавычках.
- Не добавляй и не удаляй ключи схемы.
- Используй ТОЛЬКО продукты из входного списка products.
- Запрещено добавлять продукты, которых нет во входе.
- Запрещено добавлять "соль", "перец", "специи", "вода" если их нет во входе.
- Не используй бренды.
- Если используешь продукт — имя строго как products[].name.
- Нельзя придумывать ингредиенты.

ВАЖНО — структура блюд:
- Меню состоит из БЛЮД, но без рецептов.
- У каждого блюда есть:
    - "dish_name": краткое реалистичное название блюда (без брендов).
    - "products": массив продуктов (строго products[].name).
- НЕ добавляй инструкции приготовления.
- НЕ добавляй шаги рецепта.
- НЕ добавляй количества продуктов внутри блюд.

Пояснение по единицам измерения (units):
Во входных данных продукты имеют поле unit и calories_per_unit.
calories_per_unit — это целое число, но его смысл зависит от unit:

- если unit == "g": calories_per_unit = ккал на 100 g
- если unit == "kg": calories_per_unit = ккал на 1 kg
- если unit == "ml": calories_per_unit = ккал на 100 ml
- если unit == "l": calories_per_unit = ккал на 1 l
- если unit == "pcs": calories_per_unit = ккал на 1 штуку

Калорийность (обязательно):
- Во входе есть calorie_target.min_kcal_per_day и calorie_target.max_kcal_per_day.
- Составляй меню так, чтобы оценочная калорийность КАЖДОГО дня была в диапазоне:
  [min_kcal_per_day, max_kcal_per_day].
- Допустимое отклонение: не более 200 ккал за пределы диапазона.
- Оценку делай на основе calories_per_unit и приблизительных реалистичных порций.
- Верни оценку калорийности по дням в daily_kcal_estimates (7 чисел).

Цель:
Собери недельное меню (7 дней) с 3 приёмами пищи:

- Завтрак
- Обед
- Ужин

Требования к menu_structure:

- Это массив из 7 объектов.
- Каждый объект имеет ключи:

    - "day": номер дня (1-7)
    - "breakfast": массив блюд
    - "lunch": массив блюд
    - "dinner": массив блюд

Структура блюда:

{
  "dish_name": "строка",
  "products": ["product_name_1", "product_name_2"]
}

Правила:

- В каждом приёме пищи 1–3 блюда.
- В каждом блюде 2–5 продуктов.
- Не повторяй одно и то же блюдо чаще 2 раз за неделю.
- Одна и та же каша максимум 3 раза за неделю.
- Блюда должны быть реалистичными для Москвы/Перекрёстка.
- Названия блюд короткие и понятные.

Дополнительная задача — список продуктов:

Сформируй список продуктов на всю неделю: "products_with_quantities".

Правила:

- Верни список ВСЕХ продуктов, использованных в menu_structure.
- Используй ТОЛЬКО продукты из входного списка products.
- "product_name" строго совпадает с products[].name.
- "unit" строго совпадает с products[].unit.

quantity:

- pcs → целое число
- g/ml → целое число
- kg/l → допускается дробное число

Количество должно быть реалистичным на 7 дней.

Схема ответа (строго):

{{
  "meta": {{
    "store": "Перекрёсток",
    "city": "Москва",
    "version": null
  }},
  "calorie_target": {{
    "min_kcal_per_day": null,
    "max_kcal_per_day": null
  }},
  "menu_structure": [],
  "daily_kcal_estimates": [],
  "products_with_quantities": []
}}

Требования к daily_kcal_estimates:

- массив из 7 целых чисел.
- значения должны соответствовать правилу калорийности.

Входные данные:

{{
  "products": __PRODUCTS_JSON__,
  "units": __UNITS_JSON__,
  "calorie_target": {{
    "min_kcal_per_day": __MIN_KCAL__,
    "max_kcal_per_day": __MAX_KCAL__
  }}
}}
"""


def build_menu_prompt(products_json: str, min_kcal: int, max_kcal: int) -> str:
    return (
        MENU_FROM_PRODUCTS_PROMPT_TEMPLATE.replace(
            "__UNITS_JSON__", json.dumps(UNITS, ensure_ascii=False)
        )
        .replace("__PRODUCTS_JSON__", products_json)
        .replace("__MIN_KCAL__", str(min_kcal))
        .replace("__MAX_KCAL__", str(max_kcal))
    )
