from enum import StrEnum


class ProductCategory(StrEnum):
    protein_meat = "protein_meat"
    protein_fish = "protein_fish"
    protein_eggs = "protein_eggs"
    protein_dairy = "protein_dairy"
    protein_plant = "protein_plant"

    carbs_grains = "carbs_grains"
    carbs_bread = "carbs_bread"
    carbs_pasta = "carbs_pasta"

    veg_fresh = "veg_fresh"
    veg_frozen = "veg_frozen"
    fruit = "fruit"

    fats_oils = "fats_oils"
    nuts_seeds = "nuts_seeds"

    canned = "canned"
    sauces = "sauces"
    spices = "spices"
    drinks = "drinks"
    other = "other"

    @property
    def code(self) -> str:
        return self.value

    @property
    def name_ru(self) -> str:
        return _NAME_RU[self]


_NAME_RU = {
    ProductCategory.protein_meat: "Мясо",
    ProductCategory.protein_fish: "Рыба и морепродукты",
    ProductCategory.protein_eggs: "Яйца",
    ProductCategory.protein_dairy: "Молочные продукты (белок)",
    ProductCategory.protein_plant: "Растительный белок",
    ProductCategory.carbs_grains: "Крупы и злаки",
    ProductCategory.carbs_bread: "Хлеб",
    ProductCategory.carbs_pasta: "Макароны",
    ProductCategory.veg_fresh: "Овощи свежие",
    ProductCategory.veg_frozen: "Овощи замороженные",
    ProductCategory.fruit: "Фрукты и ягоды",
    ProductCategory.fats_oils: "Масла и жиры",
    ProductCategory.nuts_seeds: "Орехи и семечки",
    ProductCategory.canned: "Консервы",
    ProductCategory.sauces: "Соусы",
    ProductCategory.spices: "Специи",
    ProductCategory.drinks: "Напитки",
    ProductCategory.other: "Прочее",
}
