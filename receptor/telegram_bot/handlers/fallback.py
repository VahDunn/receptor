import logging

from aiogram import Router
from aiogram.types import Message

logger = logging.getLogger(__name__)
router = Router()


@router.message()
async def fallback_handler(message: Message) -> None:
    logger.info(
        "UNHANDLED MESSAGE text=%r user_id=%s",
        message.text,
        message.from_user.id if message.from_user else None,
    )
    await message.answer(
        "Не удалось распознать команду. Пожалуйста, выберите действие из меню."
    )
