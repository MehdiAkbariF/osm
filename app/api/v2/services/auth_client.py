import httpx


AUTH_BASE_URL = "http://localhost:8001"  # سرویس auth جدا


async def get_user(user_id: int):
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.get(f"{AUTH_BASE_URL}/users/{user_id}")

        if r.status_code != 200:
            return None

        return r.json()