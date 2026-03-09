import logging

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from receptor.core.errors import EntityNotFoundError
from receptor.telegram_bot.services_factory import build_services
from receptor.telegram_bot.user_resolver import get_telegram_user

logger = logging.getLogger(__name__)


class ServicesMiddleware(BaseMiddleware):
    def __init__(self, ai_client, payments_http_client):
        self._ai_client = ai_client
        self._payments_http_client = payments_http_client

    async def __call__(self, handler, event, data):
        (
            session,
            user_service,
            menu_service,
            payment_service,
            menu_pdf_service,
        ) = await build_services(
            ai_client=self._ai_client,
            payments_http_client=self._payments_http_client,
        )

        try:
            data["user_service"] = user_service
            data["menu_service"] = menu_service
            data["payment_service"] = payment_service
            data["menu_pdf_service"] = menu_pdf_service
            return await handler(event, data)
        finally:
            await session.close()


class UserMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_service = data["user_service"]
        data["user"] = None

        tg_user = getattr(event, "from_user", None)

        if isinstance(event, Message):
            logger.info("Incoming message text=%r", event.text)
        elif isinstance(event, CallbackQuery):
            logger.info("Incoming callback data=%r", event.data)

        logger.info(
            "UserMiddleware: tg_user=%s", None if tg_user is None else tg_user.id
        )

        if tg_user is not None:
            try:
                user = await get_telegram_user(
                    user_service=user_service,
                    telegram_user_id=tg_user.id,
                )
                data["user"] = user
                logger.info(
                    "UserMiddleware: user found user_id=%s tg_id=%s",
                    user.id,
                    tg_user.id,
                )
            except EntityNotFoundError:
                logger.info("UserMiddleware: user not found tg_id=%s", tg_user.id)

        return await handler(event, data)


class RequireUserMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = data.get("user")

        logger.info(
            "RequireUserMiddleware: user=%s",
            "None" if user is None else user.id,
        )

        if user is None:
            logger.info("RequireUserMiddleware: blocked request")

            if isinstance(event, Message):
                await event.answer("Сначала нажми /start, чтобы зарегистрироваться.")
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "Сначала нажми /start, чтобы зарегистрироваться.",
                    show_alert=True,
                )
            return

        logger.info("RequireUserMiddleware: passed")
        return await handler(event, data)
