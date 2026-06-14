# c:\Users\Raven\OSM\app\api\v2\endpoints\map.py
import os
import json
import urllib.request
import psycopg2
from fastapi import APIRouter, Response, HTTPException, Query

from app.api.v2.schemas.map import RouteRequest, RouteOptimizeRequest
from app.api.v2.services.search_service import search
from app.api.v2.services.reverse_service import reverse_geocode
from app.api.v2.services.routing_service import get_route, optimize_trip

router = APIRouter(prefix="/map", tags=["Map"])


@router.get("/styles/default", summary="دریافت استایل کارتوگرافی استاندارد ایران (v2)")
async def get_default_style():
    style_path = os.path.join(os.getcwd(), "styles", "default.json")
    
    if not os.path.exists(style_path):
        raise HTTPException(
            status_code=404, 
            detail=f"Style file not found at: {style_path}"
        )
        
    try:
        with open(style_path, "r", encoding="utf-8") as f:
            style_data = json.load(f)
        return style_data
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error reading stylesheet from disk: {str(e)}"
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


@router.get("/tiles/{z}/{x}/{y}")
async def tile_endpoint(z: int, x: int, y: int):
    # پروکسی ایمن تایل‌های برداری از مارتین
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