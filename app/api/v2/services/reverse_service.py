# c:\Users\Raven\OSM\app\api\v2\services\reverse_service.py
"""
Reverse Geocoder — نسخه Hybrid addr:* + Interpolation
=====================================================
روش کار:
  ۱. addr_context  : نزدیک‌ترین نقطه یا ساختمان که addr:street/quarter/suburb داره
  ۲. snapped       : نزدیک‌ترین خیابان با وزن‌دهی (با یا بدون name)
  ۳. street_chain  : زنجیره خیابان‌ها از توپولوژی OSM (تا ۴ سطح)
  ۴. interpolation : وقتی snapped بدون name بود، از addr:street جایگزین می‌کنیم
  ۵. boundaries    : مرزهای اداری با اولویت‌بندی area
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import re
import time
from dataclasses import dataclass
from typing import Any

import asyncpg
import structlog

# ─── تنظیمات ──────────────────────────────────────────────────────────────────
DB_DSN               = "postgresql://map_admin:map_secure_pass@localhost:5433/iran_map"
POOL_MIN_SIZE        = 2
POOL_MAX_SIZE        = 10
POOL_COMMAND_TIMEOUT = 8.0

CACHE_MAX_SIZE       = 4096
CACHE_TTL_SEC        = 3600
CACHE_GRID_DEG       = 0.0001

ADDR_CONTEXT_RADIUS  = 120   # شعاع جستجو برای addr_context (متر)
CHAIN_SNAP_RADIUS    = 8     # شعاع اتصال بین خیابان‌ها در زنجیره (متر)

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
log = structlog.get_logger("reverse_geocoder")


# ─── مدل خروجی ────────────────────────────────────────────────────────────────
@dataclass
class ReverseResult:
    address: str
    province: str | None        = None
    city: str | None            = None
    district: str | None        = None
    neighbourhood: str | None   = None
    street_level1: str | None   = None   # بلوار / بزرگراه
    street_level2: str | None   = None   # خیابان اصلی
    street_level3: str | None   = None   # کوچه
    street_level4: str | None   = None   # کوچه فرعی‌تر
    building_name: str | None   = None
    house_number: str | None    = None
    landmark: str | None        = None
    distance_to_street_m: float | None = None
    addr_source: str | None     = None   # osm_line | addr_interpolated
    traffic_zone: str | None    = None
    confidence: float           = 1.0
    source_type: str            = "hybrid_v1"
    cached: bool                = False
    elapsed_ms: float           = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


# ─── خطاها ────────────────────────────────────────────────────────────────────
class GeocoderError(Exception): pass
class DatabaseError(GeocoderError): pass
class NoResultError(GeocoderError): pass


# ─── connection pool ───────────────────────────────────────────────────────────
_pool: asyncpg.Pool | None = None
_pool_lock = asyncio.Lock()


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is not None:
        return _pool
    async with _pool_lock:
        if _pool is None:
            try:
                _pool = await asyncpg.create_pool(
                    dsn=DB_DSN,
                    min_size=POOL_MIN_SIZE,
                    max_size=POOL_MAX_SIZE,
                    command_timeout=POOL_COMMAND_TIMEOUT,
                )
                log.info("db_pool_created")
            except Exception as e:
                raise DatabaseError("db pool failed") from e
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


# ─── cache ────────────────────────────────────────────────────────────────────
@dataclass
class _CacheEntry:
    result: ReverseResult
    expires_at: float


class _GeoCache:
    def __init__(self, max_size: int, ttl: float) -> None:
        self._store: dict[str, _CacheEntry] = {}
        self._max_size = max_size
        self._ttl = ttl

    def _key(self, lat: float, lon: float) -> str:
        glat = round(lat / CACHE_GRID_DEG) * CACHE_GRID_DEG
        glon = round(lon / CACHE_GRID_DEG) * CACHE_GRID_DEG
        return hashlib.md5(f"{glat:.6f},{glon:.6f}".encode()).hexdigest()

    def get(self, lat: float, lon: float) -> ReverseResult | None:
        key = self._key(lat, lon)
        entry = self._store.get(key)
        if entry is None or time.monotonic() > entry.expires_at:
            if entry:
                del self._store[key]
            return None
        return entry.result

    def set(self, lat: float, lon: float, result: ReverseResult) -> None:
        if len(self._store) >= self._max_size:
            oldest = min(self._store, key=lambda k: self._store[k].expires_at)
            del self._store[oldest]
        self._store[self._key(lat, lon)] = _CacheEntry(
            result=result,
            expires_at=time.monotonic() + self._ttl,
        )


_cache = _GeoCache(max_size=CACHE_MAX_SIZE, ttl=CACHE_TTL_SEC)


# ─── regex / helpers ──────────────────────────────────────────────────────────
_EN_TO_FA     = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
_RE_PROVINCE  = re.compile(r"^استان\s+")
_RE_CITY      = re.compile(r"^(شهرستان|شهر|بخش\s+مرکزی)\s+")
_RE_TEHRAN    = re.compile(r"\s*شهر\s*تهران$")
_RE_DISTRICT  = re.compile(r"^منطقه\s+")
_RE_NUMERIC   = re.compile(r"^[\d۰-۹]{1,5}([/-][\d۰-۹]{1,4})?$")


def _fa(text: str) -> str:
    return text.translate(_EN_TO_FA) if text else ""


def _abbrev(t: str) -> str:
    if not t:
        return ""
    t = t.replace("بزرگراه شهید سلیمانی (جاده ملارد)", "بل. شهید سلیمانی")
    t = t.replace("بلوار", "بل.")
    t = t.replace("خیابان", "خ.")
    t = t.replace("کوچه", "ک.")
    t = t.replace("بن‌بست", "ب.ب")
    return t


def _valid_hn(text: str | None) -> bool:
    if not text:
        return False
    t = str(text).strip()
    if not (1 <= len(t) <= 12):
        return False
    if len(re.findall(r"[آ-ی]", t)) > 2:
        return False
    return bool(_RE_NUMERIC.match(t) or re.match(r"^\d{1,5}$", t))


def _clean_province(n: str) -> str:
    return _RE_PROVINCE.sub("", n).strip() if n else ""


def _clean_city(n: str) -> str:
    if not n:
        return ""
    n = _RE_CITY.sub("", n).strip()
    if re.search(r"\s*[-–]\s*", n):
        n = re.split(r"\s*[-–]\s*", n, 1)[-1].strip()
    return n


def _clean_district(n: str) -> str:
    n = _RE_TEHRAN.sub("", n)
    n = _RE_DISTRICT.sub("منطقهٔ ", n)
    return n.strip()


# ─── landmark prefix ──────────────────────────────────────────────────────────
_LM_MAP: list[tuple[tuple[str, ...], str]] = [
    (("mosque",),                               "جنب مسجد"),
    (("hospital", "clinic", "doctors"),         "نزدیک بیمارستان"),
    (("pharmacy",),                             "جنب داروخانه"),
    (("bank", "atm", "bureau_de_change"),       "نزدیک بانک"),
    (("school", "university", "college"),       "نزدیک مدرسه/دانشگاه"),
    (("fire_station",),                         "نزدیک آتش‌نشانی"),
    (("police",),                               "نزدیک کلانتری"),
    (("post_office",),                          "نزدیک پست"),
    (("fuel",),                                 "نزدیک پمپ بنزین"),
    (("park",),                                 "نزدیک پارک"),
    (("restaurant", "cafe", "fast_food"),       "جنب رستوران"),
    (("supermarket", "convenience", "grocery"), "جنب سوپرمارکت"),
    (("mall", "department_store", "marketplace"), "نزدیک مرکز خرید"),
]
_TOURISM_MAP = {"hotel": "جنب هتل", "museum": "نزدیک موزه", "attraction": "نزدیک جاذبه"}


def _lm_prefix(amenity: str, shop: str, tourism: str) -> str:
    for keys, prefix in _LM_MAP:
        if amenity in keys or shop in keys:
            return prefix
    return _TOURISM_MAP.get(tourism, "نزدیک")


# ─── کوئری اصلی ───────────────────────────────────────────────────────────────
_MASTER_QUERY = """
WITH
  pt AS (
    SELECT ST_Transform(ST_SetSRID(ST_MakePoint($1, $2), 4326), 3857) AS geom
  ),

  boundaries AS (
    SELECT
      p.name,
      p.admin_level,
      p.landuse,
      p.tags -> 'place'  AS place_tag,
      ST_Area(p.way)     AS area
    FROM planet_osm_polygon p, pt
    WHERE (
        p.boundary = 'administrative'
        OR p.landuse IN ('residential','commercial','retail')
        OR p.tags -> 'place' IN ('city','town','suburb','quarter','neighbourhood','village')
      )
      AND p.name IS NOT NULL
      AND ST_Contains(p.way, pt.geom)
    ORDER BY ST_Area(p.way) ASC
  ),

  -- addr_context: نزدیک‌ترین شیء با تگ addr:*
  addr_context_raw AS (
    SELECT
      COALESCE(tags -> 'addr:street', tags -> 'addr:place')  AS addr_street,
      tags -> 'addr:quarter'                                  AS addr_quarter,
      tags -> 'addr:suburb'                                   AS addr_suburb,
      tags -> 'addr:neighbourhood'                            AS addr_neighbourhood,
      tags -> 'addr:city'                                     AS addr_city,
      tags -> 'addr:housenumber'                              AS addr_hn,
      ST_Distance(pt.geom, way)                               AS dist
    FROM planet_osm_point, pt
    WHERE (
        tags -> 'addr:street'           IS NOT NULL
        OR tags -> 'addr:place'         IS NOT NULL
        OR tags -> 'addr:quarter'       IS NOT NULL
        OR tags -> 'addr:suburb'        IS NOT NULL
        OR tags -> 'addr:neighbourhood' IS NOT NULL
      )
      AND ST_DWithin(pt.geom, way, $3)

    UNION ALL

    SELECT
      COALESCE(tags -> 'addr:street', tags -> 'addr:place')  AS addr_street,
      tags -> 'addr:quarter'                                  AS addr_quarter,
      tags -> 'addr:suburb'                                   AS addr_suburb,
      tags -> 'addr:neighbourhood'                            AS addr_neighbourhood,
      tags -> 'addr:city'                                     AS addr_city,
      tags -> 'addr:housenumber'                              AS addr_hn,
      ST_Distance(pt.geom, way)                               AS dist
    FROM planet_osm_polygon, pt
    WHERE (
        tags -> 'addr:street'           IS NOT NULL
        OR tags -> 'addr:place'         IS NOT NULL
        OR tags -> 'addr:quarter'       IS NOT NULL
        OR tags -> 'addr:suburb'        IS NOT NULL
        OR tags -> 'addr:neighbourhood' IS NOT NULL
      )
      AND ST_DWithin(pt.geom, way, $3)
  ),

  addr_context AS (
    SELECT * FROM addr_context_raw ORDER BY dist ASC LIMIT 1
  ),

  -- snapped: نزدیک‌ترین خیابان (با یا بدون name)
  snapped AS (
    SELECT
      l.name,
      l.highway,
      l.way,
      ST_Distance(pt.geom, l.way) AS dist
    FROM planet_osm_line l, pt
    WHERE l.highway IN (
        'motorway','trunk','primary','secondary','tertiary',
        'residential','service','unclassified','living_street','pedestrian'
      )
      AND ST_DWithin(pt.geom, l.way, 300)
    ORDER BY
      ST_Distance(pt.geom, l.way) *
      CASE l.highway
        WHEN 'motorway'     THEN 0.25
        WHEN 'trunk'        THEN 0.35
        WHEN 'primary'      THEN 0.70
        WHEN 'secondary'    THEN 1.00
        WHEN 'tertiary'     THEN 1.50
        WHEN 'unclassified' THEN 2.20
        ELSE 3.80
      END
    LIMIT 1
  ),

  -- chain1: خیابانی که به snapped متصله و به نقطه نزدیک‌تره
  chain1 AS (
    SELECT l.name, l.highway, l.way,
           ST_Distance(pt.geom, l.way) AS dist
    FROM planet_osm_line l, pt, snapped
    WHERE l.name IS NOT NULL
      AND (snapped.name IS NULL OR l.name != snapped.name)
      AND ST_DWithin(l.way, snapped.way, $4)
      AND l.highway IN (
        'residential','service','tertiary','secondary',
        'primary','living_street','pedestrian'
      )
    ORDER BY ST_Distance(pt.geom, l.way) ASC
    LIMIT 1
  ),

  -- chain2: خیابانی که به chain1 متصله
  chain2 AS (
    SELECT l.name, l.highway, l.way,
           ST_Distance(pt.geom, l.way) AS dist
    FROM planet_osm_line l, pt, chain1
    WHERE chain1.way IS NOT NULL
      AND l.name IS NOT NULL
      AND l.name != chain1.name
      AND ST_DWithin(l.way, chain1.way, $4)
      AND l.highway IN (
        'residential','service','tertiary','secondary',
        'primary','living_street','pedestrian'
      )
    ORDER BY ST_Distance(pt.geom, l.way) ASC
    LIMIT 1
  ),

  -- chain3: خیابانی که به chain2 متصله
  chain3 AS (
    SELECT l.name, l.highway, l.way,
           ST_Distance(pt.geom, l.way) AS dist
    FROM planet_osm_line l, pt, chain2
    WHERE chain2.way IS NOT NULL
      AND l.name IS NOT NULL
      AND l.name != chain2.name
      AND ST_DWithin(l.way, chain2.way, $4)
      AND l.highway IN ('residential','service','living_street','pedestrian')
    ORDER BY ST_Distance(pt.geom, l.way) ASC
    LIMIT 1
  ),

  -- parent: بلوار/بزرگراه اصلی نزدیک snapped
  parent AS (
    SELECT l.name, l.highway
    FROM planet_osm_line l
    CROSS JOIN pt
    CROSS JOIN snapped
    LEFT JOIN chain1 ON TRUE
    WHERE l.highway IN ('motorway','trunk','primary','secondary')
      AND l.name IS NOT NULL
      AND (snapped.name IS NULL OR l.name != snapped.name)
      AND (chain1.name  IS NULL OR l.name != chain1.name)
      AND (
        ST_DWithin(l.way, snapped.way, $4)
        OR (chain1.way IS NOT NULL AND ST_DWithin(l.way, chain1.way, $4))
        OR ST_DWithin(pt.geom, l.way, 350)
      )
    ORDER BY
      CASE
        WHEN ST_DWithin(l.way, snapped.way, $4)                              THEN 0
        WHEN chain1.way IS NOT NULL AND ST_DWithin(l.way, chain1.way, $4)   THEN 1
        ELSE 2
      END,
      ST_Distance(pt.geom, l.way) ASC
    LIMIT 1
  ),

  building AS (
    SELECT
      p.name,
      p.tags -> 'addr:housenumber'                                AS house_number,
      COALESCE(p.tags->'addr:housename', p.tags->'name:fa')      AS house_name
    FROM planet_osm_polygon p, pt
    WHERE (p.building IS NOT NULL OR p.tags->'addr:housenumber' IS NOT NULL)
      AND ST_DWithin(pt.geom, p.way, 40)
    ORDER BY ST_Distance(pt.geom, p.way) ASC
    LIMIT 1
  ),

  landmark AS (
    SELECT name, amenity, shop, tourism FROM (
      SELECT name, amenity, shop, tourism, ST_Distance(pt.geom, way) AS dist
      FROM planet_osm_point, pt
      WHERE (amenity IS NOT NULL OR shop IS NOT NULL OR tourism IS NOT NULL)
        AND name IS NOT NULL AND ST_DWithin(pt.geom, way, 50)
      UNION ALL
      SELECT name, amenity, shop, tourism, ST_Distance(pt.geom, way) AS dist
      FROM planet_osm_polygon, pt
      WHERE (amenity IS NOT NULL OR shop IS NOT NULL OR tourism IS NOT NULL)
        AND name IS NOT NULL AND ST_DWithin(pt.geom, way, 50)
    ) lm ORDER BY dist ASC LIMIT 1
  ),

  traffic_zone AS (
    SELECT name, description
    FROM tehran_traffic_zones, pt
    WHERE ST_Contains(way, pt.geom)
    LIMIT 1
  )

SELECT
  (SELECT json_agg(json_build_object(
            'name',name,'level',admin_level,
            'landuse',landuse,'place',place_tag,'area',area))
   FROM boundaries)                   AS boundaries,

  (SELECT json_build_object('name',name,'highway',highway,'dist',dist)
   FROM snapped)                      AS snapped,

  (SELECT json_build_object(
            'addr_street',addr_street,
            'addr_quarter',addr_quarter,
            'addr_suburb',addr_suburb,
            'addr_neighbourhood',addr_neighbourhood,
            'addr_city',addr_city,
            'addr_hn',addr_hn,
            'dist',dist)
   FROM addr_context)                 AS addr_context,

  (SELECT json_build_object('name',name,'highway',highway,'dist',dist)
   FROM chain1)                       AS chain1,

  (SELECT json_build_object('name',name,'highway',highway,'dist',dist)
   FROM chain2)                       AS chain2,

  (SELECT json_build_object('name',name,'highway',highway,'dist',dist)
   FROM chain3)                       AS chain3,

  (SELECT json_build_object('name',name,'highway',highway)
   FROM parent)                       AS parent,

  (SELECT json_build_object(
            'name',COALESCE(name,house_name),
            'house_number',house_number)
   FROM building)                     AS building,

  (SELECT json_build_object(
            'name',name,'amenity',amenity,'shop',shop,'tourism',tourism)
   FROM landmark)                     AS landmark,

  (SELECT json_build_object('name',name,'description',description)
   FROM traffic_zone)                 AS traffic_zone;
"""


# ─── پردازش مرزها ─────────────────────────────────────────────────────────────
def _parse_boundaries(rows: list[dict]) -> tuple[str, str, str, str]:
    province = city = district = neighbourhood = ""
    rows_sorted = sorted(rows, key=lambda r: float(r.get("area") or 0))

    for r in rows_sorted:
        level   = str(r.get("level") or "")
        name    = r.get("name") or ""
        place   = r.get("place") or ""
        landuse = r.get("landuse") or ""

        if level == "4":
            province = _clean_province(name)

        elif level in ("6", "7", "8") or place in ("town", "city"):
            if not city:
                city = _clean_city(name)

        elif level in ("9", "10") or place in ("suburb", "quarter"):
            if not district:
                district = _clean_district(name)

        elif (
            place in ("neighbourhood", "village")
            or landuse == "residential"
            or "فاز" in name
        ):
            if not neighbourhood:
                neighbourhood = name.strip()

    return province, city, district, neighbourhood


# ─── resolve زنجیره خیابان ────────────────────────────────────────────────────
def _resolve_street_chain(
    snapped_name: str,
    chain1_name: str,
    chain2_name: str,
    chain3_name: str,
    parent_name: str,
    addr_street: str,
    addr_quarter: str,
    addr_suburb: str,
    addr_neighbourhood: str,
) -> tuple[list[str], str]:
    """
    ترتیب خروجی: از بزرگ‌ترین به کوچیک‌ترین (parent → ... → snapped)
    اگر snapped اسم نداشت، از addr_context جایگزین می‌کنیم.
    """
    seen: set[str] = set()
    chain: list[str] = []

    def add(name: str) -> None:
        n = name.strip()
        if n and n not in seen:
            seen.add(n)
            chain.append(n)

    if snapped_name:
        # داده OSM کامل داریم
        add(parent_name)
        add(chain1_name)
        add(chain2_name)
        add(chain3_name)
        add(snapped_name)
        return chain, "osm_line"
    else:
        # snapped اسم نداره — interpolation از addr_context
        add(parent_name)
        add(addr_suburb)
        add(addr_quarter)
        add(addr_neighbourhood)
        add(addr_street)
        # chain های توپولوژیک رو هم اضافه کن اگه موجودن
        add(chain1_name)
        add(chain2_name)
        add(chain3_name)
        return chain, "addr_interpolated"


# ─── ساخت آدرس نهایی ─────────────────────────────────────────────────────────
def _build_address(
    province: str,
    city: str,
    district: str,
    neighbourhood: str,
    street_chain: list[str],
    dist_to_road: float,
    building_name: str,
    house_number: str,
    landmark_name: str,
    landmark_prefix: str,
    addr_city: str,
    addr_neighbourhood: str,
) -> tuple[str, float]:
    parts: list[str] = []
    conf = 0.0

    effective_city          = city or addr_city
    effective_neighbourhood = neighbourhood or addr_neighbourhood

    # ── جغرافیا ────────────────────────────────────────────────────────────
    if province:
        parts.append(province); conf += 0.08
    if effective_city and effective_city != province:
        parts.append(effective_city); conf += 0.12
    if district and district != effective_city:
        parts.append(district); conf += 0.08
    if effective_neighbourhood and effective_neighbourhood not in (effective_city, district):
        parts.append(effective_neighbourhood); conf += 0.08

    # ── زنجیره خیابان ──────────────────────────────────────────────────────
    chain_abbrev = [_abbrev(s) for s in street_chain]
    for i, seg in enumerate(chain_abbrev):
        is_last = (i == len(chain_abbrev) - 1)
        if is_last and dist_to_road > 35.0:
            parts.append(seg)
            parts.append(f"داخل معبر به مسافت {_fa(str(round(dist_to_road)))} متر")
            conf += 0.25
        else:
            parts.append(seg)
            conf += 0.25 if is_last else 0.10

    # ── ساختمان / پلاک ─────────────────────────────────────────────────────
    last_street = chain_abbrev[-1] if chain_abbrev else ""
    if building_name and building_name != last_street:
        parts.append(building_name); conf += 0.05
    if house_number and _valid_hn(house_number):
        parts.append(f"پلاک {_fa(str(house_number))}"); conf += 0.08

    # ── لندمارک ────────────────────────────────────────────────────────────
    if landmark_name and landmark_name not in (last_street, building_name):
        parts.append(f"{landmark_prefix} {landmark_name}"); conf += 0.04

    if not parts:
        return "آدرسی در این محدوده ثبت نشده است", 0.0

    return "، ".join(parts), min(conf, 1.0)


# ─── تابع اصلی ────────────────────────────────────────────────────────────────
async def reverse_geocode(lat: float, lon: float) -> ReverseResult:
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise ValueError(f"invalid coordinates: lat={lat}, lon={lon}")

    t0 = time.perf_counter()

    cached = _cache.get(lat, lon)
    if cached is not None:
        cached.cached     = True
        cached.elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        return cached

    pool = await get_pool()
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                _MASTER_QUERY,
                lon, lat,
                float(ADDR_CONTEXT_RADIUS),
                float(CHAIN_SNAP_RADIUS),
            )
    except asyncpg.PostgresError as e:
        log.error("db_query_error", lat=lat, lon=lon, error=str(e))
        raise DatabaseError(f"db error: {e}") from e
    except asyncio.TimeoutError:
        raise DatabaseError("timeout")

    if row is None:
        raise NoResultError(f"no result for ({lat}, {lon})")

    def _p(val) -> dict:
        return json.loads(val) if val else {}

    def _pl(val) -> list:
        return json.loads(val) if val else []

    boundaries_raw = _pl(row["boundaries"])
    snapped_raw    = _p(row["snapped"])
    addr_ctx_raw   = _p(row["addr_context"])
    chain1_raw     = _p(row["chain1"])
    chain2_raw     = _p(row["chain2"])
    chain3_raw     = _p(row["chain3"])
    parent_raw     = _p(row["parent"])
    building_raw   = _p(row["building"])
    landmark_raw   = _p(row["landmark"])
    traffic_raw    = _p(row["traffic_zone"])

    province, city, district, neighbourhood = _parse_boundaries(boundaries_raw)

    snapped_name = snapped_raw.get("name") or ""
    dist_to_road = float(snapped_raw["dist"]) if snapped_raw.get("dist") else 0.0

    addr_street        = addr_ctx_raw.get("addr_street") or ""
    addr_quarter       = addr_ctx_raw.get("addr_quarter") or ""
    addr_suburb        = addr_ctx_raw.get("addr_suburb") or ""
    addr_neighbourhood = addr_ctx_raw.get("addr_neighbourhood") or ""
    addr_city          = addr_ctx_raw.get("addr_city") or ""
    addr_hn            = addr_ctx_raw.get("addr_hn") or ""

    chain1_name = chain1_raw.get("name") or ""
    chain2_name = chain2_raw.get("name") or ""
    chain3_name = chain3_raw.get("name") or ""
    parent_name = parent_raw.get("name") or ""

    street_chain, addr_source = _resolve_street_chain(
        snapped_name, chain1_name, chain2_name, chain3_name,
        parent_name, addr_street, addr_quarter,
        addr_suburb, addr_neighbourhood,
    )

    bld_name  = building_raw.get("name") or ""
    house_num = building_raw.get("house_number") or addr_hn

    lm_name   = landmark_raw.get("name") or ""
    lm_prefix = _lm_prefix(
        landmark_raw.get("amenity") or "",
        landmark_raw.get("shop") or "",
        landmark_raw.get("tourism") or "",
    ) if lm_name else ""

    tz_name = traffic_raw.get("name") or ""
    tz_desc = traffic_raw.get("description") or ""

    final_address, confidence = _build_address(
        province, city, district, neighbourhood,
        street_chain, dist_to_road,
        bld_name, house_num,
        lm_name, lm_prefix,
        addr_city, addr_neighbourhood,
    )

    if tz_name:
        final_address += f" (توجه: {tz_name} - {tz_desc})"

    # سطوح خیابان برای فیلدهای جداگانه
    sl = (street_chain + [None, None, None, None])[:4]

    elapsed = round((time.perf_counter() - t0) * 1000, 2)

    result = ReverseResult(
        address               = final_address,
        province              = province or None,
        city                  = city or addr_city or None,
        district              = district or None,
        neighbourhood         = neighbourhood or addr_neighbourhood or None,
        street_level1         = sl[0],
        street_level2         = sl[1],
        street_level3         = sl[2],
        street_level4         = sl[3],
        building_name         = bld_name or None,
        house_number          = _fa(house_num) if _valid_hn(house_num) else None,
        landmark              = f"{lm_prefix} {lm_name}".strip() if lm_name else None,
        distance_to_street_m  = round(dist_to_road, 1) if dist_to_road else None,
        addr_source           = addr_source,
        traffic_zone          = f"{tz_name} ({tz_desc})" if tz_name else None,
        confidence            = round(confidence, 2),
        source_type           = "hybrid_addr_interpolation_v1",
        cached                = False,
        elapsed_ms            = elapsed,
    )

    log.info(
        "geocode_success",
        lat=lat, lon=lon,
        city=result.city,
        chain=street_chain,
        addr_source=addr_source,
        confidence=result.confidence,
        elapsed_ms=elapsed,
    )

    _cache.set(lat, lon, result)
    return result


async def reverse_geocode_safe(lat: float, lon: float) -> dict[str, Any]:
    try:
        return (await reverse_geocode(lat, lon)).to_dict()
    except (DatabaseError, NoResultError) as e:
        log.warning("geocode_soft_error", lat=lat, lon=lon, error=str(e))
        return {
            "address": "آدرسی در این محدوده ثبت نشده است",
            "source_type": "error",
            "error": str(e),
        }
    except Exception as e:
        log.error("geocode_unexpected_error", lat=lat, lon=lon, error=str(e))
        return {
            "address": "خطا در سرویس آدرس‌دهی معکوس",
            "source_type": "error",
            "error": "خطای داخلی سرور",
        }