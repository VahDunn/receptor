from enum import StrEnum


class Unit(StrEnum):
    g = "g"
    kg = "kg"
    ml = "ml"
    l = "l"  # noqa: E741
    pcs = "pcs"


UNITS = [u.value for u in Unit]
