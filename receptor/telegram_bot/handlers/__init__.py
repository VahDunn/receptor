from aiogram import Router

from receptor.telegram_bot.handlers.errors import router as errors_router
from receptor.telegram_bot.handlers.fallback import router as fallback_router
from receptor.telegram_bot.handlers.menu import router as menu_router
from receptor.telegram_bot.handlers.profile import router as profile_router
from receptor.telegram_bot.handlers.start import router as start_router
from receptor.telegram_bot.middlewares import RequireUserMiddleware

router = Router()

router.include_router(errors_router)

public_router = Router()
public_router.include_router(start_router)

protected_router = Router()
protected_router.message.middleware(RequireUserMiddleware())
protected_router.callback_query.middleware(RequireUserMiddleware())

protected_router.include_router(menu_router)
protected_router.include_router(profile_router)
protected_router.include_router(fallback_router)

router.include_router(public_router)
router.include_router(protected_router)
