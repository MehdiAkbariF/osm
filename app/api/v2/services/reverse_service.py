# c:\Users\Raven\OSM\app\api\v2\services\reverse_service.py
from __future__ import annotations

import asyncio
import hashlib
import re
import time
from dataclasses import dataclass
from typing import Any, List, Dict, Tuple, Optional

import asyncpg
import structlog

DB_DSN = "postgresql://map_admin:map_secure_pass@localhost:5433/iran_map"

POOL_MIN_SIZE = 2
POOL_MAX_SIZE = 10
POOL_COMMAND_TIMEOUT = 8.0   

CACHE_MAX_SIZE   = 4096       
CACHE_TTL_SEC    = 3600       
CACHE_GRID_DEG   = 0.0001     

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


@dataclass
class ReverseResult:
    address: str
    province: str | None = None
    city: str | None = None
    district: str | None = None
    neighbourhood: str | None = None
    nearest_street: str | None = None
    connector_street: str | None = None
    parent_street: str | None = None
    building_name: str | None = None
    house_number: str | None = None
    landmark: str | None = None
    distance_to_street_m: float | None = None
    traffic_zone: str | None = None    
    confidence: float = 1.0           
    source_type: str = "postgis_v3"
    cached: bool = False
    elapsed_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


class GeocoderError(Exception):
    pass

class DatabaseError(GeocoderError):
    pass

class NoResultError(GeocoderError):
    pass


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
                log.info("db_pool_created", min=POOL_MIN_SIZE, max=POOL_MAX_SIZE)
            except Exception as e:
                log.error("db_pool_failed", error=str(e))
                raise DatabaseError("db pool failed") from e
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        log.info("db_pool_closed")


@dataclass
class _CacheEntry:
    result: ReverseResult
    expires_at: float


class _GeoCache:
    def __init__(self, max_size: int, ttl: float) -> None:
        self._store: dict[str, _CacheEntry] = {}
        self._max_size = max_size
        self._ttl = ttl
        self._hits = 0
        self._misses = 0

    def _grid_key(self, lat: float, lon: float) -> str:
        glat = round(lat / CACHE_GRID_DEG) * CACHE_GRID_DEG
        glon = round(lon / CACHE_GRID_DEG) * CACHE_GRID_DEG
        raw = f"{glat:.6f},{glon:.6f}"
        return hashlib.md5(raw.encode()).hexdigest()

    def get(self, lat: float, lon: float) -> ReverseResult | None:
        key = self._grid_key(lat, lon)
        entry = self._store.get(key)
        if entry is None or time.monotonic() > entry.expires_at:
            self._misses += 1
            if entry:
                del self._store[key]
            return None
        self._hits += 1
        return entry.result

    def set(self, lat: float, lon: float, result: ReverseResult) -> None:
        if len(self._store) >= self._max_size:
            oldest = min(self._store, key=lambda k: self._store[k].expires_at)
            del self._store[oldest]
        key = self._grid_key(lat, lon)
        self._store[key] = _CacheEntry(
            result=result,
            expires_at=time.monotonic() + self._ttl,
        )

    @property
    def stats(self) -> dict[str, int]:
        return {"hits": self._hits, "misses": self._misses, "size": len(self._store)}


_cache = _GeoCache(max_size=CACHE_MAX_SIZE, ttl=CACHE_TTL_SEC)

_EN_TO_FA = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
_PROVINCE_PREFIX  = re.compile(r"^استان\s+")
_CITY_PREFIX      = re.compile(r"^(شهرستان|شهر|بخش\s+مرکزی)\s+")
_TEHRAN_SUFFIX    = re.compile(r"\s*شهر\s*تهران$")
_DISTRICT_PREFIX  = re.compile(r"^منطقه\s+")
_NEIGHBOURHOOD_PX = re.compile(r"^(محله|ناحیه)\s+")
_NUMERIC_PLATE    = re.compile(r"^[\d۰-۹]{1,5}([/-][\d۰-۹]{1,4})?$")


def to_persian_digits(text: str) -> str:
    return text.translate(_EN_TO_FA) if text else ""


def is_valid_house_number(text: str | None) -> bool:
    if not text:
        return False
    t = str(text).strip()
    if len(t) > 12 or len(t) < 1:
        return False
    fa_letters = re.findall(r"[آ-ی]", t)
    if len(fa_letters) > 2:
        return False
    return bool(_NUMERIC_PLATE.match(t) or re.match(r"^\d{1,5}$", t))


def clean_province(name: str) -> str:
    return _PROVINCE_PREFIX.sub("", name).strip() if name else ""


def clean_city(name: str) -> str:
    return _CITY_PREFIX.sub("", name).strip() if name else ""


def clean_district(name: str) -> str:
    name = _TEHRAN_SUFFIX.sub("", name)
    name = _DISTRICT_PREFIX.sub("منطقهٔ ", name)
    return name.strip()


def clean_neighbourhood(name: str) -> str:
    if not name:
        return ""
    if not _NEIGHBOURHOOD_PX.match(name):
        name = f"محلهٔ {name}"
    return name.strip()


_LANDMARK_PREFIXES: dict[tuple[str, ...], str] = {
    ("mosque",):                                    "جنب مسجد",
    ("hospital", "clinic", "doctors"):              "نزدیک بیمارستان",
    ("pharmacy",):                                  "جنب داروخانه",
    ("bank", "atm", "bureau_de_change"):            "نزدیک بانک",
    ("school", "university", "college"):            "نزدیک مدرسه/دانشگاه",
    ("fire_station",):                              "نزدیک آتش‌نشانی",
    ("police",):                                    "نزدیک کلانتری",
    ("post_office",):                               "نزدیک پست",
    ("fuel",):                                      "نزدیک پمپ بنزین",
    ("park",):                                      "نزدیک پارک",
    ("restaurant", "cafe", "fast_food"):            "جنب رستوران",
    ("supermarket", "convenience", "grocery"):      "جنب سوپرمارکت",
    ("mall", "department_store", "marketplace"):    "نزدیک مرکز خرید",
}

_TOURISM_PREFIXES: dict[str, str] = {
    "hotel":    "جنب هتل",
    "museum":   "نزدیک موزه",
    "attraction": "نزدیک جاذبه",
}


def get_landmark_prefix(amenity: str, shop: str, tourism: str) -> str:
    for keywords, prefix in _LANDMARK_PREFIXES.items():
        if amenity in keywords or shop in keywords:
            return prefix
    if tourism in _TOURISM_PREFIXES:
        return _TOURISM_PREFIXES[tourism]
    return "نزدیک"


_MASTER_QUERY = """
WITH
  pt AS (
    SELECT ST_Transform(ST_SetSRID(ST_MakePoint($1, $2), 4326), 3857) AS geom
  ),

  boundaries AS (
    SELECT
      p.name,
      p.admin_level,
      p.tags -> 'place' AS place_tag
    FROM planet_osm_polygon p, pt
    WHERE p.boundary = 'administrative'
      AND p.name IS NOT NULL
      AND ST_Contains(p.way, pt.geom)
    ORDER BY p.admin_level ASC
  ),

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
      AND l.name IS NOT NULL
      AND ST_DWithin(pt.geom, l.way, 300)
    ORDER BY
      ST_Distance(pt.geom, l.way) *
      CASE l.highway
        WHEN 'motorway'  THEN 0.25
        WHEN 'trunk'     THEN 0.35
        WHEN 'primary'   THEN 0.70
        WHEN 'secondary' THEN 1.00
        WHEN 'tertiary'  THEN 1.50
        WHEN 'unclassified' THEN 2.20
        ELSE 3.80
      END
    LIMIT 1
  ),

  connector AS (
    SELECT 
      l.name, 
      l.highway, 
      l.way,
      ST_Distance(pt.geom, l.way) AS dist
    FROM planet_osm_line l, pt, snapped
    WHERE l.name IS NOT NULL
      AND l.name != snapped.name
      AND ST_DWithin(l.way, snapped.way, 5)
      AND l.highway IN ('residential', 'service', 'tertiary', 'secondary', 'primary')
    ORDER BY ST_Distance(pt.geom, l.way) ASC
    LIMIT 1
  ),

  parent AS (
    SELECT l.name, l.highway
    FROM planet_osm_line l
    CROSS JOIN pt
    CROSS JOIN snapped
    LEFT JOIN connector ON TRUE
    WHERE l.highway IN ('motorway','trunk','primary','secondary')
      AND l.name IS NOT NULL
      AND l.name != snapped.name
      AND (connector.name IS NULL OR l.name != connector.name)
      AND (
        ST_DWithin(l.way, snapped.way, 5) 
        OR (connector.way IS NOT NULL AND ST_DWithin(l.way, connector.way, 5)) 
        OR ST_DWithin(pt.geom, l.way, 350)
      )
    ORDER BY 
      CASE 
        WHEN ST_DWithin(l.way, snapped.way, 5) THEN 0 
        WHEN (connector.way IS NOT NULL AND ST_DWithin(l.way, connector.way, 5)) THEN 1 
        ELSE 2 
      END ASC,
      ST_Distance(pt.geom, l.way) ASC
    LIMIT 1
  ),

  building AS (
    SELECT
      p.name,
      p.tags -> 'addr:housenumber' AS house_number,
      COALESCE(p.tags -> 'addr:housename', p.tags -> 'name:fa') AS house_name
    FROM planet_osm_polygon p, pt
    WHERE (p.building IS NOT NULL OR p.tags -> 'addr:housenumber' IS NOT NULL)
      AND ST_DWithin(pt.geom, p.way, 40)
    ORDER BY ST_Distance(pt.geom, p.way) ASC
    LIMIT 1
  ),

  landmark AS (
    SELECT name, amenity, shop, tourism
    FROM (
      SELECT name, amenity, shop, tourism,
             ST_Distance(pt.geom, way) AS dist
      FROM planet_osm_point, pt
      WHERE (amenity IS NOT NULL OR shop IS NOT NULL OR tourism IS NOT NULL)
        AND name IS NOT NULL
        AND ST_DWithin(pt.geom, way, 50)
      UNION ALL
      SELECT name, amenity, shop, tourism,
             ST_Distance(pt.geom, way) AS dist
      FROM planet_osm_polygon, pt
      WHERE (amenity IS NOT NULL OR shop IS NOT NULL OR tourism IS NOT NULL)
        AND name IS NOT NULL
        AND ST_DWithin(pt.geom, way, 50)
    ) lm
    ORDER BY dist ASC
    LIMIT 1
  ),

  traffic_zone AS (
    SELECT name, description
    FROM tehran_traffic_zones, pt
    WHERE ST_Contains(way, pt.geom)
    LIMIT 1
  )

SELECT
  (SELECT json_agg(json_build_object('name', name, 'level', admin_level, 'place', place_tag))
   FROM boundaries)                                           AS boundaries,

  (SELECT json_build_object('name', name, 'highway', highway, 'dist', dist)
   FROM snapped)                                             AS snapped,

  (SELECT json_build_object('name', name, 'highway', highway)
   FROM connector)                                           AS connector,

  (SELECT json_build_object('name', name, 'highway', highway)
   FROM parent)                                              AS parent,

  (SELECT json_build_object(
            'name', COALESCE(name, house_name),
            'house_number', house_number)
   FROM building)                                            AS building,

  (SELECT json_build_object(
            'name', name,
            'amenity', amenity,
            'shop', shop,
            'tourism', tourism)
   FROM landmark)                                            AS landmark,

  (SELECT json_build_object('name', name, 'description', description)
   FROM traffic_zone)                                        AS traffic_zone;
"""


def _parse_boundaries(
    rows: List[Dict[str, Any]],
) -> Tuple[str, str, str, str]:
    province = city = district = neighbourhood = ""
    for r in rows:
        level = str(r.get("level") or "")
        name  = r.get("name") or ""
        place = r.get("place") or ""
        if level == "4":
            province = clean_province(name)
        elif level in ("6", "8"):
            city = clean_city(name)
        elif level in ("9", "10") or place in ("suburb", "quarter"):
            if not district:
                district = clean_district(name)
        elif level == "11" or place == "neighbourhood":
            if not neighbourhood:
                neighbourhood = clean_neighbourhood(name)
    return province, city, district, neighbourhood


def _build_address(
    province: str,
    city: str,
    district: str,
    neighbourhood: str,
    snapped_name: str,
    snapped_type: str,
    connector_name: str,
    parent_name: str,
    building_name: str,
    house_number: str,
    landmark_name: str,
    landmark_prefix: str,
) -> Tuple[str, float]:
    parts: list[str] = []
    confidence_score = 0.0

    if province:
        parts.append(province)
        confidence_score += 0.15
    if city and city != province:
        parts.append(city)
        confidence_score += 0.15
    if district:
        parts.append(district)
        confidence_score += 0.10
    if neighbourhood:
        parts.append(neighbourhood)
        confidence_score += 0.10

    if parent_name and parent_name != snapped_name:
        parts.append(parent_name)
        confidence_score += 0.10

    if connector_name and connector_name not in (parent_name, snapped_name):
        parts.append(connector_name)
        confidence_score += 0.10

    if snapped_name:
        parts.append(snapped_name)
        confidence_score += 0.20

    if building_name and building_name != snapped_name:
        parts.append(building_name)
        confidence_score += 0.05

    if house_number and is_valid_house_number(house_number):
        fa_plate = to_persian_digits(str(house_number))
        parts.append(f"پلاک {fa_plate}")
        confidence_score += 0.10

    if landmark_name and landmark_name not in (snapped_name, building_name):
        parts.append(f"{landmark_prefix} {landmark_name}")
        confidence_score += 0.05

    if not parts:
        return "آدرسی در این محدوده ثبت نشده است", 0.0

    return "، ".join(parts), min(confidence_score, 1.0)


async def reverse_geocode(lat: float, lon: float) -> ReverseResult:
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise ValueError(f"invalid: lat={lat}, lon={lon}")

    t0 = time.perf_counter()

    cached = _cache.get(lat, lon)
    if cached is not None:
        cached.cached = True
        cached.elapsed_ms = (time.perf_counter() - t0) * 1000
        return cached

    pool = await get_pool()
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(_MASTER_QUERY, lon, lat)
    except asyncpg.PostgresError as e:
        log.error("db_query_error", lat=lat, lon=lon, error=str(e))
        raise DatabaseError(f"db error: {e}") from e
    except asyncio.TimeoutError:
        log.warning("db_query_timeout", lat=lat, lon=lon)
        raise DatabaseError("timeout")

    if row is None:
        raise NoResultError(f"no result: ({lat}, {lon})")

    import json

    def _parse(val: str | None) -> dict:
        return json.loads(val) if val else {}

    def _parse_list(val: str | None) -> list[dict]:
        return json.loads(val) if val else []

    boundaries_raw = _parse_list(row["boundaries"])
    snapped_raw    = _parse(row["snapped"])
    connector_raw  = _parse(row["connector"])
    parent_raw     = _parse(row["parent"])
    building_raw   = _parse(row["building"])
    landmark_raw   = _parse(row["landmark"])
    traffic_raw    = _parse(row["traffic_zone"])

    province, city, district, neighbourhood = _parse_boundaries(boundaries_raw)

    snapped_name = snapped_raw.get("name") or ""
    snapped_type = snapped_raw.get("highway") or ""
    dist_to_road = float(snapped_raw["dist"]) if snapped_raw.get("dist") else None

    connector_name = connector_raw.get("name") or ""
    parent_name  = parent_raw.get("name") or ""

    bld_name     = building_raw.get("name") or ""
    house_num    = building_raw.get("house_number") or ""

    lm_name    = landmark_raw.get("name") or ""
    lm_prefix  = get_landmark_prefix(
        landmark_raw.get("amenity") or "",
        landmark_raw.get("shop") or "",
        landmark_raw.get("tourism") or "",
    ) if lm_name else ""

    traffic_zone_name = traffic_raw.get("name") or ""
    traffic_zone_desc = traffic_raw.get("description") or ""

    final_address, confidence = _build_address(
        province, city, district, neighbourhood,
        snapped_name, snapped_type, connector_name, parent_name,
        bld_name, house_num,
        lm_name, lm_prefix,
    )

    if traffic_zone_name:
        final_address = f"{final_address} (🚨 توجه: {traffic_zone_name} - {traffic_zone_desc})"

    elapsed = (time.perf_counter() - t0) * 1000

    result = ReverseResult(
        address            = final_address,
        province           = province or None,
        city               = city or None,
        district           = district or None,
        neighbourhood      = neighbourhood or None,
        nearest_street     = snapped_name or None,
        connector_street   = connector_name or None,
        parent_street      = parent_name or None,
        building_name      = bld_name or None,
        house_number       = to_persian_digits(house_num) if is_valid_house_number(house_num) else None,
        landmark           = f"{lm_prefix} {lm_name}".strip() if lm_name else None,
        distance_to_street_m = round(dist_to_road, 1) if dist_to_road is not None else None,
        traffic_zone       = f"{traffic_zone_name} ({traffic_zone_desc})" if traffic_zone_name else None,
        confidence         = round(confidence, 2),
        source_type        = "postgis_v3_ultra_topological_traffic",
        cached             = False,
        elapsed_ms         = round(elapsed, 2),
    )

    log.info(
        "geocode_success",
        lat=lat, lon=lon,
        city=city,
        street=snapped_name,
        traffic_zone=result.traffic_zone,
        confidence=result.confidence,
        elapsed_ms=result.elapsed_ms,
    )

    _cache.set(lat, lon, result)
    return result


async def reverse_geocode_safe(lat: float, lon: float) -> dict[str, Any]:
    try:
        result = await reverse_geocode(lat, lon)
        return result.to_dict()
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