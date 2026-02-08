from enum import StrEnum


class ProductTypeCode(StrEnum):
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
    ProductTypeCode.protein_meat: "Мясо",
    ProductTypeCode.protein_fish: "Рыба и морепродукты",
    ProductTypeCode.protein_eggs: "Яйца",
    ProductTypeCode.protein_dairy: "Молочные продукты (белок)",
    ProductTypeCode.protein_plant: "Растительный белок",
    ProductTypeCode.carbs_grains: "Крупы и злаки",
    ProductTypeCode.carbs_bread: "Хлеб",
    ProductTypeCode.carbs_pasta: "Макароны",
    ProductTypeCode.veg_fresh: "Овощи свежие",
    ProductTypeCode.veg_frozen: "Овощи замороженные",
    ProductTypeCode.fruit: "Фрукты и ягоды",
    ProductTypeCode.fats_oils: "Масла и жиры",
    ProductTypeCode.nuts_seeds: "Орехи и семечки",
    ProductTypeCode.canned: "Консервы",
    ProductTypeCode.sauces: "Соусы",
    ProductTypeCode.spices: "Специи",
    ProductTypeCode.drinks: "Напитки",
    ProductTypeCode.other: "Прочее",
}
