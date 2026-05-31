۱. معماری و جریان داده‌های پلتفرم (System Architecture)
پلتفرم نقشه شما از ساختار میکروسرویس ناهم‌گام (Async Microservices) بهره می‌برد. کلاینت‌ها (نقشه وب یا موبایل) هرگز به طور مستقیم با موتورهای سنگین داکر صحبت نمی‌کنند؛ بلکه تمام درخواست‌ها از طریق درگاه متمرکز پایتون (API Gateway) در پورت 8000 عبور می‌کنند:
code
Text
کلاینت وب (map.html)
                                        │
                                        ▼  (پورت 8000)
                     درگاه متمرکز پایتون (FastAPI - Async Engine)
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           ▼ (احراز هویت و کشینگ)       ▼ (پروکسی تایل‌های برداری)     ▼ (آدرس‌یابی معکوس پیشرفته)
    Nominatim (8080)              Martin Server (3000)          PostGIS Database (5433)
  موتور جستجوی آدرس              تایل‌سرور و رند فونت           بافر و نزدیک‌ترین معبر
۲. ساختار نهایی پوشه‌بندی پروژه
code
Text
OSM/
├── app/
│   ├── main.py                      # نقطه ورود وب‌سرور پایتون (Initialization)
│   ├── core/
│   │   └── config.py                # مدیریت تنظیمات پروژه و خواندن فایل .env
│   ├── api/
│   │   └── v1/
│   │       ├── router.py            # هماهنگ‌کننده تمام درگاه‌های نسخه ۱
│   │       └── endpoints/
│   │           ├── search.py        # درگاه جستجوی متنی آدرس
│   │           ├── reverse.py       # درگاه آدرس‌یابی معکوس پستی
│   │           ├── tiles.py         # درگاه پروکسی تایل‌های نقشه
│   │           └── pois.py          # درگاه فیلتر نزدیک‌ترین مکان‌ها (POI)
│   └── services/
│       ├── nominatim.py             # کلاس ارتباطی Nominatim
│       ├── tile_service.py          # کلاس ارتباطی Martin (Async)
│       └── postgis_service.py       # کلاس ارتباط با دیتابیس PostGIS (SQL هندسی)
├── data/
│   ├── iran-latest.osm.pbf          # فایل دیتای خام جغرافیایی ایران
│   ├── iran-latest.osrm             # فایل‌های گراف مسیریابی OSRM
│   └── ...
├── fonts/
│   ├── arial.ttf                    # فونت کمکی سیستم
│   └── Vazirmatn-Thin.ttf           # فونت فارسی نقشه (وزیر)
├── martin/
│   └── martin.exe                   # فایل اجرایی تایل‌سرور
├── config.yaml                      # تنظیمات تایل‌سرور Martin
├── docker-compose.yml               # سرویس‌های دیتابیس، مسیریاب و جستجوی داکر
├── map.html                         # رابط کاربری وب نقشه (کلاینت یکپارچه)
├── .env                             # متغیرهای حساس و پورت‌های سرور
└── requirements.txt                 # شناسنامه پکیج‌های پایتونی پروژه
۳. فایل‌های پیکربندی و بهینه‌سازی زیرساخت
الف) تنظیمات منابع سیستم‌عامل ویندوز (C:\Users\Raven\.wslconfig)
اختصاص منابع کافی به داکر جهت جلوگیری از فریز شدن سیستم در زمان ایمپورت:
code
Ini
[wsl2]
memory=8GB
processors=4
ب) فایل تنظیمات سرویس‌های داکر (docker-compose.yml)
مدیریت و بهینه‌سازی دیتابیس PostGIS، موتور جستجو با رم ۲ گیگابایتی و موتور مسیریاب OSRM:
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
      - NOMINATIM_POSTGRESQL_SHARED_BUFFERS=2GB
      - NOMINATIM_POSTGRESQL_WORK_MEM=128MB
    restart: always

  osrm:
    image: osrm/osrm-backend
    container_name: custom_osrm
    ports:
      - "5000:5000"
    volumes:
      - ./data:/data
    command: osrm-routed --algorithm mld /data/iran-latest.osrm
    restart: always

volumes:
  postgres_data:
  nominatim_data:
ج) فایل تنظیمات تایل‌سرور Martin (config.yaml)
افزایش رم کش تایل‌ها به ۲ گیگابایت و تسریع فشرده‌سازی با الگوریتم gzip:
code
Yaml
postgres:
  connection_string: 'postgres://map_admin:map_secure_pass@localhost:5433/iran_map'

fonts:
  - 'fonts'

cache_size_mb: 2048
preferred_encoding: gzip
د) فایل تنظیمات متغیرهای محیطی پایتون (.env)
code
Env
PROJECT_NAME="Iran Map API Platform"
VERSION="1.0.0"
API_V1_STR="/api/v1"

NOMINATIM_URL="http://127.0.0.1:8080"
OSRM_URL="http://127.0.0.1:5000"
POSTGRES_URL="postgresql://map_admin:map_secure_pass@127.0.0.1:5433/iran_map"
MARTIN_URL="http://127.0.0.1:3000"
۴. مرجع وب‌سرویس‌های تجاری پلتفرم (SaaS Map API Reference)
تمام کلاینت‌ها فقط به پورت 8000 پایتون متصل می‌شوند. نمونه درگاه‌های فعال:
۱. سرویس جستجوی متنی فارسی (Geocoding)
آدرس: GET http://127.0.0.1:8000/api/v1/search
پارامترها:
q (متن جستجو)
mode (global برای کل ایران، viewport برای کادر جاری)
viewbox (مختصات کادر جاری نقشه)
ویژگی: فیلتر خودکار در مرزهای ایران و بازگرداندن پاسخ با فونت فارسی بومی.
۲. سرویس آدرس‌یابی معکوس پستی (Reverse Geocoding)
آدرس: GET http://127.0.0.1:8000/api/v1/reverse
پارامترها: lat (عرض جغرافیایی)، lon (طول جغرافیایی)
ویژگی: تلفیق هوشمند کوئری بافر ۵۰ متری PostGIS با Nominatim جهت رندر آدرس پستی دقیق فارسی به همراه فاصله دقیق تا نزدیک‌ترین خیابان.
۳. سرویس تایل‌های برداری نقشه (Vector Tiles Proxy)
آدرس: GET http://127.0.0.1:8000/api/v1/tiles/{table}/{z}/{x}/{y}
ویژگی: پروکسی کاملاً ناهم‌گام (Async) با کلاینت httpx و کشینگ ۲۴ ساعته در مرورگر جهت لود آنی نقشه.
۴. سرویس نزدیک‌ترین مکان‌های اطراف کاربر (POI API)
آدرس: GET http://127.0.0.1:8000/api/v1/pois/nearest
پارامترها: lat و lon (موقعیت کاربر)، category (نوع صنف: fuel, atm, hospital, restaurant)، radius (شعاع جستجو)
ویژگی: استفاده از الگوریتم KNN دیتابیس PostGIS جهت بازگرداندن سریع پمپ‌بنزین‌ها، بیمارستان‌ها و عابربانک‌های اطراف کاربر با فاصله متری دقیق.