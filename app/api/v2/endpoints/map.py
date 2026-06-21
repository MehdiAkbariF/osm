# c:\Users\Raven\OSM\app\api\v2\endpoints\map.py
import os
import json
import urllib.request
import psycopg2
from fastapi import APIRouter, Response, HTTPException, Query, Depends, Request
from sqlalchemy.orm import Session

from app.api.v2.schemas.map import RouteRequest, RouteOptimizeRequest, PublicPublishRequest
from app.api.v2.services.search_service import search
from app.api.v2.services.reverse_service import reverse_geocode
from app.api.v2.services.routing_service import get_route, optimize_trip

# ایمپورت‌های مربوط به واکشی داینامیک تنظیمات از دیتابیس
from app.core.database import get_db
from app.api.v2.services.settings_service import get_active_settings

router = APIRouter(prefix="/map", tags=["Map"])


@router.get("/styles/default", summary="دریافت استایل کارتوگرافی استاندارد ایران مجهز به رندر داینامیک و سیستم فالبک امن (v2)")
async def get_default_style(
    request: Request,
    db: Session = Depends(get_db)
):
    style_path = os.path.join(os.getcwd(), "styles", "default.json")
    
    if not os.path.exists(style_path):
        raise HTTPException(
            status_code=404, 
            detail=f"Style template file not found at: {style_path}"
        )
        
    try:
        # ۱. تلاش برای واکشی تنظیمات دیتابیس به صورت کاملاً امن
        try:
            settings_record = get_active_settings(db)
        except Exception:
            settings_record = None

        # ۲. استفاده از متدهای پیش‌فرض (فالبک) در صورت عدم وجود ستون یا نال بودن مقدار دیتابیس
        bg_color = getattr(settings_record, "background_color", "#f4f1ea") or "#f4f1ea"
        park_color = getattr(settings_record, "park_color", "#d0e4cc") or "#d0e4cc"
        water_color = getattr(settings_record, "water_color", "#aad3df") or "#aad3df"
        primary_color = getattr(settings_record, "primary_road_color", "#ffa042") or "#ffa042"
        secondary_color = getattr(settings_record, "secondary_road_color", "#ffe082") or "#ffe082"
        minor_color = getattr(settings_record, "minor_road_color", "#ffffff") or "#ffffff"
        font_family = getattr(settings_record, "font_family", "Vazirmatn Thin") or "Vazirmatn Thin"
        
        # واکشی فیلدهای پیشرفته جدید از دیتابیس یا مقادیر فالبک
        building_color = getattr(settings_record, "building_color", "#e0deda") or "#e0deda"
        res_color = getattr(settings_record, "residential_zone_color", "#e5e0d8") or "#e5e0d8"
        label_size = getattr(settings_record, "label_font_size", 1.0) or 1.0
        
        # ۳. خواندن قالب استایل خام کارتوگرافی
        with open(style_path, "r", encoding="utf-8") as f:
            style_raw = f.read()

        # ۴. تزریق داینامیک آدرس تایل‌ها بر اساس دامنه فعال درخواست‌کننده
        base_url = f"{request.url.scheme}://{request.url.netloc}/api/v2/map"
        style_raw = style_raw.replace("http://localhost:8000/api/v2/map/tiles/{z}/{x}/{y}", f"{base_url}/tiles/{{z}}/{{x}}/{{y}}")
        style_raw = style_raw.replace("http://localhost:8000/api/v2/map/raster/{z}/{x}/{y}", f"{base_url}/raster/{{z}}/{{x}}/{{y}}")
        style_raw = style_raw.replace("http://localhost:8000/api/v2/map/terrain/{z}/{x}/{y}", f"{base_url}/terrain/{{z}}/{{x}}/{{y}}")
        
        # ۵. جایگذاری داینامیک و زنده پارامترهای رنگ‌بندی و فونت پایه با امنیت بالا
        style_raw = style_raw.replace("{{BACKGROUND_COLOR}}", bg_color)
        style_raw = style_raw.replace("{{PARK_COLOR}}", park_color)
        style_raw = style_raw.replace("{{WATER_COLOR}}", water_color)
        style_raw = style_raw.replace("{{PRIMARY_ROAD_COLOR}}", primary_color)
        style_raw = style_raw.replace("{{SECONDARY_ROAD_COLOR}}", secondary_color)
        style_raw = style_raw.replace("{{MINOR_ROAD_COLOR}}", minor_color)
        style_raw = style_raw.replace("{{FONT_FAMILY}}", font_family)

        # جایگذاری متغیرهای پیشرفته جدید کارتوگرافی در فایل استایل
        style_raw = style_raw.replace("{{BUILDING_COLOR}}", building_color)
        style_raw = style_raw.replace("{{RESIDENTIAL_COLOR}}", res_color)
        style_raw = style_raw.replace("{{LABEL_FONT_SIZE}}", str(label_size))

        # تبدیل رشته نهایی به ساختار استاندارد JSON
        style_data = json.loads(style_raw)
        return style_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error compiling dynamic stylesheet: {str(e)}"
        )


@router.get("/search")
async def search_endpoint(
    q: str,
    lat: float | None = Query(None, description="عرض جغرافیایی مرکز نقشه"),
    lon: float | None = Query(None, description="طول جغرافیایی مرکز نقشه")
):
    return await search(q, user_lat=lat, user_lon=lon)


@router.get("/reverse")
async def reverse_endpoint(lat: float, lon: float):
    return await reverse_geocode(lat, lon)


@router.post("/route")
async def route_endpoint(route: RouteRequest):
    return await get_route(
        route.start_lat,
        route.start_lon,
        route.end_lat,
        route.end_lon
    )


@router.post("/route/optimize", summary="مسیریابی چندمقصده بهینه توزیع قطعات (یدکچی)")
async def route_optimize_endpoint(payload: RouteOptimizeRequest):
    locs_list = [{"lat": loc.lat, "lon": loc.lon} for loc in payload.locations]
    return await optimize_trip(locations=locs_list)


@router.post("/public-publish", summary="ثبت و همگام‌سازی داوطلبانه موقعیت فروشگاه روی نقشه عمومی")
async def public_publish_endpoint(payload: PublicPublishRequest):
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            user="map_admin",
            password="map_secure_pass",
            dbname="iran_map"
        )
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO stores (id, name, lat, lon, address, phone) 
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) 
            DO UPDATE SET 
                name = EXCLUDED.name, 
                lat = EXCLUDED.lat, 
                lon = EXCLUDED.lon, 
                address = EXCLUDED.address, 
                phone = EXCLUDED.phone
            RETURNING id, name, lat, lon, address, phone;
            """,
            (str(payload.id), payload.name, payload.lat, payload.lon, payload.address, payload.phone)
        )
        updated_store = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "detail": "Store location synchronized and published on map",
            "store": {
                "id": updated_store[0],
                "name": updated_store[1],
                "lat": updated_store[2],
                "lon": updated_store[3]
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Database error during public publishing: {str(e)}"
        )


@router.get("/tiles/{z}/{x}/{y}")
async def tile_endpoint(z: int, x: int, y: int):
    martin_url = f"http://127.0.0.1:3000/planet_osm_point,planet_osm_line,planet_osm_polygon,planet_osm_roads/{z}/{x}/{y}"
    try:
        req = urllib.request.Request(martin_url)
        req.add_header("Accept-Encoding", "gzip")
        
        with urllib.request.urlopen(req, timeout=5.0) as response:
            tile_data = response.read()
            
            response_headers = {}
            for header, value in response.headers.items():
                header_lower = header.lower()
                if header_lower not in ["content-length", "transfer-encoding", "connection", "server", "content-type"]:
                    response_headers[header] = value
            
            response_headers["Cache-Control"] = "public, max-age=86400"
            
            return Response(
                content=tile_data,
                media_type="application/vnd.mapbox-vector-tile",
                status_code=200,
                headers=response_headers
            )
    except Exception as e:
        return Response(
            status_code=502, 
            content=f"Error proxying tile from vector engine: {str(e)}"
        )


@router.get("/raster/{z}/{x}/{y}", summary="دریافت تایل‌های رستر ماهواره‌ای نقشه")
async def raster_tile_endpoint(z: int, x: int, y: int):
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            user="map_admin",
            password="map_secure_pass",
            dbname="iran_map"
        )
        cursor = conn.cursor()
        cursor.execute(
            "SELECT tile_data FROM iran_raster_tiles WHERE z=%s AND x=%s AND y=%s;",
            (z, x, y)
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row and row[0]:
            return Response(
                content=row[0], 
                media_type="image/png", 
                status_code=200,
                headers={"Cache-Control": "public, max-age=86400"}
            )
        else:
            return Response(content=b"", media_type="image/png", status_code=200)
    except Exception as e:
        raise HTTPException(
            status_code=502, 
            detail=f"Database error while fetching raster: {str(e)}"
        )


@router.get("/terrain/{z}/{x}/{y}", summary="دریافت تایل‌های رستر سه‌بعدی ارتفاعی نقشه")
async def terrain_tile_endpoint(z: int, x: int, y: int):
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            user="map_admin",
            password="map_secure_pass",
            dbname="iran_map"
        )
        cursor = conn.cursor()
        cursor.execute(
            "SELECT tile_data FROM iran_terrain_tiles WHERE z=%s AND x=%s AND y=%s;",
            (z, x, y)
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row and row[0]:
            return Response(
                content=row[0], 
                media_type="image/png", 
                status_code=200,
                headers={"Cache-Control": "public, max-age=86400"}
            )
        else:
            return Response(content=b"", media_type="image/png", status_code=200)
    except Exception as e:
        raise HTTPException(
            status_code=502, 
            detail=f"Database error while fetching terrain: {str(e)}"
        )


@router.get("/traffic-zones", summary="دریافت هندسه GeoJSON محدوده‌های ترافیکی تهران")
async def get_traffic_zones_geojson():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            user="map_admin",
            password="map_secure_pass",
            dbname="iran_map"
        )
        cursor = conn.cursor()
        
        sql_geojson = """
            SELECT jsonb_build_object(
                'type',     'FeatureCollection',
                'features', jsonb_agg(features.feature)
            )
            FROM (
              SELECT jsonb_build_object(
                'type',       'Feature',
                'geometry',   ST_AsGeoJSON(ST_Transform(way, 4326))::jsonb,
                'properties', json_build_object('id', id, 'name', name, 'description', description, 'color', color)
              ) AS feature
              FROM tehran_traffic_zones
            ) features;
        """
        cursor.execute(sql_geojson)
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row and row[0]:
            return row[0]
        
        return {"type": "FeatureCollection", "features": []}
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Database error while generating GeoJSON: {str(e)}"
        )