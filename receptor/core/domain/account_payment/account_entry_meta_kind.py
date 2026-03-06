from enum import StrEnum


class AccountEntryMetaKind(StrEnum):
    TOPUP = "topup"
    MENU_GENERATION = "menu_generation"
    REFUND = "refund"
