import httpx
from app.core.config import settings

class TileService:
    def __init__(self):
        self.base_url = settings.MARTIN_URL
        # ایجاد یک کلاینت ناهم‌گام دائمی با قابلیت Connection Pooling برای سرعت بالا
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=10.0)

    async def get_vector_tile(self, table: str, z: int, x: int, y: int) -> tuple[bytes, dict]:
        """
        دریافت کاملاً ناهم‌گام (Async) بایت‌های تایل از مارتین بدون قفل کردن صف پردازش
        """
        url = f"/{table}/{z}/{x}/{y}"
        try:
            # ارسال درخواست ناهم‌گام با متد await
            response = await self.client.get(url)
            if response.status_code == 200:
                return response.content, dict(response.headers)
            return b"", {}
        except httpx.HTTPError:
            return b"", {}

tile_service = TileService()