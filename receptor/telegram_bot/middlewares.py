from receptor.telegram_bot.services_factory import build_services


class ServicesMiddleware:
    def __init__(self, ai_client, payments_http_client):
        self._ai_client = ai_client
        self._payments_http_client = payments_http_client

    async def __call__(self, handler, event, data):
        session, user_service, menu_service, payment_service = await build_services(
            ai_client=self._ai_client,
            payments_http_client=self._payments_http_client,
        )

        try:
            data["user_service"] = user_service
            data["menu_service"] = menu_service
            data["payment_service"] = payment_service
            return await handler(event, data)
        finally:
            await session.close()