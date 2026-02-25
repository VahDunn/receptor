from enum import Enum


class Unit(str, Enum):
    g = "g"
    kg = "kg"
    ml = "ml"
    l = "l"
    pcs = "pcs"


UNITS = [u.value for u in Unit]
