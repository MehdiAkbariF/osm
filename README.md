Iran Self-Hosted Map Stack

این پروژه یک زیرساخت نقشه اختصاصی و بومی (Self-hosted) برای کشور ایران است که با استفاده از پایگاه داده جغرافیایی و تایل‌سرور وکتور پیاده‌سازی شده است.

## ساختار پوشه‌ها
```text
OSM/
├── data/
│   └── iran-latest.osm.pbf      # فایل دیتای خام نقشه ایران
├── martin/
│   └── martin.exe                # تایل‌سرور وکتور مپ (نسخه ویندوز)
├── docker-compose.yml            # تنظیمات پایگاه داده داکر
├── README.md                     # مستندات پروژه
└── .gitignore                    # فایل‌های نادیده‌گرفته شده در گیت
نیازمندی‌ها
Docker Desktop روی ویندوز (به همراه WSL 2)
PowerShell یا CMD
Git
راهنمای راه‌اندازی و اجرا
۱. اجرای پایگاه داده (PostgreSQL + PostGIS)
دیتابیس روی پورت اختصاصی 5433 اجرا می‌شود تا با نسخه‌های محلی PostgreSQL تداخلی نداشته باشد.
برای اجرای پایگاه داده دستور زیر را بزنید:
code
Bash
docker compose up -d
۲. ایمپورت داده‌های نقشه ایران
دیتای ایران ازGeofabrik دانلود شده و با استفاده از ابزار osm2pgsql که درون کانتینر نصب شده است، به ساختار جدول‌های جغرافیایی تبدیل می‌شود.
فرآیند ایمپورت با دستور زیر اجرا می‌شود:
code
Powershell
docker exec -it custom_map_db osm2pgsql --create --slim --cache 1024 --database=postgres://map_admin:map_secure_pass@127.0.0.1:5432/iran_map /data/iran-latest.osm.pbf
۳. اجرای تایل‌سرور (Martin)
تایل‌سرور وکتور (Martin) به صورت مستقیم در سیستم‌عامل میزبان اجرا شده و تایل‌های برداری (MVT) را تولید می‌کند.
برای اجرا، دستورات زیر را در PowerShell وارد کنید:
code
Powershell
$env:CONNECTION_STRING="postgres://map_admin:map_secure_pass@localhost:5433/iran_map"
.\martin\martin.exe --webui enable-for-all
پس از اجرا، نقشه از آدرس زیر در مرورگر قابل بررسی است:
http://localhost:3000