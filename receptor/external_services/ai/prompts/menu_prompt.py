import json

from receptor.core.domain.marketplaces import Marketplace
from receptor.core.domain.units import UNITS

MENU_FROM_PRODUCTS_PROMPT_TEMPLATE = """
Жёсткие правила формата:
- Верни ТОЛЬКО валидный JSON. Никакого текста вне JSON.
- Ответ начинается с { и заканчивается }.
- Все ключи строго в двойных кавычках.
- Не добавляй и не удаляй ключи схемы ответа.

Ограничения по продуктам:
- Используй ТОЛЬКО продукты из входного списка products.
- В блюдах и в products_with_quantities указывай ТОЛЬКО products[].id.
- Запрещено придумывать новые product_id.
- Запрещено выводить product_name где-либо.
- Внутри блюд запрещено использовать названия продуктов.

Блюда:
- Меню состоит из блюд без рецептов и без инструкций.
- Каждое блюдо:
  - "dish_name": короткое реалистичное название без брендов
  - "products": массив из 2..5 уникальных product_id
- В каждом приёме пищи 1..3 блюда.
- 7 дней: breakfast/lunch/dinner.
- Не повторяй одно и то же блюдо чаще 2 раз за неделю.
- Одна и та же каша максимум 3 раза за неделю.
- Блюда должны быть реалистичными для сети __STORE__.

Единицы и калории:
- В продуктах есть "unit" и "calories_per_unit".
- calories_per_unit означает:
  - g  -> ккал на 100 g
  - kg -> ккал на 1 kg
  - ml -> ккал на 100 ml
  - l  -> ккал на 1 l
  - pcs-> ккал на 1 штуку
- Во входе есть calorie_target.min_kcal_per_day и calorie_target.max_kcal_per_day.
- В ответе верни calorie_target ровно с этими числами из входа.
- daily_kcal_estimates: 7 целых чисел.
- Каждый день по калориям должен попадать в диапазон
  [min_kcal_per_day, max_kcal_per_day] с допуском не более 200 ккал.

Бюджет:
- Во входе есть money_target.weekly_budget_rub и money_target.tolerance_rub.
- weekly_cost_estimate_rub: целое число.
- weekly_cost_estimate_rub должен быть в диапазоне:
  [weekly_budget_rub - tolerance_rub, weekly_budget_rub + tolerance_rub].
- Оценку делай на основе price_rub и реалистичных порций.

Список продуктов на неделю (products_with_quantities):
- products_with_quantities должен содержать РОВНО все product_id,
  которые встречаются в menu_structure:
  - без пропусков
  - без лишних id
- quantity всегда строго > 0.
- Нельзя возвращать quantity = 0.
- Если продукт не используется в menu_structure — НЕ добавляй его.
- unit должен строго совпадать с products[].unit.
- quantity формат:
  - pcs -> целое число
  - g/ml -> целое число
  - kg/l -> допускается дробное число
- Количество должно быть реалистичным на 7 дней.

Схема ответа (строго):
{
  "meta": {
    "store": "__STORE__",
    "region": "__REGION__",
    "version": null
  },
  "calorie_target": {
    "min_kcal_per_day": 0,
    "max_kcal_per_day": 0
  },
  "menu_structure": [
    {
      "day": 1,
      "breakfast": [{"dish_name": "строка", "products": [1,2]}],
      "lunch": [{"dish_name": "строка", "products": [1,2]}],
      "dinner": [{"dish_name": "строка", "products": [1,2]}]
    }
  ],
  "daily_kcal_estimates": [0,0,0,0,0,0,0],
  "weekly_cost_estimate_rub": 0,
  "products_with_quantities": [
    {"product_id": 1, "unit": "g", "quantity": 500}
  ]
}

Входные данные:
{
  "products": __PRODUCTS_JSON__,
  "units": __UNITS_JSON__,
  "calorie_target": {
    "min_kcal_per_day": __MIN_KCAL__,
    "max_kcal_per_day": __MAX_KCAL__
  },
  "money_target": {
    "weekly_budget_rub": __MAX_MONEY__,
    "tolerance_rub": __MONEY_TOLERANCE__
  }
}
"""


def build_menu_prompt(
    products_json: str,
    min_kcal: int,
    max_kcal: int,
    marketplace: Marketplace,
    max_money_rub: int,
    money_tolerance_rub: int,
    region: str = "Москва",
) -> str:
    return (
        MENU_FROM_PRODUCTS_PROMPT_TEMPLATE.replace(
            "__UNITS_JSON__", json.dumps(UNITS, ensure_ascii=False)
        )
        .replace("__STORE__", marketplace.value)
        .replace("__PRODUCTS_JSON__", products_json)
        .replace("__MIN_KCAL__", str(min_kcal))
        .replace("__MAX_KCAL__", str(max_kcal))
        .replace("__MAX_MONEY__", str(max_money_rub))
        .replace("__MONEY_TOLERANCE__", str(money_tolerance_rub))
        .replace("__REGION__", region)
    )
