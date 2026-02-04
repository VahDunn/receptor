import aiohttp


class ChadAIClient:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        api_key: str,
        url: str,
    ):
        self.api_key = api_key
        self.session = session
        self.url = url

    async def send_prompt(self, prompt_text: str) -> dict:
        request_json = {
            "message": prompt_text,
            "api_key": self.api_key,
        }

        timeout = aiohttp.ClientTimeout(total=60)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(self.url, json=request_json) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise RuntimeError(f"HTTP {resp.status}: {text}")

                data = await resp.json(content_type=None)

        return data
