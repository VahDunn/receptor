import logging

from aiogram import Router
from aiogram.types import ErrorEvent

from receptor.core.errors import (
    EntityNotFoundError,
    InsufficientFundsError,
    ServiceError,
    ValidationError,
)

logger = logging.getLogger(__name__)
router = Router()


@router.errors()
async def errors_handler(event: ErrorEvent) -> bool:
    error = event.exception
    update = event.update

    message = update.message
    callback = update.callback_query
    target_message = message or (callback.message if callback else None)

    if callback:
        try:
            await callback.answer()
        except Exception:
            pass

    match error:
        case InsufficientFundsError():
            text = "Недостаточно средств для выполнения операции."

        case ValidationError():
            text = f"Некорректные данные: {error}"

        case EntityNotFoundError():
            text = "Не удалось найти запрошенные данные."

        case ServiceError():
            text = f"Не удалось выполнить команду: {error}"

        case _:
            logger.exception("Unhandled telegram bot error")
            text = "Произошла внутренняя ошибка. Пожалуйста, попробуйте позже."

    if target_message:
        await target_message.answer(text)

    return True
