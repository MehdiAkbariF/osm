# Iran Custom Map Stack (Vector Tiles)

این پروژه یک زیرساخت نقشه اختصاصی و بومی (Self-hosted) برای کشور ایران است که داده‌های جغرافیایی را از پایگاه داده PostGIS خوانده و به صورت تایل‌های برداری (MVT) به همراه فونت‌های فارسی پویا (SDF) ارائه می‌دهد.

## ساختار پوشه‌ها و فایل‌های پروژه
```text
OSM/
├── data/
│   └── iran-latest.osm.pbf      # فایل دیتای خام جغرافیایی ایران
├── fonts/
│   ├── arial.ttf                 # فونت کمکی سیستم
│   └── Vazirmatn-Thin.ttf        # فونت فارسی نقشه
├── martin/
│   └── martin.exe                # تایل‌سرور وکتور (نسخه ویندوز)
├── config.yaml                   # تنظیمات تایل‌سرور (ارتباط دیتابیس و فونت)
├── docker-compose.yml            # تنظیمات پایگاه داده داکر
├── map.html                      # کلاینت وب نمایش نقشه (MapLibre GL JS)
└── README.md                     # مستندات پروژه
نحوه راه‌اندازی و اجرا (پله به پله)
۱. اجرای پایگاه داده (PostgreSQL + PostGIS)
پایگاه داده جغرافیایی روی پورت اختصاصی 5433 اجرا می‌شود تا با دیگر سرویس‌های محلی تداخل نداشته باشد:
code
Bash
docker compose up -d
۲. ایمپورت داده‌های نقشه ایران به دیتابیس
پردازش و تبدیل فایل خام نقشه به جداول بهینه‌شده هندسی در لایه دیتابیس با استفاده از ابزار osm2pgsql داخلی داکر:
code
Powershell
docker exec -it custom_map_db osm2pgsql --create --slim --cache 1024 --database=postgres://map_admin:map_secure_pass@127.0.0.1:5432/iran_map /data/iran-latest.osm.pbf
۳. تنظیم فایل پیکربندی Martin (config.yaml)
این فایل آدرس پایگاه داده و پوشه فونت‌های معمولی سیستم (.ttf یا .otf) را به تایل‌سرور معرفی می‌کند:
code
Yaml
postgres:
  connection_string: 'postgres://map_admin:map_secure_pass@localhost:5433/iran_map'

fonts:
  - 'fonts'
۴. اجرای تایل‌سرور اختصاصی
دستور اجرای Martin با استفاده از فایل پیکربندی و فعال‌سازی اینترفیس وب:
code
Powershell
.\martin\martin.exe --config config.yaml --webui enable-for-all
۵. مشاهده نقشه تحت وب
فایل map.html را در مرورگر باز کنید. این فایل از کتابخانه MapLibre GL JS استفاده کرده و با لود کردن پلاگین رسمی راست‌به‌چپ (RTL Text) متون فارسی را به صورت متصل و خوانا نمایش می‌دهد.
