# c:\Users\Raven\OSM\app\api\v2\services\search_service.py
"""
search_service.py — نسخه فوق‌حرفه‌ای v3 (اصلاح شده و بدون خطای اپراتور)
PostGIS Full-Text + Fuzzy Search | Iran Map
============================================
"""

from __future__ import annotations

import asyncio
import hashlib
import re
import time
import unicodedata
from dataclasses import dataclass
from typing import Any

import asyncpg
import structlog

# ─────────────────────────────────────────────
# پیکربندی دیتابیس
# ─────────────────────────────────────────────

DB_DSN = "postgresql://map_admin:map_secure_pass@localhost:5433/iran_map"

POOL_MIN_SIZE = 2
POOL_MAX_SIZE = 10
POOL_COMMAND_TIMEOUT = 10.0

IRAN_CENTER_LAT = 32.4
IRAN_CENTER_LON = 53.7

# شعاع dedup مختصاتی (درجه ≈ ۵۰ متر)
DEDUP_GRID_DEG = 0.0005

MAX_CANDIDATES = 60   # قبل از dedup و رتبه‌بندی
MAX_RESULTS    = 10   # خروجی نهایی

# ─────────────────────────────────────────────
# Logging ساختاریافته
# ─────────────────────────────────────────────

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.BoundLogger,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)
log = structlog.get_logger("search_service")

# ─────────────────────────────────────────────
# Connection Pool بهینه asyncpg
# ─────────────────────────────────────────────

_pool: asyncpg.Pool | None = None
_pool_lock = asyncio.Lock()


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is not None:
        return _pool
    async with _pool_lock:
        if _pool is None:
            _pool = await asyncpg.create_pool(
                dsn=DB_DSN,
                min_size=POOL_MIN_SIZE,
                max_size=POOL_MAX_SIZE,
                command_timeout=POOL_COMMAND_TIMEOUT,
            )
            log.info("search_pool_created")
    return _pool

# ─────────────────────────────────────────────
# لایه‌های ترجمه تگ‌های OSM ایران
# ─────────────────────────────────────────────

_AMENITY_FA: dict[str, str] = {
    "hospital": "بیمارستان",
    "clinic": "درمانگاه",
    "pharmacy": "داروخانه",
    "doctors": "مطب پزشک",
    "dentist": "مطب دندانپزشک",
    "restaurant": "رستوران",
    "cafe": "کافه",
    "fast_food": "فست‌فود",
    "bank": "بانک",
    "atm": "عابربانک",
    "fuel": "پمپ بنزین",
    "school": "مدرسه",
    "kindergarten": "مهدکودک",
    "university": "دانشگاه",
    "college": "دانشکده",
    "library": "کتابخانه",
    "parking": "پارکینگ",
    "hotel": "هتل",
    "mosque": "مسجد",
    "place_of_worship": "مکان مذهبی",
    "bus_station": "پایانه اتوبوس",
    "bus_stop": "ایستگاه اتوبوس",
    "subway_entrance": "ورودی مترو",
    "taxi": "ایستگاه تاکسی",
    "police": "کلانتری",
    "fire_station": "آتش‌نشانی",
    "post_office": "اداره پست",
    "townhall": "شهرداری",
    "theatre": "تئاتر",
    "cinema": "سینما",
    "community_centre": "خانه فرهنگ",
    "sports_centre": "مرکز ورزشی",
    "swimming_pool": "استخر",
    "park": "بوستان",
}

_SHOP_FA: dict[str, str] = {
    "supermarket": "سوپرمارکت",
    "convenience": "هایپرمارکت",
    "bakery": "نانوایی",
    "butcher": "قصابی",
    "greengrocer": "میوه‌فروشی",
    "mall": "مرکز خرید",
    "department_store": "فروشگاه بزرگ",
    "clothes": "فروشگاه پوشاک",
    "electronics": "فروشگاه لوازم الکترونیک",
    "mobile_phone": "فروشگاه موبایل",
    "car_repair": "تعمیرگاه خودرو",
    "car_parts": "لوازم یدکی",
    "hairdresser": "آرایشگاه",
    "optician": "عینک‌سازی",
    "jewelry": "جواهرفروشی",
    "books": "کتاب‌فروشی",
}

_TOURISM_FA: dict[str, str] = {
    "hotel": "هتل",
    "hostel": "مهمانپذیر",
    "motel": "متل",
    "museum": "موزه",
    "attraction": "جاذبه گردشگری",
    "viewpoint": "دیدگاه",
    "information": "مرکز اطلاعات گردشگری",
}

_PLACE_FA: dict[str, str] = {
    "city": "کلان‌شهر",
    "town": "شهر",
    "village": "روستا",
    "hamlet": "دهکده",
    "suburb": "محله",
    "quarter": "محله",
    "neighbourhood": "محله",
    "district": "منطقه",
    "county": "شهرستان",
    "state": "استان",
    "country": "کشور",
}

_PLACE_WEIGHT: dict[str, float] = {
    "country": 1.0,
    "state": 0.95,
    "county": 0.90,
    "city": 0.88,
    "town": 0.82,
    "district": 0.75,
    "suburb": 0.65,
    "quarter": 0.60,
    "neighbourhood": 0.55,
    "village": 0.50,
    "hamlet": 0.40,
}

_HIGHWAY_WEIGHT: dict[str, float] = {
    "motorway": 0.85,
    "trunk": 0.80,
    "primary": 0.72,
    "secondary": 0.65,
    "tertiary": 0.55,
    "residential": 0.40,
    "service": 0.25,
    "unclassified": 0.20,
}

_AMENITY_WEIGHT: dict[str, float] = {
    "hospital": 0.75,
    "university": 0.75,
    "bus_station": 0.70,
    "subway_entrance": 0.70,
    "townhall": 0.68,
    "school": 0.60,
    "bank": 0.55,
    "mosque": 0.55,
    "pharmacy": 0.50,
    "fuel": 0.45,
    "restaurant": 0.40,
    "cafe": 0.35,
    "parking": 0.30,
}


def translate_tag(amenity: str, shop: str, tourism: str, highway: str, place: str) -> tuple[str, float]:
    if place:
        return _PLACE_FA.get(place, place), _PLACE_WEIGHT.get(place, 0.45)
    if amenity:
        return _AMENITY_FA.get(amenity, amenity), _AMENITY_WEIGHT.get(amenity, 0.40)
    if shop:
        label = _SHOP_FA.get(shop, shop)
        return f"فروشگاه {label}", 0.38
    if tourism:
        return _TOURISM_FA.get(tourism, tourism), 0.50
    if highway:
        return "معبر", _HIGHWAY_WEIGHT.get(highway, 0.25)
    return "", 0.30

# ─────────────────────────────────────────────
# پاکسازی متون فارسی
# ─────────────────────────────────────────────

_RE_PROVINCE  = re.compile(r"^استان\s+")
_RE_COUNTY    = re.compile(r"^شهرستان\s+")
_RE_DISTRICT  = re.compile(r"^(بخش\s+مرکزی|بخش|منطقه)\s+")
_RE_SUBURB    = re.compile(r"^(محله|ناحیه)\s+")
_RE_MULTISPACE = re.compile(r"\s{2,}")


def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("ي", "ی").replace("ك", "ک").replace("‌", "")
    return _RE_MULTISPACE.sub(" ", text).strip().lower()


def clean_boundary(text: str, pattern: re.Pattern) -> str:
    return pattern.sub("", text).strip() if text else ""

# ─────────────────────────────────────────────
# آدرس‌ساز سلسله‌مراتب ایرانی
# ─────────────────────────────────────────────

def build_address(row: dict[str, Any]) -> str:
    name = (row.get("name") or "").strip() or "مکان بدون نام"

    province = clean_boundary(row.get("province") or "", _RE_PROVINCE)
    county   = clean_boundary(row.get("county") or "", _RE_COUNTY)
    district = clean_boundary(row.get("district") or "", _RE_DISTRICT)
    suburb   = clean_boundary(row.get("suburb") or "", _RE_SUBURB)
    street   = (row.get("street") or "").strip()

    poi_fa, _ = translate_tag(
        row.get("amenity") or "",
        row.get("shop") or "",
        row.get("tourism") or "",
        row.get("highway") or "",
        row.get("place") or "",
    )

    display_name = name
    if poi_fa and normalize_text(poi_fa) not in normalize_text(name):
        display_name = f"{poi_fa} {name}"

    addr_parts: list[str] = []
    if province:
        addr_parts.append(province)
    if county and county != province and county != name:
        addr_parts.append(county)
    if district and district not in (county, name):
        if district.strip().lower() not in ("مرکزی", "مركزي"):
            addr_parts.append(district)
    if suburb and suburb not in addr_parts and suburb != name:
        addr_parts.append(suburb)
    if street and street != name:
        addr_parts.append(street)

    if addr_parts:
        return f"{display_name} ({', '.join(addr_parts)})"

    geo_label = {"point": "مکان", "line": "معبر", "polygon": "منطقه"}.get(
        row.get("source_type", "point"), "مکان"
    )
    return f"{display_name} ({geo_label})"

# ─────────────────────────────────────────────
# سیستم رتبه‌بندی پیشرفته (Fuzzy Match Scoring)
# ─────────────────────────────────────────────

def score_result(
    row: dict[str, Any],
    query_tokens: list[str],
    trgm_score: float,
) -> float:
    _, type_weight = translate_tag(
        row.get("amenity") or "",
        row.get("shop") or "",
        row.get("tourism") or "",
        row.get("highway") or "",
        row.get("place") or "",
    )

    display = normalize_text(row.get("display_name") or "")
    addr    = normalize_text(
        (row.get("province") or "") + " " +
        (row.get("county") or "") + " " +
        (row.get("district") or "")
    )
    combined_text = f"{display} {addr}"
    matched = sum(
        1 for t in query_tokens
        if normalize_text(t) in combined_text
    )
    token_ratio = matched / max(len(query_tokens), 1)

    lat = row.get("lat") or 32.4
    lon = row.get("lon") or 53.7
    dist_deg = ((lat - IRAN_CENTER_LAT) ** 2 + (lon - IRAN_CENTER_LON) ** 2) ** 0.5
    proximity = max(0.0, 1.0 - dist_deg / 25.0)

    score = (
        trgm_score   * 35 +
        type_weight  * 30 +
        token_ratio  * 25 +
        proximity    * 10
    )
    return round(score, 3)

# ─────────────────────────────────────────────
# کوئری بهینه‌سازی شده با تکنیک تأخیر در پیوند فضایی و آرایه‌ها
# ─────────────────────────────────────────────

_SEARCH_SQL = """
WITH
  boundaries_prep AS (
    SELECT name, admin_level, way
    FROM planet_osm_polygon
    WHERE boundary = 'administrative'
      AND admin_level IN ('4','6','8','10','11')
      AND name IS NOT NULL
  ),

  pts AS (
    SELECT
      name,
      tags -> 'place'   AS place,
      tags -> 'amenity'  AS amenity,
      tags -> 'shop'     AS shop,
      tags -> 'tourism'  AS tourism,
      tags -> 'highway'  AS highway,
      tags -> 'addr:suburb'  AS suburb,
      tags -> 'addr:street'  AS street,
      NULL::text         AS landuse,
      way,
      'point'            AS source_type,
      similarity(name, $1) AS score
    FROM planet_osm_point
    WHERE name IS NOT NULL
      AND name % ANY($2) -- 🟢 اصلاح شد: استفاده از تک درصد استاندارد برای ایندکس GIN
      AND similarity(name, $1) > 0.12
  ),

  lns AS (
    SELECT
      name,
      NULL              AS place,
      NULL              AS amenity,
      NULL              AS shop,
      NULL              AS tourism,
      highway,
      NULL              AS suburb,
      NULL              AS street,
      NULL              AS landuse,
      ST_Centroid(way)  AS way,
      'line'            AS source_type,
      similarity(name, $1) AS score
    FROM planet_osm_line
    WHERE name IS NOT NULL
      AND name % ANY($2) -- 🟢 اصلاح شد: استفاده از تک درصد استاندارد برای ایندکس GIN
      AND highway IS NOT NULL
      AND similarity(name, $1) > 0.12
  ),

  polys AS (
    SELECT
      name,
      tags -> 'place'   AS place,
      amenity,
      shop,
      tourism,
      NULL              AS highway,
      tags -> 'addr:suburb' AS suburb,
      tags -> 'addr:street' AS street,
      landuse,
      ST_Centroid(way)  AS way,
      'polygon'         AS source_type,
      similarity(name, $1) AS score
    FROM planet_osm_polygon
    WHERE name IS NOT NULL
      AND name % ANY($2) -- 🟢 اصلاح شد: استفاده از تک درصد استاندارد برای ایندکس GIN
      AND boundary IS DISTINCT FROM 'administrative'
      AND similarity(name, $1) > 0.12
  ),

  candidates AS (
    SELECT * FROM pts
    UNION ALL
    SELECT * FROM lns
    UNION ALL
    SELECT * FROM polys
    ORDER BY score DESC
    LIMIT $3
  )

SELECT
  c.name,
  c.place,
  c.amenity,
  c.shop,
  c.tourism,
  c.highway,
  c.suburb,
  c.street,
  c.source_type,
  c.score,
  ST_Y(ST_Transform(c.way, 4326)) AS lat,
  ST_X(ST_Transform(c.way, 4326)) AS lon,

  -- اجرای ساب‌کوئری‌های فضایی صرفاً برای کاندیداهای نهایی فیلتر شده (سرعت نور)
  (SELECT b.name FROM boundaries_prep b
   WHERE b.admin_level = '4' AND ST_Contains(b.way, c.way)
   LIMIT 1) AS province,

  (SELECT b.name FROM boundaries_prep b
   WHERE b.admin_level = '6' AND ST_Contains(b.way, c.way)
   LIMIT 1) AS county,

  (SELECT b.name FROM boundaries_prep b
   WHERE b.admin_level = '8' AND ST_Contains(b.way, c.way)
   LIMIT 1) AS district

FROM candidates c;
"""

# ─────────────────────────────────────────────
# سیستم حذف رکوردهای تکراری چندسطحی (Dedup)
# ─────────────────────────────────────────────

def _coord_key(lat: float, lon: float) -> str:
    """grid ۱۱۰ متری برای فیلتر نقاط همپوشان فیزیکی"""
    glat = round(lat / 0.001) * 0.001
    glon = round(lon / 0.001) * 0.001
    return f"{glat:.3f},{glon:.3f}"


def _name_key(name: str, place: str, amenity: str) -> str:
    return hashlib.md5((normalize_text(name) + "|" + (place or "") + "|" + (amenity or "")).encode()).hexdigest()


def dedup_results(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen_coords: set[str] = set()
    name_best: dict[str, dict] = {}
    seen_addresses: set[str] = set() # 🟢 اضافه شدن فیلتر اسامی همسان مجاور

    for row in rows:
        lat = row.get("lat") or 0.0
        lon = row.get("lon") or 0.0
        ck = _coord_key(lat, lon)
        nk = _name_key(
            row.get("name") or "",
            row.get("place") or "",
            row.get("amenity") or "",
        )
        addr_name = row.get("display_name")

        if ck in seen_coords or addr_name in seen_addresses:
            continue
        seen_coords.add(ck)
        seen_addresses.add(addr_name)

        existing = name_best.get(nk)
        if existing is None or row.get("final_score", 0) > existing.get("final_score", 0):
            name_best[nk] = row

    return list(name_best.values())

# ─────────────────────────────────────────────
# تابع اصلی جستجو
# ─────────────────────────────────────────────

async def search(query: str, limit: int = MAX_RESULTS) -> list[dict[str, Any]]:
    t0 = time.perf_counter()

    clean_query = str(query).strip()
    if len(clean_query) < 2:
        return []

    # خرد کردن کلمات جستجو به صورت آرایه متنی برای انتقال به ANY در دیتابیس
    query_tokens = [t for t in clean_query.split() if len(t) >= 2]
    if not query_tokens:
        return []

    pool = await get_pool()
    try:
        async with pool.acquire() as conn:
            # 🟢 انتقال صحیح آرایه متنی پایتون به صورت مستقیم به دیتابیس بدون هیچ ارور نگارشی
            rows = await conn.fetch(_SEARCH_SQL, clean_query, query_tokens, MAX_CANDIDATES)
    except asyncpg.PostgresError as e:
        log.error("search_db_error", query=query, error=str(e))
        return []
    except asyncio.TimeoutError:
        log.warning("search_timeout", query=query)
        return []

    processed: list[dict[str, Any]] = []
    for r in rows:
        row = dict(r)

        # ساخت آدرس دقیق
        row["display_name"] = build_address(row)

        poi_fa, _ = translate_tag(
            row.get("amenity") or "",
            row.get("shop") or "",
            row.get("tourism") or "",
            row.get("highway") or "",
            row.get("place") or "",
        )
        row["place_type"] = poi_fa or None

        # امتیاز نهایی
        row["final_score"] = score_result(row, query_tokens, float(row.get("score") or 0))

        processed.append(row)

    # فیلتر تکراری‌ها
    unique = dedup_results(processed)

    # مرتب‌سازی بر اساس برترین امتیاز ترکیبی حاصل شده
    unique.sort(key=lambda x: x["final_score"], reverse=True)
    top = unique[:limit]

    elapsed = (time.perf_counter() - t0) * 1000
    log.info(
        "search_done",
        query=query,
        raw=len(rows),
        after_dedup=len(unique),
        returned=len(top),
        elapsed_ms=round(elapsed, 1),
    )

    return [
        {
            "display_name": item["display_name"],
            "lat": round(item["lat"], 7),
            "lon": round(item["lon"], 7),
            "score": item["final_score"],
            "place_type": item.get("place_type"),
        }
        for item in top
    ]