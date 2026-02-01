from receptor.external_services.ai.abstract_ai_client import AbstractAIClient


class ChadAIClient(AbstractAIClient):


    async def send_prompt(self, prompt_text: str) -> dict:
        request_json = {
            "message": prompt_text,
            "api_key": CHAD_API_KEY,
        }

        timeout = aiohttp.ClientTimeout(total=60)  # можно увеличить при длинных ответах

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(URL, json=request_json) as resp:
                # 1) HTTP-ошибки
                if resp.status != 200:
                    text = await resp.text()
                    raise RuntimeError(f"HTTP {resp.status}: {text}")

                # 2) Парсим JSON
                data = await resp.json(content_type=None)

        # 3) Логика как у тебя
        if not data.get("is_success"):
            raise RuntimeError(f"API error: {data.get('error_message')}")

        return data
