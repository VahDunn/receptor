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

    logger.exception("Telegram bot error: %s", error)

    message = None
    if update.message:
        message = update.message
    elif update.callback_query:
        message = update.callback_query.message

    if message is None:
        return True

    if isinstance(error, InsufficientFundsError):
        await message.answer("Недостаточно средств для выполнения операции.")
        return True

    if isinstance(error, ValidationError):
        await message.answer(f"Некорректные данные: {error}")
        return True

    if isinstance(error, EntityNotFoundError):
        await message.answer("Нужные данные не найдены.")
        return True

    if isinstance(error, ServiceError):
        await message.answer(f"Не удалось выполнить команду: {error}")
        return True

    await message.answer("Произошла внутренняя ошибка. Попробуй ещё раз позже.")
    return True