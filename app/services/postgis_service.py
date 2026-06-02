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
        آدرس‌یابی معکوس پیشرفته، سلسله‌مراتب معابر و لندمارک‌های مجاور بر پایه PostGIS خالص
        """
        # بافرهای متغیر متوالی
        adaptive_buffers = [30, 60, 120, 250, 500]
        
        best_result = None
        best_confidence = -1
        
        for buffer_meters in adaptive_buffers:
            # کوئری مهندسی‌شده و یکپارچه بدون نیاز به فیلد tags یا ستون‌های هدر هس‌تور
            query = """
                WITH params AS (
                    SELECT 
                        ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s), 4326), 3857) as geom,
                        %s::double precision as buffer
                ),
                -- ۱. یافتن نام دقیق مجتمع مسکونی، برج، پاساژ یا ساختمان از لایه پلیگون‌ها
                building_complex AS (
                    SELECT 
                        name as b_name,
                        ST_Distance(way, (SELECT geom FROM params)) as dist
                    FROM planet_osm_polygon
                    WHERE building IS NOT NULL 
                      AND name IS NOT NULL AND name != ''
                      AND ST_DWithin(way, (SELECT geom FROM params), (SELECT buffer FROM params))
                    ORDER BY dist ASC
                    LIMIT 1
                ),
                -- ۲. نزدیک‌ترین کوچه، بن‌بست یا خیابان محلی فرعی (Minor Road) در فاصله کوتاه
                nearest_minor_road AS (
                    SELECT 
                        name as road_name,
                        highway,
                        ST_Distance(way, (SELECT geom FROM params)) as dist,
                        way
                    FROM planet_osm_line
                    WHERE highway IN ('residential', 'living_street', 'service', 'unclassified', 'footway', 'path')
                      AND name IS NOT NULL AND name != ''
                      AND ST_DWithin(way, (SELECT geom FROM params), (SELECT buffer FROM params))
                    ORDER BY dist ASC
                    LIMIT 1
                ),
                -- ۳. نزدیک‌ترین خیابان اصلی/بلوار شریانی منتهی یا مجاور به معبر بالا
                nearest_major_road AS (
                    SELECT 
                        name as road_name,
                        highway,
                        ST_Distance(way, (SELECT geom FROM params)) as dist,
                        way
                    FROM planet_osm_line
                    WHERE highway IN ('motorway', 'trunk', 'primary', 'secondary', 'tertiary')
                      AND name IS NOT NULL AND name != ''
                      AND ST_DWithin(way, (SELECT geom FROM params), (SELECT buffer FROM params) * 2.5) -- بافر بزرگتر برای خیابان اصلی
                    ORDER BY dist ASC
                    LIMIT 1
                ),
                -- ۴. ادغام اطلاعات خطوط معابر فرعی و اصلی
                street_lines AS (
                    SELECT 
                        (SELECT road_name FROM nearest_minor_road) as minor_street,
                        (SELECT road_name FROM nearest_major_road) as major_street,
                        COALESCE((SELECT dist FROM nearest_minor_road), (SELECT dist FROM nearest_major_road)) as distance
                    WHERE EXISTS (SELECT 1 FROM nearest_minor_road) OR EXISTS (SELECT 1 FROM nearest_major_road)
                ),
                -- ۵. یافتن محله دقیق (neighbourhood) از لایه پلیگون‌ها با محاسبات مساحتی
                neighbourhoods AS (
                    SELECT 
                        name as neighbourhood_name,
                        ST_Distance(way, (SELECT geom FROM params)) as distance
                    FROM planet_osm_polygon
                    WHERE (place IN ('neighbourhood', 'quarter', 'suburb') OR landuse = 'residential')
                      AND name IS NOT NULL
                      AND ST_DWithin(way, (SELECT geom FROM params), (SELECT buffer FROM params) * 3) -- بافر بزرگتر برای محله
                    ORDER BY distance ASC, ST_Area(way) ASC
                    LIMIT 1
                ),
                -- ۶. یافتن شاخص‌ترین مرکز خدمات عمومی مجاور (Landmark) در فاصله ۶۰ متری جهت راهنمای آدرس
                adjacent_landmark AS (
                    SELECT 
                        name as landmark_name,
                        amenity,
                        shop,
                        ST_Distance(way, (SELECT geom FROM params)) as dist
                    FROM planet_osm_point
                    WHERE name IS NOT NULL 
                      AND (amenity IN ('mosque', 'bank', 'pharmacy', 'hospital', 'clinic', 'school', 'university', 'mall', 'cinema')
                           OR shop IN ('supermarket', 'mall', 'department_store'))
                      AND ST_DWithin(way, (SELECT geom FROM params), 60)
                    ORDER BY dist ASC
                    LIMIT 1
                ),
                -- ۷. استخراج استان (admin_level = 4)
                province_data AS (
                    SELECT name as province_name
                    FROM planet_osm_polygon
                    WHERE boundary = 'administrative' AND admin_level = '4'
                      AND ST_Contains(way, (SELECT geom FROM params))
                    LIMIT 1
                ),
                -- ۸. استخراج شهر (admin_level = 8)
                city_data AS (
                    SELECT name as city_name
                    FROM planet_osm_polygon
                    WHERE (boundary = 'administrative' AND admin_level = '8' OR place IN ('city', 'town'))
                      AND ST_Contains(way, (SELECT geom FROM params))
                    ORDER BY admin_level DESC
                    LIMIT 1
                ),
                -- ۹. استخراج منطقه شهرداری (admin_level = 9 یا suburb)
                district_data AS (
                    SELECT name as district_name
                    FROM planet_osm_polygon
                    WHERE (boundary = 'administrative' AND admin_level = '9' OR place = 'suburb')
                      AND ST_Contains(way, (SELECT geom FROM params))
                    LIMIT 1
                )
                SELECT 
                    (SELECT province_name FROM province_data) as province,
                    (SELECT city_name FROM city_data) as city,
                    (SELECT district_name FROM district_data) as district,
                    (SELECT neighbourhood_name FROM neighbourhoods) as neighbourhood,
                    (SELECT major_street FROM street_lines) as major_street,
                    (SELECT minor_street FROM street_lines) as minor_street,
                    (SELECT b_name FROM building_complex) as building_name,
                    (SELECT landmark_name FROM adjacent_landmark) as landmark_name,
                    (SELECT amenity FROM adjacent_landmark) as landmark_amenity,
                    (SELECT shop FROM adjacent_landmark) as landmark_shop,
                    ROUND((SELECT COALESCE((SELECT distance FROM street_lines), 0.0))::numeric, 2) as distance;
            """
            
            try:
                conn = psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
                cursor = conn.cursor()
                
                # ارسال فیکس و دقیق ۳ پارامتر (طول، عرض، بافر)
                cursor.execute(query, (lon, lat, buffer_meters))
                result = cursor.fetchone()
                
                cursor.close()
                conn.close()
                
                if result and (result.get('minor_street') or result.get('major_street')):
                    # امتیازدهی بر اساس غنای داده‌ها
                    score = 40
                    if result.get('minor_street'): score += 20
                    if result.get('major_street'): score += 20
                    if result.get('building_name'): score += 10
                    if result.get('landmark_name'): score += 10
                    
                    if score > best_confidence:
                        best_result = result
                        best_confidence = score
                    
                    if best_confidence >= 80:
                        return best_result
                
            except Exception as e:
                logger.error(f"Smart reverse geocode error at buffer {buffer_meters}: {str(e)}")
                continue
        
        if not best_result:
            best_result = self.get_nearest_street(lat, lon, buffer_meters=500)
        
        return best_result

    def get_nearest_street(self, lat: float, lon: float, buffer_meters: float = 100.0) -> dict:
        """
        پیدا کردن نزدیک‌ترین خیابان (نسخه فالبک ثانویه)
        """
        query = """
            WITH point_geom AS (
                SELECT ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s), 4326), 3857) as geom
            )
            SELECT 
                name as major_street,
                NULL as minor_street,
                highway,
                ROUND(ST_Distance(way, (SELECT geom FROM point_geom))::numeric, 2) as distance,
                ROUND(ST_LineLocatePoint(way, ST_ClosestPoint(way, (SELECT geom FROM point_geom)))::numeric * 100) as approx_house_number,
                'line' as source_type
            FROM planet_osm_line
            WHERE highway IS NOT NULL 
              AND name IS NOT NULL
              AND name != ''
              AND ST_DWithin(way, (SELECT geom FROM point_geom), %s)
            ORDER BY distance ASC
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
        استخراج نزدیک‌ترین مکان‌ها با رتبه‌بندی اهمیت
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