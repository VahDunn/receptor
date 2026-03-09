import asyncio
import logging

import httpx
from aiogram import Bot, Dispatcher

from receptor.config import settings
from receptor.external_services.ai.clients.chad_ai_client import ChadAIClient
from receptor.telegram_bot.handlers import router
from receptor.telegram_bot.middlewares import ServicesMiddleware, UserMiddleware

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    logger.info("Starting Telegram bot...")

    ai_http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(
            timeout=1200.0,
            connect=10.0,
            read=1100.0,
            write=30.0,
            pool=30.0,
        )
    )

    payments_http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(
            timeout=20.0,
            connect=5.0,
            read=15.0,
            write=10.0,
            pool=5.0,
        )
    )

    ai_client = ChadAIClient(
        client=ai_http_client,
        api_key=settings.chad_api_key,
        url=settings.chad_url,
    )

    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher()

    dp.update.middleware(
        ServicesMiddleware(
            ai_client=ai_client,
            payments_http_client=payments_http_client,
        )
    )

    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())

    dp.include_router(router)

    try:
        logger.info("Bot polling started")
        await dp.start_polling(bot)
    except Exception:
        logger.exception("Bot crashed")
        raise
    finally:
        logger.info("Shutting down bot")
        await ai_http_client.aclose()
        await payments_http_client.aclose()
        logger.info("HTTP clients closed")


if __name__ == "__main__":
    asyncio.run(main())
