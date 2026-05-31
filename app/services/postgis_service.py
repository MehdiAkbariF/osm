# app/services/postgis_service.py
import psycopg2
from psycopg2.extras import RealDictCursor
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class PostGISService:
    def __init__(self):
        self.db_url = settings.POSTGRES_URL

    def smart_reverse_geocode(self, lat: float, lon: float) -> dict:
        """
        آدرس‌یابی معکوس هوشمند با بافرهای چندمرحله‌ای و امتیازدهی ترکیبی
        """
        # بافرهای مرحله‌ای برای جستجوی گسترده‌تر
        adaptive_buffers = [30, 60, 120, 250, 500]
        
        best_result = None
        best_confidence = -1
        
        for buffer_meters in adaptive_buffers:
            query = """
                WITH point_geom AS (
                    SELECT ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s), 4326), 3857) as geom
                ),
                -- جستجو در نقاط آدرس‌دار (دقیق‌ترین)
                address_points AS (
                    SELECT 
                        "addr:housenumber" as house_number,
                        "addr:street" as street_name,
                        "addr:city" as city,
                        ST_Distance(way, (SELECT geom FROM point_geom)) as distance,
                        way,
                        100 as confidence,
                        'point' as source_type
                    FROM planet_osm_point
                    WHERE "addr:housenumber" IS NOT NULL 
                      AND "addr:street" IS NOT NULL
                      AND ST_DWithin(way, (SELECT geom FROM point_geom), %s)
                ),
                -- جستجو در خطوط خیابان با امتیازدهی (دقت متوسط)
                street_lines AS (
                    SELECT 
                        NULL as house_number,
                        name as street_name,
                        NULL as city,
                        ST_Distance(way, (SELECT geom FROM point_geom)) as distance,
                        way,
                        CASE 
                            WHEN highway IN ('primary', 'secondary', 'tertiary') THEN 80
                            WHEN highway IN ('residential', 'living_street') THEN 70
                            WHEN highway IN ('unclassified', 'service') THEN 50
                            ELSE 30
                        END as confidence,
                        'line' as source_type
                    FROM planet_osm_line
                    WHERE highway IS NOT NULL 
                      AND name IS NOT NULL
                      AND name != ''
                      AND ST_DWithin(way, (SELECT geom FROM point_geom), %s)
                ),
                -- جستجو در پلی‌گون‌های محله (کمترین دقت)
                neighbourhoods AS (
                    SELECT 
                        NULL as house_number,
                        name as street_name,
                        NULL as city,
                        ST_Distance(way, (SELECT geom FROM point_geom)) as distance,
                        way,
                        40 as confidence,
                        'polygon' as source_type
                    FROM planet_osm_polygon
                    WHERE (boundary = 'administrative' OR place = 'suburb' OR place = 'neighbourhood')
                      AND name IS NOT NULL
                      AND ST_DWithin(way, (SELECT geom FROM point_geom), %s)
                ),
                -- ترکیب همه منابع
                all_sources AS (
                    SELECT * FROM address_points
                    UNION ALL
                    SELECT * FROM street_lines
                    UNION ALL
                    SELECT * FROM neighbourhoods
                )
                SELECT 
                    house_number,
                    street_name,
                    city,
                    ROUND(distance::numeric, 2) as distance,
                    confidence,
                    source_type,
                    -- امتیاز نهایی: ترکیب فاصله + اطمینان منبع
                    ROUND((confidence * (1 - LEAST(distance / %s, 0.95)))::numeric, 2) as final_score
                FROM all_sources
                WHERE distance <= %s
                ORDER BY final_score DESC, distance ASC
                LIMIT 1;
            """
            
            try:
                conn = psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
                cursor = conn.cursor()
                
                # حداکثر فاصله مجاز همان بافر فعلی است
                max_dist = buffer_meters
                cursor.execute(query, (lon, lat, buffer_meters, buffer_meters, buffer_meters, max_dist, max_dist))
                result = cursor.fetchone()
                
                cursor.close()
                conn.close()
                
                if result and result.get('street_name'):
                    # اگر نتیجه بهتری پیدا کردیم، ذخیره کن
                    if result.get('final_score', 0) > best_confidence:
                        best_result = result
                        best_confidence = result.get('final_score', 0)
                    
                    # اگر امتیاز بالای ۷۰ است، همین حالا برگردان
                    if best_confidence > 70:
                        return best_result
                
            except Exception as e:
                logger.error(f"Smart reverse geocode error at buffer {buffer_meters}: {str(e)}")
                continue
        
        # اگر چیزی پیدا نشد، از تابع قبلی استفاده کن
        if not best_result:
            best_result = self.get_nearest_street(lat, lon, buffer_meters=500)
        
        return best_result

    def get_nearest_street(self, lat: float, lon: float, buffer_meters: float = 100.0) -> dict:
        """
        پیدا کردن نزدیک‌ترین خیابان (نسخه بهبود یافته با امتیازدهی)
        """
        query = """
            WITH point_geom AS (
                SELECT ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s), 4326), 3857) as geom
            )
            SELECT 
                name,
                highway,
                ROUND(ST_Distance(way, (SELECT geom FROM point_geom))::numeric, 2) as distance,
                -- محاسبه پلاک تقریبی بر اساس نسبت موقعیت روی خیابان
                ROUND(ST_LineLocatePoint(way, ST_ClosestPoint(way, (SELECT geom FROM point_geom)))::numeric * 100) as approx_house_number,
                -- امتیاز کیفیت خیابان
                CASE 
                    WHEN highway IN ('primary', 'secondary', 'tertiary') THEN 100
                    WHEN highway IN ('residential', 'living_street') THEN 85
                    WHEN highway IN ('unclassified', 'service') THEN 60
                    ELSE 40
                END as quality_score,
                'line' as source_type
            FROM planet_osm_line
            WHERE highway IS NOT NULL 
              AND name IS NOT NULL
              AND name != ''
              AND ST_DWithin(way, (SELECT geom FROM point_geom), %s)
            ORDER BY 
                quality_score DESC,
                distance ASC
            LIMIT 1;
        """
        
        try:
            conn = psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
            cursor = conn.cursor()
            cursor.execute(query, (lon, lat, buffer_meters))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result
            
        except Exception as e:
            logger.error(f"PostGIS Spatial Query Error: {str(e)}")
            return None

    def get_nearest_pois(self, lat: float, lon: float, category: str = None, radius_meters: float = 5000.0, limit: int = 10) -> list:
        """
        استخراج نزدیک‌ترین مکان‌ها با رتبه‌بندی
        """
        query = """
            WITH point_geom AS (
                SELECT ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s), 4326), 3857) as geom
            )
            SELECT 
                name, 
                amenity, 
                shop, 
                tourism,
                ROUND(ST_Distance(way, (SELECT geom FROM point_geom))::numeric, 2) as distance_meters,
                ST_Y(ST_Transform(way, 4326)) as lat,
                ST_X(ST_Transform(way, 4326)) as lon,
                -- رتبه‌بندی اهمیت
                CASE 
                    WHEN amenity IN ('restaurant', 'cafe') THEN 90
                    WHEN shop IN ('supermarket', 'convenience') THEN 85
                    WHEN amenity IN ('hospital', 'clinic', 'pharmacy') THEN 95
                    WHEN amenity IN ('bank', 'atm') THEN 70
                    WHEN tourism IS NOT NULL THEN 80
                    ELSE 50
                END as importance
            FROM planet_osm_point
            WHERE name IS NOT NULL
              AND (amenity = %s OR shop = %s OR tourism = %s OR %s IS NULL)
              AND ST_DWithin(way, (SELECT geom FROM point_geom), %s)
            ORDER BY importance DESC, distance_meters ASC
            LIMIT %s;
        """
        
        try:
            conn = psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
            cursor = conn.cursor()
            cursor.execute(query, (
                lon, lat, 
                category, category, category, category,
                radius_meters,
                limit
            ))
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"PostGIS POI Query Error: {str(e)}")
            return []


postgis_service = PostGISService()