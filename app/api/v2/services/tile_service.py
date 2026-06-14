from app.api.v2.core.config import settings


def get_tile_url(z: int, x: int, y: int):
    return f"{settings.MARTIN_URL}/osm/{z}/{x}/{y}"