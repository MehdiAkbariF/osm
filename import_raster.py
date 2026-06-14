# scripts/import_raster.py
import os
import sqlite3
import psycopg2

# ۱. تعریف آدرس‌های فیزیکی فایل‌ها
mbtiles_path = os.path.join("data", "iran_satellite.mbtiles")
pg_connection = "host=localhost port=5433 dbname=iran_map user=map_admin password=map_secure_pass"

if not os.path.exists(mbtiles_path):
    print(f"Error: Please place your raster file at: {mbtiles_path}")
    exit()

print("Connecting to databases...")
try:
    # اتصال به دیتابیسsqlite فایل mbtiles
    sqlite_conn = sqlite3.connect(mbtiles_path)
    sqlite_cursor = sqlite_conn.cursor()

    # اتصال به دیتابیس اصلی PostgreSQL
    pg_conn = psycopg2.connect(pg_connection)
    pg_cursor = pg_conn.cursor()
    
    print("Reading tiles from MBTiles...")
    sqlite_cursor.execute("SELECT zoom_level, tile_column, tile_row, tile_data FROM tiles;")
    tiles = sqlite_cursor.fetchall()
    total_tiles = len(tiles)
    print(f"Discovered {total_tiles} raster tiles. Starting import to PostgreSQL...")

    # ایمپورت کردن تایل‌ها به صورت دسته‌ای (Batch) برای سرعت بالا
    inserted = 0
    batch = []
    
    for tile in tiles:
        z = tile[0]
        x = tile[1]
        # فرمول معکوس کردن y در استاندارد TMS به Slippy Map
        y = (1 << z) - 1 - tile[2]
        tile_data = tile[3]
        
        batch.append((z, x, y, psycopg2.Binary(tile_data)))
        
        if len(batch) >= 500:
            pg_cursor.executemany(
                "INSERT INTO iran_raster_tiles (z, x, y, tile_data) VALUES (%s, %s, %s, %s) ON CONFLICT (z, x, y) DO NOTHING;",
                batch
            )
            pg_conn.commit()
            inserted += len(batch)
            print(f"Imported {inserted} / {total_tiles} tiles...", end="\r")
            batch = []

    # ثبت باقی‌مانده تایل‌ها
    if batch:
        pg_cursor.executemany(
            "INSERT INTO iran_raster_tiles (z, x, y, tile_data) VALUES (%s, %s, %s, %s) ON CONFLICT (z, x, y) DO NOTHING;",
            batch
        )
        pg_conn.commit()
        inserted += len(batch)

    print(f"\n🎉 Success! {inserted} raster tiles imported successfully to PostgreSQL.")
    
    sqlite_cursor.close()
    sqlite_conn.close()
    pg_cursor.close()
    pg_conn.close()

except Exception as e:
    print(f"Error occurred: {str(e)}")