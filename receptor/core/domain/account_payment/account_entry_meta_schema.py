from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from receptor.core.domain.account_payment.account_entry_meta_kind import (
    AccountEntryMetaKind,
)


class MetaBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

class TopupMeta(MetaBase):
    kind: Literal[AccountEntryMetaKind.TOPUP]
    provider: str
    external_payment_id: str

class ChargeMenuGenerationMeta(MetaBase):
    kind: Literal[AccountEntryMetaKind.MENU_GENERATION]
    menu_id: int
    tariff_code: str | None = None
    request_id: str | None = None

class RefundMeta(MetaBase):
    kind: Literal[AccountEntryMetaKind.REFUND]
    reason: str | None = None
    original_operation_key: str | None = None

AccountEntryMeta = Annotated[
    TopupMeta | ChargeMenuGenerationMeta | RefundMeta,
    Field(discriminator="kind"),
]