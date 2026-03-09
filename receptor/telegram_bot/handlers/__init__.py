from aiogram import Router

from .user import router as user_router
from .menu import router as menu_router


router = Router()

router.include_router(user_router)
router.include_router(menu_router)