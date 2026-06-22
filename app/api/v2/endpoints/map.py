# c:\Users\Raven\OSM\app\api\v2\endpoints\map.py
import os
import json
import urllib.request
import psycopg2
from fastapi import APIRouter, Response, HTTPException, Query, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import text

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
        try:
            settings_record = get_active_settings(db)
        except Exception:
            settings_record = None

        bg_color = getattr(settings_record, "background_color", "#f4f1ea") or "#f4f1ea"
        park_color = getattr(settings_record, "park_color", "#d0e4cc") or "#d0e4cc"
        water_color = getattr(settings_record, "water_color", "#aad3df") or "#aad3df"
        primary_color = getattr(settings_record, "primary_road_color", "#ffa042") or "#ffa042"
        secondary_color = getattr(settings_record, "secondary_road_color", "#ffe082") or "#ffe082"
        minor_color = getattr(settings_record, "minor_road_color", "#ffffff") or "#ffffff"
        font_family = getattr(settings_record, "font_family", "Vazirmatn Thin") or "Vazirmatn Thin"
        
        building_color = getattr(settings_record, "building_color", "#e0deda") or "#e0deda"
        res_color = getattr(settings_record, "residential_zone_color", "#e5e0d8") or "#e5e0d8"
        label_size = getattr(settings_record, "label_font_size", 1.0) or 1.0
        
        with open(style_path, "r", encoding="utf-8") as f:
            style_raw = f.read()

        base_url = f"{request.url.scheme}://{request.url.netloc}/api/v2/map"
        style_raw = style_raw.replace("http://localhost:8000/api/v2/map/tiles/{z}/{x}/{y}", f"{base_url}/tiles/{{z}}/{{x}}/{{y}}")
        style_raw = style_raw.replace("http://localhost:8000/api/v2/map/raster/{z}/{x}/{y}", f"{base_url}/raster/{{z}}/{{x}}/{{y}}")
        style_raw = style_raw.replace("http://localhost:8000/api/v2/map/terrain/{z}/{x}/{y}", f"{base_url}/terrain/{{z}}/{{x}}/{{y}}")
        
        style_raw = style_raw.replace("{{BACKGROUND_COLOR}}", bg_color)
        style_raw = style_raw.replace("{{PARK_COLOR}}", park_color)
        style_raw = style_raw.replace("{{WATER_COLOR}}", water_color)
        style_raw = style_raw.replace("{{PRIMARY_ROAD_COLOR}}", primary_color)
        style_raw = style_raw.replace("{{SECONDARY_ROAD_COLOR}}", secondary_color)
        style_raw = style_raw.replace("{{MINOR_ROAD_COLOR}}", minor_color)
        style_raw = style_raw.replace("{{FONT_FAMILY}}", font_family)

        style_raw = style_raw.replace("{{BUILDING_COLOR}}", building_color)
        style_raw = style_raw.replace("{{RESIDENTIAL_COLOR}}", res_color)
        
        # جایگزینی سایز فونت بدون نقل‌قول
        style_raw = style_raw.replace('"{{LABEL_FONT_SIZE}}"', str(label_size))

        style_data = json.loads(style_raw)

        # ==========================================================
        # 🛰️ تزریق خودکار منابع ماهواره‌ای و ارتفاعی با تصحیح پرانتزهای دوبل f-string
        # ==========================================================
        style_data["sources"]["satellite-raster"] = {
            "type": "raster",
            "tiles": [f"{base_url}/raster/{{z}}/{{x}}/{{y}}"],
            "tileSize": 256
        }
        
        style_data["sources"]["terrain-source"] = {
            "type": "raster-dem",
            "tiles": [f"{base_url}/terrain/{{z}}/{{x}}/{{y}}"],
            "tileSize": 256,
            "encoding": "mapbox"
        }

        # قرار دادن لایه ماهواره در ایندکس صفر (زیر خیابان‌ها و نوشته‌ها)
        satellite_layer = {
            "id": "satellite-layer",
            "type": "raster",
            "source": "satellite-raster",
            "paint": {
                "raster-opacity": 0.0  
            }
        }
        
        if "layers" in style_data:
            style_data["layers"].insert(0, satellite_layer)

        return style_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error compiling dynamic stylesheet: {str(e)}"
        )


@router.get("/search")
async def search_endpoint(
    q: str,
    lat: float | None = Query(None, description="عرض جغایی مرکز نقشه"),
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
            INSERT INTO stores (id, name, lat, lon, address, phone, is_warehouse) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) 
            DO UPDATE SET 
                name = EXCLUDED.name, 
                lat = EXCLUDED.lat, 
                lon = EXCLUDED.lon, 
                address = EXCLUDED.address, 
                phone = EXCLUDED.phone,
                is_warehouse = EXCLUDED.is_warehouse
            RETURNING id, name, lat, lon, address, phone, is_warehouse;
            """,
            (str(payload.id), payload.name, payload.lat, payload.lon, payload.address, payload.phone, payload.is_warehouse)
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
                "lon": updated_store[3],
                "is_warehouse": updated_store[6]
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


# =====================================================================
# 🔍 موتور سرچ فضایی لوکیشن‌ها بر اساس محصولات همگام‌سازی شده محلی
# =====================================================================
@router.get("/search/by-product", summary="موتور فیلتر و جستجوی فضایی لوکیشن‌ها بر اساس موجودی محصولات دیتابیس محلی")
def search_by_product(
    q: str | None = Query(None, description="نام یا بخشی از نام محصول (Fuzzy Match)"),
    product_id: str | None = Query(None, description="شناسه یکتای دقیق محصول"),
    lat: float | None = Query(None, description="عرض جغرافیایی کاربر (جهت مرتب‌سازی بر اساس نزدیکی)"),
    lon: float | None = Query(None, description="طول جغرافیایی کاربر (جهت مرتب‌سازی بر اساس نزدیکی)"),
    db: Session = Depends(get_db)
):
    if not q and not product_id:
        raise HTTPException(status_code=400, detail="ارسال حداقل یکی از پارامترهای q یا product_id الزامی است.")

    base_sql = """
        SELECT 
            s.id AS store_id,
            s.name AS store_name,
            s.lat AS store_lat,
            s.lon AS store_lon,
            s.address AS store_address,
            s.phone AS store_phone,
            s.is_warehouse AS store_is_warehouse,
            w.id AS warehouse_id,
            w.name AS warehouse_name,
            p.id AS product_id,
            p.name AS product_name,
            i.quantity,
            CASE 
                WHEN CAST(:lat AS DOUBLE PRECISION) IS NOT NULL AND CAST(:lon AS DOUBLE PRECISION) IS NOT NULL THEN
                    ST_Distance(
                        ST_Transform(ST_SetSRID(ST_MakePoint(s.lon, s.lat), 4326), 3857),
                        ST_Transform(ST_SetSRID(ST_MakePoint(CAST(:lon AS DOUBLE PRECISION), CAST(:lat AS DOUBLE PRECISION)), 4326), 3857)
                    )
                ELSE 0.0
            END AS distance_meters
        FROM inventories i
        JOIN products p ON i.product_id = p.id
        JOIN warehouses w ON i.warehouse_id = w.id
        JOIN stores s ON w.store_id = s.id
        WHERE i.quantity > 0
    """
    
    params = {"lat": lat, "lon": lon}
    conditions = []

    if product_id:
        conditions.append("p.id = :product_id")
        params["product_id"] = product_id
    elif q:
        conditions.append("p.name = :q")
        params["q"] = q

    if conditions:
        base_sql += " AND " + " AND ".join(conditions)

    if lat is not None and lon is not None:
        base_sql += " ORDER BY distance_meters ASC;"
    else:
        base_sql += " ORDER BY p.name ASC;"

    try:
        results = db.execute(text(base_sql), params).mappings().all()
        
        formatted_results = []
        for r in results:
            formatted_results.append({
                "product": {
                    "id": r["product_id"],
                    "name": r["product_name"],
                    "quantity": r["quantity"]
                },
                "store": {
                    "id": r["store_id"],
                    "name": r["store_name"],
                    "lat": r["store_lat"],
                    "lon": r["store_lon"],
                    "address": r["store_address"],
                    "phone": r["store_phone"],
                    "is_warehouse": r["store_is_warehouse"]
                },
                "warehouse": {
                    "id": r["warehouse_id"],
                    "name": r["warehouse_name"]
                },
                "distance_meters": round(r["distance_meters"], 1) if r["distance_meters"] else None
            })
        return formatted_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error during product search: {str(e)}")


# =====================================================================
# 📦 اندپوینت: دریافت کاتالوگ تمام قطعات دارای موجودی فعال روی نقشه
# =====================================================================
@router.get("/products", summary="دریافت کاتالوگ تمام قطعات فعال و موجود در سیستم نقشه")
def get_active_products(db: Session = Depends(get_db)):
    """
    دریافت کاتالوگ تمام قطعاتی که در حال حاضر حداقل در یکی از انبارها موجودی فعال (بیشتر از صفر) دارند.
    این لیست به صورت گروهی بر اساس نام محصول ادغام می‌شود تا نام هر قطعه دقیقاً یک‌بار رندر شود.
    """
    sql = """
        SELECT p.name, MIN(p.id) AS id
        FROM products p
        JOIN inventories i ON p.id = i.product_id
        WHERE i.quantity > 0
        GROUP BY p.name
        ORDER BY p.name ASC;
    """
    try:
        results = db.execute(text(sql)).mappings().all()
        return [{"id": r["id"], "name": r["name"]} for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")