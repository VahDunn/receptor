import json

from receptor.external_services.ai.prompts.products_prompt import UNITS

RECIPES_FROM_PRODUCTS_PROMPT_TEMPLATE = """
Жёсткие правила:
- Верни ТОЛЬКО валидный JSON. Никакого текста вне JSON.
- Вывод начинается с { и заканчивается }.
- Все ключи в двойных кавычках.
- Не добавляй и не удаляй ключи схемы.
- Используй ТОЛЬКО продукты из входного списка products. Никаких "соль/перец/специи" если их нет во входе.
- Каждый ингредиент обязан ссылаться на продукт: "product_id" (если есть во входе), иначе "product_name" (строго как во входе).
- amount реалистичный, unit строго из списка: __UNITS_JSON__.
- calories_total — целое число, посчитай из calories_per_unit и amount.

Правила calories_per_unit во входе:
- если unit продукта == "g": calories_per_unit = ккал на 100 g
- если unit продукта == "kg": calories_per_unit = ккал на 1 kg
- если unit продукта == "ml": calories_per_unit = ккал на 100 ml
- если unit продукта == "l": calories_per_unit = ккал на 1 l
- если unit продукта == "pcs": calories_per_unit = ккал на 1 штуку

Правила расчёта калорий ингредиента:
- если unit ингредиента == "g": calories = calories_per_unit * amount / 100
- если unit == "kg": calories = calories_per_unit * amount
- если unit == "ml": calories = calories_per_unit * amount / 100
- если unit == "l": calories = calories_per_unit * amount
- если unit == "pcs": calories = calories_per_unit * amount
- calories_total = сумма calories, округли до целого

Цель:
Сгенерируй 30–45 рецептов для типичного недельного меню (завтрак/обед/ужин) 1500–3000 ккал/день.
Рецепты универсальные без брендов, упор на белок/крупы/овощи/фрукты/молочку/масла.

Требования:
- 30–45 рецептов
- 3–10 ингредиентов в рецепте
- Разнообразие: каши, салаты, супы, запеканки, блюда с курицей/рыбой/яйцами/творогом/крупами
- Минимизируй повторы

Схема ответа (строго):
{
  "meta": {
    "store": "Перекрёсток",
    "city": "Москва",
    "version": null
  },
  "recipes": [
    {
      "name": null,
      "meal_type": null,
      "servings": null,
      "ingredients": [
        {
          "product_id": null,
          "product_name": null,
          "amount": null,
          "unit": null
        }
      ],
      "instructions": [],
      "calories_total": null,
      "estimated_cost_rub": null
    }
  ]
}

Входные данные:
{"products": __PRODUCTS_JSON__}
"""


def build_recipes_prompt(products_json: str) -> str:
    return RECIPES_FROM_PRODUCTS_PROMPT_TEMPLATE.replace(
        "__UNITS_JSON__", json.dumps(UNITS, ensure_ascii=False)
    ).replace("__PRODUCTS_JSON__", products_json)
