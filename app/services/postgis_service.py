import psycopg2
from psycopg2.extras import RealDictCursor
from app.core.config import settings

class PostGISService:
    def __init__(self):
        self.db_url = settings.POSTGRES_URL

    def get_nearest_street(self, lat: float, lon: float, buffer_meters: float = 100.0) -> dict:
        """
        پیدا کردن هوشمندترین و نزدیک‌ترین معبر واقعی با بافر بزرگ ۱۰۰ متری و اولویت‌دهی وزن‌دار
        """
        # کوئری پیشرفته فضایی با اعمال تکنیک اولویت‌دهی جاده‌ای (CASE WHEN)
        query = """
            SELECT name, highway, 
                   ST_Distance(way, ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s), 4326), 3857)) as distance
            FROM planet_osm_line
            WHERE highway IS NOT NULL 
              AND name IS NOT NULL
              -- فیلتر کردن معابر در حریم بافر بزرگتر (۱۰۰ متر پیش‌فرض)
              AND ST_DWithin(way, ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s), 4326), 3857), %s)
            ORDER BY 
              -- ۱. اولویت اول: ترجیح دادن معابر اصلی و مسکونی به پیاده‌روها و کوچه‌های بن‌بست فرعی
              CASE 
                WHEN highway IN ('motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'residential') THEN 1
                WHEN highway IN ('service', 'unclassified') THEN 2
                ELSE 3
              END,
              -- ۲. اولویت دوم: فاصله واقعی هندسی تا نقطه کلیک شده (نزدیک‌ترین همسایه <->)
              way <-> ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s), 4326), 3857)
            LIMIT 1;
        """
        
        try:
            conn = psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
            cursor = conn.cursor()
            
            # ارسال پارامترها به کوئری فضایی وزن‌دار
            cursor.execute(query, (lon, lat, lon, lat, buffer_meters, lon, lat))
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            return result
            
        except Exception as e:
            print(f"PostGIS Spatial Query Error: {str(e)}")
            return None

    def get_nearest_pois(self, lat: float, lon: float, category: str = None, radius_meters: float = 5000.0, limit: int = 10) -> list:
        """
        استخراج سریع نزدیک‌ترین مکان‌ها (POI) در شعاع کاربر بر اساس ایندکس فضایی PostGIS
        """
        # کوئری پیشرفته فضایی برای تبدیل هندسه و پیدا کردن نقاط دیدنی نام‌دار
        query = """
            SELECT name, amenity, shop, tourism,
                   ST_Distance(way, ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s), 4326), 3857)) as distance_meters,
                   ST_Y(ST_Transform(way, 4326)) as lat,
                   ST_X(ST_Transform(way, 4326)) as lon
            FROM planet_osm_point
            WHERE name IS NOT NULL
              AND (
                  -- فیلتر کردن پویا بر اساس طبقه‌بندی‌های استاندارد OSM
                  amenity = %s OR shop = %s OR tourism = %s OR %s IS NULL
              )
              -- فیلتر بافر فضایی (فقط نقاط داخل شعاع کاربر)
              AND ST_DWithin(way, ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s), 4326), 3857), %s)
            -- مرتب‌سازی بر اساس نزدیک‌ترین فاصله هندسی
            ORDER BY way <-> ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s), 4326), 3857)
            LIMIT %s;
        """
        
        try:
            conn = psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
            cursor = conn.cursor()
            
            # ارسال پارامترها به کوئری
            # اگر دسته‌بندی خالی بود، مقدار None ارسال می‌شود تا فیلتر اعمال نشود
            cursor.execute(query, (
                lon, lat, 
                category, category, category, category,
                lon, lat, radius_meters,
                lon, lat, limit
            ))
            results = cursor.fetchall()
            
            cursor.close()
            conn.close()
            return results
            
        except Exception as e:
            print(f"PostGIS POI Query Error: {str(e)}")
            return []


postgis_service = PostGISService()