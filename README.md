دفترچه راهنمای فنی جامع سامانه نقشه اختصاصی ایران (لوکال)
این سند راهنمای رسمی معماری، تنظیمات، ساختار دایرکتوری و نحوه راه‌اندازی زیرساخت نقشه بومی شماست.
۱. معماری کلان زیرساخت نقشه
این زیرساخت از معماری چندلایه و میکروسرویس بهره می‌برد که هر بخش وظیفه مستقل خود را بر عهده دارد:
code
Text
کلاینت وب (map.html)
                                        │
             ┌──────────────────────────┼─────────────────────────┐
             ▼                          ▼                         ▼
   تایل‌ها و فونت‌ها (پورت 3000)      موتور جستجو (پورت 8080)     موتور مسیریاب (پورت 5000)
     [Martin Server]            [Nominatim Server]          [OSRM Engine]
             │                          │                         │
             ▼                          ▼                         ▼
 دیتابیس نقشه (PostGIS - 5433)   دیتابیس داخلی موتور جستجو     گراف جاده‌ای پردازش‌شده
۲. مرجع درگاه‌ها و پورت‌های فعال سیستم
نام سرویس	بستر اجرا	پورت بیرونی	وظیفه فنی در پروژه
PostgreSQL + PostGIS	Docker Container	5433	ذخیره‌سازی داده‌های جغرافیایی ایران با فرمت فضایی هندسی
Nominatim (Search)	Docker Container	8080	موتور جستجوی متنی و آدرس‌یابی معکوس ایران
OSRM (Routing)	Docker Container	5000	موتور مسیریابی جاده‌ای خودرو بر اساس گراف زنده راه‌های ایران
Martin (Tile Server)	Windows Native	3000	رندر لحظه‌ای تایل‌های وکتور (MVT) و تولید فونت‌های فارسی SDF
Python HTTP Server	Windows Native	5500	میزبانی فایل‌های وب نقشه جهت حل مشکلات امنیتی CORS مرورگر
۳. ساختار نهایی پوشه‌بندی و فایل‌ها
code
Text
OSM/
├── data/
│   ├── iran-latest.osm.pbf          # فایل دیتای خام جغرافیایی ایران (دانلود شده از OSM)
│   ├── iran-latest.osm.osrm         # فایل‌های گراف خروجی فرآیند مسیریابی OSRM
│   └── ... (سایر فایل‌های تولیدی OSRM)
├── fonts/
│   ├── arial.ttf                    # فونت کمکی سیستم
│   └── Vazirmatn-Thin.ttf           # فونت فارسی نقشه (وزیر)
├── martin/
│   └── martin.exe                   # فایل اجرایی تایل‌سرور وکتور
├── config.yaml                      # تنظیمات اتصال تایل‌سرور به دیتابیس و پوشه فونت‌ها
├── docker-compose.yml               # پیکربندی پایگاه‌های داده، جستجو و مسیریابی تحت داکر
├── map.html                         # رابط کاربری وب نقشه (یکپارچه‌ساز تمام سرویس‌ها)
└── README.md                        # مستندات راهنما
۴. مرجع درگاه‌های API نقشه اختصاصی شما
تمام نرم‌افزارهای شما (وب‌سایت، اپلیکیشن اندروید، iOS و...) می‌توانند از طریق این وب‌سرویس‌ها به نقشه متصل شوند:
دریافت تایل‌های نقشه (Vector Tiles API):
http://127.0.0.1:3000/{table_name}/{z}/{x}/{y}
(مثال: http://127.0.0.1:3000/planet_osm_line/{z}/{x}/{y})
دریافت فونت‌های نقشه (SDF Glyphs API):
http://127.0.0.1:3000/fonts/{fontstack}/{range}
(مثال: http://127.0.0.1:3000/fonts/Vazirmatn Thin/0-255)
موتور جستجوی آدرس (Geocoding API):
http://127.0.0.1:8080/search?q={Query}&format=json
آدرس‌یابی معکوس روی نقشه (Reverse Geocoding API):
http://127.0.0.1:8080/reverse?lat={Latitude}&lon={Longitude}&format=json
موتور مسیریابی جاده‌ای خودرو (Routing API):
http://127.0.0.1:5000/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson
۵. نحوه راه‌اندازی و اجرای گام‌به‌گام سیستم
فاز اول: اجرای پایگاه‌های داده در داکر
پوشه پروژه (C:\Users\Raven\OSM) را در PowerShell باز کرده و دستور زیر را برای روشن شدن دیتابیس PostGIS، موتور جستجو و موتور مسیریاب اجرا کنید:
code
Powershell
docker compose up -d
فاز دوم: اجرای تایل‌سرور Martin
در یک پنجره PowerShell دیگر، تایل‌سرور را اجرا کنید تا لایه‌های تصویری و فونت‌ها لود شوند:
code
Powershell
.\martin\martin.exe --config config.yaml --webui enable-for-all
فاز سوم: اجرای وب‌سرور فرانت‌اَند نقشه
در پنجره سوم PowerShell، سرور وب سبک پایتون را جهت دور زدن محدودیت‌های CORS مرورگر بالا بیاورید:
code
Powershell
python -m http.server 5500
حالا نقشه از آدرس http://127.0.0.1:5500/map.html با تمام امکانات در دسترس است.
کدهای نهایی و همگام‌شده فایل docker-compose.yml
فایل داکر کامپوز شما برای اجرای هم‌زمان پایگاه داده، جستجو و مسیریابی به این صورت است:
code
Yaml
services:
  gis-db:
    image: postgis/postgis:16-3.4
    container_name: custom_map_db
    environment:
      - POSTGRES_USER=map_admin
      - POSTGRES_PASSWORD=map_secure_pass
      - POSTGRES_DB=iran_map
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./data:/data
    restart: always

  nominatim:
    image: mediagis/nominatim:4.4
    container_name: custom_nominatim
    ports:
      - "8080:8080"
    volumes:
      - nominatim_data:/var/lib/postgresql/14/main
      - ./data:/data
    environment:
      - PBF_PATH=/data/iran-latest.osm.pbf
    restart: always

  osrm:
    image: osrm/osrm-backend
    container_name: custom_osrm
    ports:
      - "5000:5000"
    volumes:
      - ./data:/data
    command: osrm-routed --algorithm mld /data/iran-latest.osm.osrm
    restart: always

volumes:
  postgres_data:
  nominatim_data:












  ۱. ساختار دایرکتوری و فایل‌های پروژه
پوشه اصلی پروژه شما در مسیر C:\Users\Raven\OSM شامل ساختار زیر است:
code
Text
OSM/
├── data/
│   ├── iran-latest.osm.pbf          # فایل دیتای خام جغرافیایی ایران (OSM)
│   ├── iran-latest.osm.osrm         # فایل‌های گراف خروجی فرآیند مسیریابی OSRM
│   └── ... (سایر فایل‌های تولیدی OSRM)
├── fonts/
│   ├── arial.ttf                    # فونت سیستم (کمکی)
│   └── Vazirmatn-Thin.ttf           # فونت فارسی رندر نقشه (وزیر)
├── martin/
│   └── martin.exe                   # فایل اجرایی تایل‌سرور وکتور
├── config.yaml                      # تنظیمات اتصال تایل‌سرور به دیتابیس و پوشه فونت‌ها
├── docker-compose.yml               # کانتینرهای پایگاه داده جغرافیایی و موتور جستجو
├── map.html                         # رابط کاربری وب نقشه (یکپارچه‌ساز تمام سرویس‌ها)
└── README.md                        # مستندات فنی پروژه
۲. تنظیمات زیرساخت سیستم‌عامل میزبان (Windows WSL2)
برای تخصیص منابع کافی به موتورهای پردازشی داکر، فایل تنظیمات .wslconfig در مسیر پوشه کاربری ویندوز (C:\Users\Raven\.wslconfig) ساخته شده است:
code
Ini
[wsl2]
memory=8GB
processors=4
۳. پیکربندی لایه داده و سرویس‌ها (Docker Compose)
فایل docker-compose.yml وظیفه راه‌اندازی و مدیریت هم‌زمان پایگاه داده جغرافیایی PostGIS، موتور جستجوی بومی Nominatim و موتور مسیریابی OSRM را بر عهده دارد:
code
Yaml
services:
  gis-db:
    image: postgis/postgis:16-3.4
    container_name: custom_map_db
    environment:
      - POSTGRES_USER=map_admin
      - POSTGRES_PASSWORD=map_secure_pass
      - POSTGRES_DB=iran_map
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./data:/data
    restart: always

  nominatim:
    image: mediagis/nominatim:4.4
    container_name: custom_nominatim
    ports:
      - "8080:8080"
    volumes:
      - nominatim_data:/var/lib/postgresql/14/main
      - ./data:/data
    environment:
      - PBF_PATH=/data/iran-latest.osm.pbf
      - NOMINATIM_DEFAULT_LANGUAGE=fa
    restart: always

  osrm:
    image: osrm/osrm-backend
    container_name: custom_osrm
    ports:
      - "5000:5000"
    volumes:
      - ./data:/data
    command: osrm-routed --algorithm mld /data/iran-latest.osm.osrm
    restart: always

volumes:
  postgres_data:
  nominatim_data:
۴. پیکربندی تایل‌سرور Martin (config.yaml)
این فایل به تایل‌سرور Rust آموزش می‌دهد که چگونه به دیتابیس داکر متصل شده و پوشه فونت‌های بومی سیستم را برای تولید SDF Glyphs پایش کند:
code
Yaml
postgres:
  connection_string: 'postgres://map_admin:map_secure_pass@localhost:5433/iran_map'

fonts:
  - 'fonts'

cache_size_mb: 2048
preferred_encoding: gzip
۵. راهنمای اجرای گام‌به‌گام پلتفرم در حالت توسعه
گام اول: اجرای سرویس‌های داکر
PowerShell را در مسیر C:\Users\Raven\OSM باز کرده و دستور زیر را اجرا کنید:
code
Powershell
docker compose up -d
گام دوم: اجرای تایل‌سرور Martin
در پنجره دوم PowerShell، دستور زیر را اجرا کنید:
code
Powershell
.\martin\martin.exe --config config.yaml --webui enable-for-all
گام سوم: اجرای وب‌سرور توسعه کلاینت
در پنجره سوم PowerShell، سرور وب پایتون را روی پورت ۵۵۰۰ استارت کنید:
code
Powershell
python -m http.server 5500
آدرس دسترسی کلاینت: http://127.0.0.1:5500/map.html