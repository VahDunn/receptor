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
Сгенерируй 30–45 рецептов для типичного недельного меню (завтрак/обед/ужин).
Рецепты универсальные без брендов, упор на белок/крупы/овощи/фрукты/молочку/масла.

Калорийность и недельная балансировка:
- Целевой диапазон калорий в день: от __CALORIES_MIN__ до __CALORIES_MAX__ ккал.
- Разброс в один день от целевого среднего должен быть не более 150 ккал в любую сторону.
  Определи target_avg = (calories_min + calories_max) / 2.
  Тогда дневная цель: [target_avg - 150, target_avg + 150], но при этом НЕ выходи за [calories_min, calories_max].
- Старайся, чтобы средняя калорийность по неделе была максимально близка к target_avg.
- Предпочитай значения ближе к target_avg, а не к краям диапазона.
- Рецепты должны позволять собрать день (завтрак+обед+ужин) в указанный коридор.
  Для этого делай разные “веса” блюд:
  - завтрак обычно 20–30% дневных ккал,
  - обед 35–45%,
  - ужин 25–35%.
  (Это ориентиры; главное — чтобы суммарно дневные ккал укладывались в коридор.)

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
    "version": null,
    "calories_min": null,
    "calories_max": null,
    "target_avg": null,
    "max_daily_deviation": 150
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
{"products": __PRODUCTS_JSON__, "calories_min": __CALORIES_MIN__, "calories_max": __CALORIES_MAX__}
"""


def build_recipes_prompt(
    products_json: str, calories_min: int, calories_max: int
) -> str:
    if not isinstance(calories_min, int) or not isinstance(calories_max, int):
        raise TypeError("calories_min и calories_max должны быть int")
    if calories_min <= 0 or calories_max <= 0:
        raise ValueError("calories_min и calories_max должны быть > 0")
    if calories_min > calories_max:
        raise ValueError("calories_min не может быть больше calories_max")

    return (
        RECIPES_FROM_PRODUCTS_PROMPT_TEMPLATE.replace(
            "__UNITS_JSON__", json.dumps(UNITS, ensure_ascii=False)
        )
        .replace("__PRODUCTS_JSON__", products_json)
        .replace("__CALORIES_MIN__", str(calories_min))
        .replace("__CALORIES_MAX__", str(calories_max))
    )
