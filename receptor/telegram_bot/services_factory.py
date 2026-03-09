from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from receptor.config import settings
from receptor.db.engine import engine
from receptor.external_services.ai.clients.chad_ai_client import ChadAIClient
from receptor.external_services.ai.parsers.default_parser import DefaultJsonAiParser
from receptor.external_services.ai.response_schemas.ai_menu_schema import WeeklyMenuAiResponseSchema
from receptor.external_services.ai.response_schemas.ai_products_schema import ProductsAiResponseSchema
from receptor.repositories import UserRepository, MenuRepository, PaymentRepository, ProductRepository
from receptor.services import UserService, MenuService, PaymentService, AIService, ProductsService
from receptor.external_services.payments.yoo_kassa_provider import YooKassaProvider


session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def build_services(
    *,
    ai_client: ChadAIClient,
    payments_http_client,
) -> tuple[
    AsyncSession,
    UserService,
    MenuService,
    PaymentService,
]:
    session: AsyncSession = session_factory()

    user_repo = UserRepository(session)
    product_repo = ProductRepository(session)
    menu_repo = MenuRepository(session)
    payment_repo = PaymentRepository(session)

    payment_provider = YooKassaProvider(
        shop_id=settings.yookassa_shop_id,
        secret_key=settings.yookassa_secret_key,
        client=payments_http_client,
    )

    product_parser = DefaultJsonAiParser(
        schema=ProductsAiResponseSchema,
        strict_json_only=True,
    )
    menu_parser = DefaultJsonAiParser(
        schema=WeeklyMenuAiResponseSchema,
        strict_json_only=True,
    )

    ai_service = AIService(ai_client)
    user_service = UserService(user_repo)
    payment_service = PaymentService(
        provider=payment_provider,
        repo=payment_repo,
    )

    products_service = ProductsService(
        product_repo,
        ai_service,
        parser=product_parser,
    )
    menu_service = MenuService(
        products_service=products_service,
        ai_service=ai_service,
        parser=menu_parser,
        repo=menu_repo,
        payment_service=payment_service,
    )

    return session, user_service, menu_service, payment_service