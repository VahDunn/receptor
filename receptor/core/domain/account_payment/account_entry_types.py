from enum import StrEnum


class AccountEntryType(StrEnum):
    CREDIT = "CREDIT"  # + деньги
    DEBIT = "DEBIT"     # - деньги