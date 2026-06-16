# PROJECT CONTEXT

This file was auto-generated to give an AI assistant full context on this project: folder structure plus the content of every relevant source file. Secrets (.env, keys, credentials) are intentionally excluded.

## FOLDER STRUCTURE

```
OSM/
    .env (secret, content skipped)
    .gitignore
    README.md
    bfg.jar
    config.yaml
    create_admin.py
    docker-compose.yml
    dump_project.py
    import_raster.py
    map.html
    project_dump.txt
    requirements.txt
    s
    app/
        __init__.py
        main.py
        api/
            __init__.py
            deps.py
            v1/
                __init__.py
                dependencies.py
                router.py
                endpoints/
                    __init__.py
                    admin.py
                    admin_locations.py
                    api_keys.py
                    auth.py
                    pois.py
                    public_locations.py
                    reverse.py
                    route.py
                    search.py
                    styles.py
                    tiles.py
                    user_locations.py
            v2/
                router.py
                core/
                    __init__.py
                    config.py
                    deps.py
                endpoints/
                    admin.py
                    auth.py
                    inventory.py
                    locations.py
                    map.py
                    stores.py
                    warehouses.py
                models/
                    __init__.py
                    base.py
                    inventory.py
                    product.py
                    store.py
                    store_product.py
                    user.py
                    warehouse.py
                schemas/
                    auth.py
                    inventory.py
                    map.py
                    settings.py
                    store.py
                    warehouse.py
                services/
                    auth_client.py
                    auth_service.py
                    inventory_service.py
                    reverse_service.py
                    routing_service.py
                    search_service.py
                    store_service.py
                    tile_service.py
                    warehouse_service.py
        core/
            __init__.py
            config.py
            database.py
        models/
            __init__.py
            api_key.py
            location.py
            user.py
            user_location.py
        schemas/
            api_key.py
            location.py
            user.py
        services/
            __init__.py
            auth.py
            location_service.py
            nominatim.py
            osrm.py
            osrm_service.py
            postgis_service.py
            tile_service.py
    scripts/
        create_admin.py
    styles/
        default.json
```

## FILES

### .env

_Skipped: looks like a secret/credentials file._

### .gitignore

```
# ======================================
# Python & Virtual Environment
# ======================================
venv/
.venv/
env/
.env/
virtualenv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
pip-log.txt
pip-delete-this-directory.txt
.pytest_cache/
.coverage
.tox/
.mypy_cache/
.dmypy.json
dmypy.json

# ======================================
# OSM Raw Data Files (حجیم - چند گیگابایت)
# ======================================
# فایل‌های نقشه خام
*.osm
*.osm.bz2
*.osm.gz
*.osm.pbf
*.pbf
*.osm.xml

# فایل‌های OSRM (مسیریابی - بسیار حجیم)
*.osrm
*.osrm.*
*.osrm.nbg_nodes
*.osrm.nbg_edges
*.osrm.enw
*.osrm.fileIndex
*.osrm.tls
*.osrm.ebg
*.osrm.ebg_nodes
*.osrm.edges
*.osrm.partition
*.osrm.maneuver_overrides
*.osrm.mldgr
*.osrm.tld
*.osrm.turn_weight_penalties
*.osrm.geometry
*.osrm.icd
*.osrm.turn_penalties_index
*.osrm.hsgr
*.osrm.fingerprint

# فایل‌های خروجی Nominatim
nominatim.log
*.svg

# ======================================
# فایل‌های GIS و دیتای مکانی
# ======================================
*.shp
*.shx
*.dbf
*.prj
*.sbn
*.sbx
*.fbn
*.fbx
*.ain
*.aih
*.ixs
*.mxs
*.atx
*.cpg
*.qgs
*.qgz
*.gpkg
*.gdb/
*.gpx
*.kml
*.kmz
*.geojson
*.topojson
*.mbtiles

# ======================================
# دیتابیس‌ها (حجیم)
# ======================================
*.sql
*.sqlite
*.sqlite3
*.db
*.db3
*.mdb
*.accdb
postgres_data/
nominatim_data/
pgdata/
*.dump
*.backup

# ======================================
# فایل‌های موقت و کش
# ======================================
*.tmp
*.temp
*.cache
*.log
*.log.*
logs/
*.pid
*.seed
*.lock
*.swp
*.swo
*~
.DS_Store
Thumbs.db
desktop.ini
.cache/
.tmp/

# ======================================
# Executables & Builds
# ======================================
*.exe
*.exe~
*.dll
*.so
*.dylib
*.bin
martin/martin.exe
osm2pgsql/
osrm-extract
osrm-contract
osrm-partition
osrm-customize
osrm-routed
*.class
*.jar
target/
build/

# ======================================
# IDE & Editor Files
# ======================================
.vscode/
.idea/
*.suo
*.user
*.userosscache
*.sln.docstates
*.code-workspace
.vs/
*.swp
*.swo
*~
.project
.classpath
.settings/

# ======================================
# Docker & Containers
# ======================================
docker-compose.override.yml
*.container
*.image
.dockerignore
Dockerfile.test
docker-compose.*.yml

# ======================================
# فایل‌های تنظیمات شخصی
# ======================================
.env
.env.local
.env.*.local
.secrets
config.local.*
*.key
*.pem
*.crt

# ======================================
# فایل‌های دیتای مسیریابی (اضافی)
# ======================================
data/ !data/.gitkeep
raw_data/
temp_data/
cache_data/
*.mdx
*.mms
*.rec
*.dat

# ======================================
# فایل‌های فشرده شده
# ======================================
*.zip
*.tar
*.tar.gz
*.tgz
*.rar
*.7z
*.bz2
*.gz

# ======================================
# Backup Files
# ======================================
*.bak
*.backup
*.old
*.orig
*.rej
*-backup
backup_*/

# ======================================
# فایل‌های تست و نمونه
# ======================================
sample_data/
test_data/
examples/*.osm
notebooks/*.ipynb_checkpoints
```

### README.md

```markdown
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
```

### config.yaml

```yaml

postgres:
  connection_string: 'postgres://map_admin:map_secure_pass@localhost:5433/iran_map'


fonts:
  - 'fonts'







cache_size_mb: 2048



preferred_encoding: gzip
```

### create_admin.py

```python
# c:\Users\Raven\OSM\create_admin.py
import psycopg2
from app.api.v2.services.auth_service import hash_password

DB_CONNECTION = "host=localhost port=5433 dbname=iran_map user=map_admin password=map_secure_pass"

def create_first_admin():
    username = "admin"
    password = "admin123456"
    full_name = "Yadakchi Administrator"
    role = "super_admin"
    
    hashed = hash_password(password)
    
    try:
        conn = psycopg2.connect(DB_CONNECTION)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username=%s;", (username,))
        exists = cursor.fetchone()
        
        if exists:
            print("Admin user already exists in database.")
            cursor.close()
            conn.close()
            return
            
        cursor.execute(
            "INSERT INTO users (username, password_hash, full_name, role) VALUES (%s, %s, %s, %s);",
            (username, hashed, full_name, role)
        )
        conn.commit()
        print(f"Success! Admin user created with username: {username} and password: {password}")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")

if __name__ == "__main__":
    create_first_admin()
```

### docker-compose.yml

```yaml
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
```

### dump_project.py

```python
#!/usr/bin/env python3
"""
dump_project.py

Packs an entire project into a single Markdown file so it can be pasted
into any AI chat (Claude, ChatGPT, Gemini, ...) and the AI immediately
understands the full structure and code.

Usage (run from inside your project root, e.g. C:\\Users\\Raven\\OSM):

    python dump_project.py

Output:
    project_context.md   (in the same folder you run it from)

What it does:
    - Walks the project directory.
    - Skips noisy / irrelevant folders: venv, __pycache__, .git, node_modules,
      dist, build, third-party vendored source trees (osm2pgsql, martin binaries),
      .bfg-report, *.egg-info, .pytest_cache, .mypy_cache, .idea, .vscode.
    - Skips binary / huge / irrelevant files (fonts, images, compiled libs,
      lockfiles you don't usually need to show, etc.).
    - Skips anything that looks like a secret (.env, *.pem, *.key) and just
      notes that it was skipped, so you don't leak credentials by accident.
    - Writes a folder tree + the full content of every remaining text file,
      each fenced with its relative path and a language tag for syntax
      highlighting.

Tweak the EXCLUDE_DIRS / EXCLUDE_FILE_PATTERNS / SECRET_PATTERNS lists below
to fit your project.
"""

import os
import sys
import fnmatch

# ---------------------------------------------------------------------------
# CONFIGURATION — edit this section for your project
# ---------------------------------------------------------------------------

ROOT = os.getcwd()                     # run the script from your project root
OUTPUT_FILE = "project_context.md"

# Folders to skip entirely (matched by folder name, anywhere in the tree)
EXCLUDE_DIRS = {
    "venv", ".venv", "env", "__pycache__", ".git", ".github",
    "node_modules", "dist", "build", ".pytest_cache", ".mypy_cache",
    ".idea", ".vscode", ".bfg-report",
    # third-party vendored source you almost never need to show an AI
    "osm2pgsql", "contrib", "martin",
    # generated/data dirs that are usually huge and not "code"
    "data", "fonts", "clean_fonts",
}

# File name patterns to skip (fnmatch-style, case-insensitive)
EXCLUDE_FILE_PATTERNS = [
    "*.pyc", "*.pyo", "*.so", "*.dll", "*.exe", "*.o", "*.a",
    "*.png", "*.jpg", "*.jpeg", "*.gif", "*.ico", "*.svg", "*.webp",
    "*.ttf", "*.otf", "*.woff", "*.woff2",
    "*.zip", "*.tar", "*.gz", "*.7z", "*.rar",
    "*.db", "*.sqlite3", "*.mbtiles", "*.pbf", "*.pmtiles",
    "*.pdf", "*.mp4", "*.mov",
    "*.lock",                 # poetry.lock / package-lock.json etc (often huge)
    OUTPUT_FILE,
]

# Anything matching these is treated as a SECRET: never print contents,
# just note that it exists and was skipped.
SECRET_PATTERNS = [
    ".env", ".env.*", "*.pem", "*.key", "*credentials*", "*secret*",
]

# Hard cap per file (characters) to avoid one giant generated file blowing
# up the whole dump. Files larger than this get truncated with a note.
MAX_FILE_CHARS = 20000

# Map file extensions to markdown code-fence language tags
LANG_MAP = {
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".tsx": "tsx", ".jsx": "jsx", ".json": "json", ".yml": "yaml",
    ".yaml": "yaml", ".toml": "toml", ".ini": "ini", ".cfg": "ini",
    ".sql": "sql", ".sh": "bash", ".bat": "bat", ".ps1": "powershell",
    ".html": "html", ".css": "css", ".md": "markdown", ".txt": "",
    ".lua": "lua", ".dockerfile": "dockerfile",
}

# ---------------------------------------------------------------------------
# IMPLEMENTATION — usually no need to touch below this line
# ---------------------------------------------------------------------------


def is_excluded_dir(dirname: str) -> bool:
    return dirname in EXCLUDE_DIRS or dirname.startswith(".") and dirname not in {".env.example"}


def matches_any(name: str, patterns) -> bool:
    name_low = name.lower()
    return any(fnmatch.fnmatch(name_low, pat.lower()) for pat in patterns)


def is_secret(name: str) -> bool:
    return matches_any(name, SECRET_PATTERNS)


def is_excluded_file(name: str) -> bool:
    return matches_any(name, EXCLUDE_FILE_PATTERNS)


def lang_for(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return LANG_MAP.get(ext, "")


def build_tree(root: str) -> str:
    lines = []
    for current_root, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if not is_excluded_dir(d))
        rel = os.path.relpath(current_root, root)
        depth = 0 if rel == "." else rel.count(os.sep) + 1
        indent = "    " * depth
        label = os.path.basename(current_root) if rel != "." else os.path.basename(root) or root
        lines.append(f"{indent}{label}/")
        sub_indent = "    " * (depth + 1)
        for f in sorted(files):
            if is_excluded_file(f):
                continue
            tag = " (secret, content skipped)" if is_secret(f) else ""
            lines.append(f"{sub_indent}{f}{tag}")
    return "\n".join(lines)


def read_text_safely(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except UnicodeDecodeError:
        return None  # binary or non-utf8, skip content
    except Exception as e:
        return f"<<could not read file: {e}>>"


def main():
    root = ROOT
    print(f"Scanning project at: {root}")

    out_lines = []
    out_lines.append("# PROJECT CONTEXT\n")
    out_lines.append(
        "This file was auto-generated to give an AI assistant full context "
        "on this project: folder structure plus the content of every "
        "relevant source file. Secrets (.env, keys, credentials) are "
        "intentionally excluded.\n"
    )

    out_lines.append("## FOLDER STRUCTURE\n")
    out_lines.append("```")
    out_lines.append(build_tree(root))
    out_lines.append("```\n")

    out_lines.append("## FILES\n")

    file_count = 0
    skipped_secret = 0
    skipped_binary = 0

    for current_root, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if not is_excluded_dir(d))
        for f in sorted(files):
            if is_excluded_file(f):
                continue

            full_path = os.path.join(current_root, f)
            rel_path = os.path.relpath(full_path, root).replace("\\", "/")

            if is_secret(f):
                skipped_secret += 1
                out_lines.append(f"### {rel_path}\n")
                out_lines.append("_Skipped: looks like a secret/credentials file._\n")
                continue

            content = read_text_safely(full_path)
            if content is None:
                skipped_binary += 1
                continue

            truncated_note = ""
            if len(content) > MAX_FILE_CHARS:
                content = content[:MAX_FILE_CHARS]
                truncated_note = "\n\n_(truncated — file exceeds size limit)_"

            lang = lang_for(rel_path)
            out_lines.append(f"### {rel_path}\n")
            out_lines.append(f"```{lang}")
            out_lines.append(content.rstrip())
            out_lines.append("```" + truncated_note + "\n")
            file_count += 1

    out_path = os.path.join(root, OUTPUT_FILE)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out_lines))

    print(f"Done. Wrote {file_count} files into: {out_path}")
    print(f"Skipped {skipped_secret} secret file(s), {skipped_binary} binary/unreadable file(s).")
    print("Review the output once before sharing it — double-check no secrets leaked in.")


if __name__ == "__main__":
    main()
```

### import_raster.py

```python
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
```

### map.html

```html
<!-- c:\Users\Raven\OSM\map.html -->
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نقشه اختصاصی ایران - مدیریت لجستیک و انبارها (v2)</title>
    <link href="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.css" rel="stylesheet" />
    <style>
        body, html { margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; font-family: Tahoma, sans-serif; }
        #map { width: 100%; height: 100%; }

        #search-container {
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background: white;
            padding: 8px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
            display: flex;
            flex-direction: column;
            width: 340px;
        }
        #search-row { display: flex; width: 100%; gap: 6px; }
        #search-input {
            flex-grow: 1;
            padding: 10px 12px;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            font-size: 13px;
            outline: none;
            font-family: inherit;
        }
        #search-button {
            padding: 10px 16px;
            background: #ffa042;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            font-weight: bold;
            font-family: inherit;
        }
        #search-button:hover { background: #e07a1b; }

        #category-filter-container {
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1000;
            display: flex;
            gap: 6px;
            background: white;
            padding: 6px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        }
        .cat-btn {
            padding: 8px 14px;
            border: 1px solid #e0e0e0;
            background: white;
            border-radius: 6px;
            cursor: pointer;
            font-size: 11px;
            font-weight: bold;
            font-family: inherit;
            display: flex;
            align-items: center;
            gap: 4px;
            transition: all 0.2s;
        }
        .cat-btn:hover { background: #ffa042; color: white; border-color: #ffa042; }
        .cat-btn.active { background: #ffa042; color: white; border-color: #ffa042; }
        
        #search-results { max-height: 200px; overflow-y: auto; margin-top: 6px; background: white; border-radius: 6px; }
        
        #info-box {
            position: absolute;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
            background: rgba(0,0,0,0.85);
            color: white;
            padding: 12px 18px;
            border-radius: 8px;
            font-size: 12px;
            line-height: 1.6;
            max-width: 280px;
            pointer-events: none;
        }

        #address-box {
            position: absolute;
            bottom: 20px;
            left: 20px;
            z-index: 1000;
            background: rgba(0,0,0,0.85);
            backdrop-filter: blur(8px);
            border-radius: 12px;
            padding: 14px 18px;
            font-size: 13px;
            max-width: 450px;
            direction: rtl;
            text-align: right;
            pointer-events: auto;
            border-right: 4px solid #ffa042;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }

        #address-box strong { color: #ffa042; display: block; margin-bottom: 8px; font-size: 13px; }
        #address-text { color: #fff; line-height: 1.6; font-size: 12px; display: block; }
        .address-coord { font-size: 10px; color: #aaa; margin-top: 8px; padding-top: 6px; border-top: 1px solid rgba(255,255,255,0.2); direction: ltr; text-align: left; }
        .close-address { position: absolute; top: 8px; left: 12px; cursor: pointer; font-size: 16px; color: #aaa; transition: color 0.2s; }
        .close-address:hover { color: #ffa042; }

        .result-item { padding: 10px 12px; cursor: pointer; border-bottom: 1px solid #f0f0f0; font-size: 12px; text-align: right; }
        .result-item:hover { background: #f7f7f7; }
        .result-distance { font-size: 10px; color: #ffa042; margin-right: 8px; }
        
        #route-panel {
            position: absolute;
            bottom: 20px;
            left: 20px;
            z-index: 1000;
            background: rgba(0,0,0,0.9);
            backdrop-filter: blur(8px);
            border-radius: 12px;
            padding: 12px;
            font-size: 12px;
            max-width: 380px;
            direction: rtl;
            border-right: 4px solid #ffa042;
            pointer-events: auto;
        }

        #satellite-toggle {
            position: absolute;
            bottom: 20px;
            left: 20px;
            z-index: 1000;
            background: #1e88e5;
            color: white;
            padding: 10px 16px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            font-family: inherit;
            font-weight: bold;
            font-size: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: background 0.2s;
        }
        #satellite-toggle:hover { background: #1565c0; }
    </style>
</head>
<body>

    <div id="search-container">
        <div id="search-row">
            <input type="text" id="search-input" placeholder="جستجوی مکان بر اساس API v2..." />
            <button id="search-button">جستجو</button>
        </div>
        <div id="search-results"></div>
    </div>

    <div id="category-filter-container">
        <button class="cat-btn" id="yadakchi-stores-btn" style="border: 1px solid #1e88e5; color: #1e88e5; font-weight: bold;">⚙️ فروشگاه‌های یدکچی</button>
        <button class="cat-btn warehouse-btn" data-store-id="1">🏢 انبارهای فروشگاه ۱</button>
        <button class="cat-btn warehouse-btn" data-store-id="2">🏢 انبارهای فروشگاه ۲</button>
        <button class="cat-btn warehouse-btn" data-store-id="3">🏢 انبارهای فروشگاه ۳</button>
    </div>

    <button id="satellite-toggle">🛰️ نقشه ماهواره‌ای / ترکیبی</button>

    <div id="info-box">
        <b>✨ نقشه اختصاصی یودکچی (نسخه ۲)</b><br/>
        ✅ کلیک چپ: تعیین مبدا (سبز) و مقصد (قرمز) برای مسیریابی جاده‌ای<br/>
        ✅ کلیک راست: دریافت آدرس معکوس نقطه از پایتون<br/>
        <span style="color:#ffa042;">🔍 زوم بیشتر = جزئیات دقیق‌تر برداری</span>
    </div>

    <div id="address-box" style="display: none;">
        <span class="close-address" onclick="document.getElementById('address-box').style.display='none';">✕</span>
        <strong>📍 آدرس دقیق مکان (v2)</strong>
        <div id="address-text">در حال دریافت آدرس...</div>
        <div id="address-coords" class="address-coord"></div>
    </div>

    <div id="map"></div>

    <script src="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.js"></script>
    <script>
        maplibregl.setRTLTextPlugin(
            'https://unpkg.com/@mapbox/mapbox-gl-rtl-text@0.2.3/mapbox-gl-rtl-text.js',
            null,
            true
        );

        const MAP_API_KEY = "yk_live_ctrFT2gB-IVAsPNP0q_QsX1VTml6qXVTaSDhkOcv630";
        const vectorStyleUrl = `http://localhost:8000/api/v2/map/styles/default?api_key=${MAP_API_KEY}`;
        
        let map;
        let searchMarker = null;
        let startCoords = null;
        let endCoords = null;
        let startMarker = null;
        let endMarker = null;
        let warehouseMarkers = [];
        let storeMarkers = []; 
        let storesActive = false; 
        let satelliteActive = false;

        async function initMap() {
            try {
                const response = await fetch(vectorStyleUrl, {
                    headers: { 'X-API-Key': MAP_API_KEY }
                });
                const style = await response.json();

                const v2TileUrl = "http://localhost:8000/api/v2/map/tiles/{z}/{x}/{y}";
                
                style.sources = {
                    "iran_polygons": {
                        "type": "vector",
                        "tiles": [v2TileUrl]
                    },
                    "iran_lines": {
                        "type": "vector",
                        "tiles": [v2TileUrl]
                    },
                    "iran_points": {
                        "type": "vector",
                        "tiles": [v2TileUrl]
                    },
                    "satellite-raster": {
                        "type": "raster",
                        "tiles": ["http://localhost:8000/api/v2/map/raster/{z}/{x}/{y}"],
                        "tileSize": 256
                    }
                };

                style.glyphs = "http://localhost:3000/font/{fontstack}/{range}";

                if (style.layers) {
                    style.layers.forEach(layer => {
                        if (layer.layout && layer.layout["text-font"]) {
                            layer.layout["text-font"] = ["Vazirmatn Thin"];
                        }
                    });

                    style.layers.unshift({
                        "id": "satellite-layer",
                        "type": "raster",
                        "source": "satellite-raster",
                        "paint": {
                            "raster-opacity": 0.0 
                        }
                    });
                }

                map = new maplibregl.Map({
                    container: 'map',
                    center: [51.404, 35.715], 
                    zoom: 16, 
                    pitch: 45, 
                    bearing: -15, 
                    style: style,
                    transformRequest: (url, resourceType) => {
                        if (url.includes("127.0.0.1:8000") || url.includes("localhost:8000")) {
                            return {
                                url: url,
                                headers: { 'X-API-Key': MAP_API_KEY }
                            };
                        }
                        return { url: url };
                    }
                });

                map.addControl(new maplibregl.NavigationControl());
                
                map.on('load', () => {
                    map.addSource('terrain-source', {
                        type: 'raster-dem',
                        tiles: ['http://localhost:8000/api/v2/map/terrain/{z}/{x}/{y}'],
                        tileSize: 256,
                        encoding: 'mapbox'
                    });
                    
                    map.setTerrain({
                        source: 'terrain-source',
                        exaggeration: 1.5 
                    });

                    loadTehranTrafficZones();
                });
                
                setupMapEvents();
                setupYadakchiStores();
                setupSatelliteToggle();

            } catch (error) {
                console.error("error:", error);
            }
        }

        function buildCleanAddress(item) {
            if (typeof item === 'string') return item;
            if (item.address) return item.address;
            return item.display_name || 'آدرس نامشخص';
        }
        
        function calculateDistance(lat1, lon1, lat2, lon2) {
            const R = 6371;
            const dLat = (lat2 - lat1) * Math.PI / 180;
            const dLon = (lon2 - lon1) * Math.PI / 180;
            const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                      Math.sin(dLon/2) * Math.sin(dLon/2);
            const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
            return R * c;
        }

        function setupSatelliteToggle() {
            const btn = document.getElementById('satellite-toggle');
            btn.addEventListener('click', () => {
                satelliteActive = !satelliteActive;
                map.setPaintProperty('satellite-layer', 'raster-opacity', satelliteActive ? 1.0 : 0.0);
                btn.style.background = satelliteActive ? '#ffa042' : '#1e88e5';
                btn.innerHTML = satelliteActive ? '🗺️ نقشه کارتوگرافی / خطوط' : '🛰️ نقشه ماهواره‌ای / ترکیبی';
                
                if (satelliteActive) {
                    if (map.getLayer('background')) map.setPaintProperty('background', 'background-color', '#000000');
                } else {
                    if (map.getLayer('background')) map.setPaintProperty('background', 'background-color', '#f4f1ea');
                }
            });
        }

        async function loadTehranTrafficZones() {
            try {
                const url = "http://localhost:8000/api/v2/map/traffic-zones";
                const response = await fetch(url, { headers: { 'X-API-Key': MAP_API_KEY } });
                const geojson = await response.json();

                map.addSource('tehran-traffic-zones', {
                    'type': 'geojson',
                    'data': geojson
                });

                map.addLayer({
                    'id': 'traffic-zones-fill',
                    'type': 'fill',
                    'source': 'tehran-traffic-zones',
                    'layout': {},
                    'paint': {
                        'fill-color': ['get', 'color'], 
                        'fill-opacity': 0.15
                    }
                });

                map.addLayer({
                    'id': 'traffic-zones-outline',
                    'type': 'line',
                    'source': 'tehran-traffic-zones',
                    'layout': {},
                    'paint': {
                        'line-color': ['get', 'color'],
                        'line-width': 2,
                        'line-dasharray': [2, 2]
                    }
                });

                map.on('click', 'traffic-zones-fill', (e) => {
                    const props = e.features[0].properties;
                    new maplibregl.Popup()
                        .setLngLat(e.lngLat)
                        .setHTML(`
                            <div style="text-align: right; direction: rtl; font-family: Tahoma, sans-serif; font-size: 11px;">
                                <b style="color: ${props.color}; font-size: 12px;">🚨 ${props.name}</b><br/>
                                ⚠️ ${props.description}
                            </div>
                        `)
                        .addTo(map);
                });

                map.on('mouseenter', 'traffic-zones-fill', () => { map.getCanvas().style.cursor = 'pointer'; });
                map.on('mouseleave', 'traffic-zones-fill', () => { map.getCanvas().style.cursor = ''; });

            } catch (error) {
                console.error("error:", error);
            }
        }

        function setupMapEvents() {
            map.on('click', async (e) => {
                const coords = [e.lngLat.lng, e.lngLat.lat];
                if (!startCoords) {
                    startCoords = coords;
                    startMarker = new maplibregl.Marker({ color: '#2e7d32' }).setLngLat(startCoords).addTo(map);
                } else if (!endCoords) {
                    endCoords = coords;
                    endMarker = new maplibregl.Marker({ color: '#d32f2f' }).setLngLat(endCoords).addTo(map);
                    await calculateRoute(startCoords, endCoords, true);
                } else {
                    resetRouting();
                    startCoords = coords;
                    startMarker = new maplibregl.Marker({ color: '#2e7d32' }).setLngLat(startCoords).addTo(map);
                }
            });

            const addressBox = document.getElementById('address-box');
            const addressText = document.getElementById('address-text');
            const addressCoords = document.getElementById('address-coords');

            map.on('contextmenu', async (e) => {
                e.preventDefault();
                const lng = e.lngLat.lng;
                const lat = e.lngLat.lat;
                
                addressBox.style.display = 'block';
                addressText.innerHTML = 'در حال دریافت آدرس...';
                addressCoords.innerHTML = `مختصات: ${lng.toFixed(6)} , ${lat.toFixed(6)}`;
                
                try {
                    const reverseUrl = `http://127.0.0.1:8000/api/v2/map/reverse?lat=${lat}&lon=${lng}`;
                    const reverseResponse = await fetch(reverseUrl, {
                        headers: { 'X-API-Key': MAP_API_KEY }
                    });
                    const data = await reverseResponse.json();
                    
                    if (!data) {
                        addressText.innerHTML = 'آدرسی برای این نقطه یافت نشد.';
                        return;
                    }
                    addressText.innerHTML = typeof data === 'string' ? data : (data.address || data.display_name || 'نامشخص');
                } catch (error) {
                    console.error('خطا در آدرس‌یابی معکوس:', error);
                    addressText.innerHTML = 'خطا در ارتباط با سرور آدرس‌یابی پایتون.';
                }
            });
        }

        async function executeSearch() {
            const query = document.getElementById('search-input').value.trim();
            const resultsContainer = document.getElementById('search-results');
            if (!query) { resultsContainer.innerHTML = ''; return; }
            
            resultsContainer.innerHTML = '<div class="result-item">در حال جستجو...</div>';
            
            const center = map.getCenter();
            
            try {
                let url = `http://127.0.0.1:8000/api/v2/map/search?q=${encodeURIComponent(query)}&lat=${center.lat}&lon=${center.lng}`;
                const response = await fetch(url, { headers: { 'X-API-Key': MAP_API_KEY } });
                const data = await response.json();
                
                displaySearchResults(data);
                
                if (!data || data.length === 0) {
                    resultsContainer.innerHTML = `<div class="result-item">مکانی برای "${query}" یافت نشد.</div>`;
                }
            } catch (error) {
                console.error("خطا در جستجو:", error);
                resultsContainer.innerHTML = '<div class="result-item" style="color:red;">خطا در اتصال به پلاتفرم نقشه!</div>';
            }
        }

        function displaySearchResults(results) {
            const resultsContainer = document.getElementById('search-results');
            resultsContainer.innerHTML = '';
            
            const items = Array.isArray(results) ? results : [results];
            if (items.length === 0 || !items[0]) return;

            const center = map.getCenter();
            items.forEach(item => {
                const div = document.createElement('div');
                div.className = 'result-item';
                
                const lat = item.lat ? parseFloat(item.lat) : center.lat;
                const lon = item.lon ? parseFloat(item.lon) : center.lng;
                
                const distance = calculateDistance(center.lat, center.lng, lat, lon);
                const formattedAddress = buildCleanAddress(item);
                
                div.innerHTML = `${formattedAddress} <span class="result-distance">(${distance.toFixed(1)} کیلومتر)</span>`;
                div.onclick = () => {
                    map.flyTo({ center: [lon, lat], zoom: 15, essential: true });
                    if (searchMarker) searchMarker.remove();
                    searchMarker = new maplibregl.Marker({ color: '#ffa042' }).setLngLat([lon, lat]).addTo(map);
                    resultsContainer.innerHTML = '';
                };
```

_(truncated — file exceeds size limit)_

### project_dump.txt

```

```

### requirements.txt

```
psycopg2-binary
```

### s

```

    Directory: C:\Users\Raven\OSM


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----         5/31/2026  10:29 AM                app
d-----         5/27/2026  10:22 AM                clean_fonts
d-----         5/31/2026   1:02 PM                data
d-----         5/27/2026  10:29 AM                fonts
d-----         5/27/2026   9:41 AM                martin
d-----         5/31/2026   9:28 AM                osm2pgsql
d-----         5/31/2026  10:28 AM                scripts
d-----         5/28/2026  12:00 PM                venv
-a----         5/31/2026  10:08 AM            690 .env
-a----         5/31/2026   8:46 AM            356 .gitignore
-a----         5/31/2026   9:32 AM            188 config.yaml
-a----         5/31/2026  10:06 AM           1064 docker-compose.yml
-a----         5/31/2026   9:45 AM          31591 map.html
-a----         5/31/2026  10:01 AM           8064 README.md
-a----         5/30/2026  10:35 AM             15 requirements.txt
-a----         5/27/2026   8:34 AM           2333 s


PS C:\Users\Raven\OSM> cd c:\Users\Raven\OSM\app
PS C:\Users\Raven\OSM\app> ls


    Directory: C:\Users\Raven\OSM\app


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----         5/30/2026  10:15 AM                api
d-----         5/31/2026  10:22 AM                core
d-----         5/31/2026   1:06 PM                models
d-----         5/31/2026  11:56 AM                schemas
d-----         5/31/2026  11:59 AM                services
d-----         5/31/2026  10:29 AM                __pycache__
-a----         5/31/2026  10:28 AM           1309 main.py
-a----         5/28/2026  11:59 AM              0 __init__.py

PS C:\Users\Raven\OSM\app\api> ls


    Directory: C:\Users\Raven\OSM\app\api


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----         5/31/2026  10:29 AM                v1
d-----         5/30/2026  10:15 AM                __pycache__
-a----         5/28/2026  11:59 AM              0 deps.py
-a----         5/28/2026  11:59 AM              0 __init__.py

PS C:\Users\Raven\OSM\app\api\v1\endpoints> ls


    Directory: C:\Users\Raven\OSM\app\api\v1\endpoints


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----         5/31/2026   1:07 PM                __pycache__
-a----         5/31/2026  10:28 AM           4293 admin.py
-a----         5/31/2026  10:42 AM           5097 auth.py
-a----         5/31/2026   1:07 PM          10288 locations.py
-a----         5/30/2026  11:51 AM           1087 pois.py
-a----         5/31/2026   8:19 AM           4649 reverse.py
-a----         5/28/2026  11:59 AM              0 route.py
-a----         5/30/2026  10:29 AM           2525 search.py
-a----         5/30/2026  11:43 AM           1008 tiles.py
-a----         5/28/2026  11:59 AM              0 __init__.py

c:\Users\Raven\OSM\app\api\v1\endpoints\admin.py
# app/api/v1/endpoints/admin.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, MessageResponse
from app.api.v1.dependencies import get_current_admin

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_current_admin)])

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = Query(0, ge=0, description="تعداد رد شده"),
    limit: int = Query(50, ge=1, le=100, description="تعداد در هر صفحه"),
    db: Session = Depends(get_db)
):
    """
    دریافت لیست همه کاربران (فقط ادمین)
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return [UserResponse.model_validate(user) for user in users]

@router.get("/users/pending", response_model=List[UserResponse])
async def get_pending_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    دریافت لیست کاربران در انتظار تایید (is_active=False)
    """
    users = db.query(User).filter(User.is_active == False).offset(skip).limit(limit).all()
    return [UserResponse.model_validate(user) for user in users]

@router.put("/users/{user_id}/approve", response_model=MessageResponse)
async def approve_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    تایید کاربر توسط ادمین
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")
    
    if user.is_active:
        return MessageResponse(message="کاربر قبلاً تایید شده است", success=True)
    
    user.is_active = True
    user.approved_at = datetime.utcnow()
    user.approved_by = current_admin.id
    
    db.commit()
    
    return MessageResponse(message=f"کاربر {user.username} با موفقیت تایید شد")

@router.put("/users/{user_id}/reject", response_model=MessageResponse)
async def reject_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    رد درخواست کاربر (حذف کاربر)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")
    
    db.delete(user)
    db.commit()
    
    return MessageResponse(message=f"درخواست کاربر {user.username} رد و حذف شد")

@router.put("/users/{user_id}/block", response_model=MessageResponse)
async def block_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    مسدود کردن کاربر (is_active = False)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")
    
    if user.is_admin:
        raise HTTPException(status_code=403, detail="نمی‌توانید ادمین را مسدود کنید")
    
    user.is_active = False
    db.commit()
    
    return MessageResponse(message=f"کاربر {user.username} مسدود شد")

@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    حذف کامل کاربر
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")
    
    if user.is_admin:
        raise HTTPException(status_code=403, detail="نمی‌توانید ادمین را حذف کنید")
    
    db.delete(user)
    db.commit()
    
    return MessageResponse(message=f"کاربر {user.username} حذف شد")

c:\Users\Raven\OSM\app\api\v1\endpoints\auth.py
# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, TokenResponse, UserResponse, MessageResponse, ChangePassword, UserUpdate
from app.services.auth import auth_service
from app.api.v1.dependencies import get_current_user  # ✅ اضافه کردن این خط

router = APIRouter(prefix="/auth", tags=["Authentication"])
@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    ثبت‌نام کاربر جدید
    """
    # بررسی وجود نام کاربری تکراری
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این نام کاربری قبلاً ثبت شده است"
        )
    
    # بررسی وجود ایمیل تکراری
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این ایمیل قبلاً ثبت شده است"
        )
    
    # هش کردن رمز عبور
    hashed_password = auth_service.hash_password(user_data.password)
    
    # ایجاد کاربر جدید (is_active = False به صورت پیش‌فرض)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        phone_number=user_data.phone_number,
        is_active=False,
        is_admin=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return MessageResponse(
        message="ثبت‌نام با موفقیت انجام شد. حساب کاربری شما منتظر تایید ادمین است.",
        success=True
    )

@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    ورود کاربر به سیستم
    """
    user = db.query(User).filter(
        (User.username == login_data.username) | (User.email == login_data.username)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="نام کاربری یا رمز عبور اشتباه است"
        )
    
    if not auth_service.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="نام کاربری یا رمز عبور اشتباه است"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="حساب کاربری شما هنوز توسط ادمین تایید نشده است"
        )
    
    user.last_login = datetime.utcnow()
    db.commit()
    
    access_token = auth_service.create_access_token(user.id, user.username)
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    دریافت اطلاعات کاربر جاری
    """
    return UserResponse.model_validate(current_user)

@router.put("/me", response_model=UserResponse)
async def update_me(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ویرایش اطلاعات کاربر جاری
    """
    if user_data.full_name is not None:
        current_user.full_name = user_data.full_name
    if user_data.phone_number is not None:
        current_user.phone_number = user_data.phone_number
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    تغییر رمز عبور
    """
    if not auth_service.verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="رمز عبور فعلی اشتباه است"
        )
    
    current_user.hashed_password = auth_service.hash_password(password_data.new_password)
    db.commit()
    
    return MessageResponse(message="رمز عبور با موفقیت تغییر کرد")

c:\Users\Raven\OSM\app\api\v1\endpoints\locations.py
# app/api/v1/endpoints/locations.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User
from app.models.location import Location
from app.schemas.location import (
    LocationCreate, LocationUpdate, LocationResponse, 
    LocationAdminResponse, LocationApprove, LocationReject,
    MessageResponse
)
from app.services.location_service import location_service
from app.api.v1.dependencies import get_current_user, get_current_admin

router = APIRouter(prefix="/locations", tags=["Locations"])

# ========== کاربر معمولی ==========

@router.post("/", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_location(
    location_data: LocationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ثبت موقعیت مکانی جدید
    - فقط کاربران تایید شده می‌توانند ثبت کنند
    - موقعیت با وضعیت pending ذخیره می‌شود
    """
    location = location_service.create_location(db, location_data, current_user.id)
    return location

@router.get("/my-locations", response_model=List[LocationResponse])
async def get_my_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None, description="pending, approved, rejected"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    دریافت موقعیت‌های ثبت شده توسط کاربر جاری
    """
    locations = location_service.get_user_locations(db, current_user.id, skip, limit, status)
    return locations

@router.get("/my-locations/{location_id}", response_model=LocationResponse)
async def get_my_location(
    location_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    دریافت جزئیات یک موقعیت (فقط اگر مالک آن باشید)
    """
    location = location_service.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="موقعیت یافت نشد")
    if location.created_by != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="شما دسترسی به این موقعیت ندارید")
    return location

@router.put("/my-locations/{location_id}", response_model=LocationResponse)
async def update_my_location(
    location_id: int,
    location_data: LocationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ویرایش موقعیت (فقط اگر در وضعیت pending باشد)
    """
    location = location_service.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="موقعیت یافت نشد")
    if location.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="شما دسترسی به این موقعیت ندارید")
    if location.status != "pending":
        raise HTTPException(status_code=400, detail="فقط موقعیت‌های در انتظار تایید قابل ویرایش هستند")
    
    updated = location_service.update_location(db, location_id, location_data)
    return updated

@router.delete("/my-locations/{location_id}", response_model=MessageResponse)
async def delete_my_location(
    location_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    حذف موقعیت (فقط اگر در وضعیت pending باشد)
    """
    location = location_service.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="موقعیت یافت نشد")
    if location.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="شما دسترسی به این موقعیت ندارید")
    if location.status != "pending":
        raise HTTPException(status_code=400, detail="فقط موقعیت‌های در انتظار تایید قابل حذف هستند")
    
    location_service.delete_location(db, location_id)
    return MessageResponse(message="موقعیت با موفقیت حذف شد")

# ========== API عمومی (برای نقشه) ==========

@router.get("/approved", response_model=List[LocationResponse])
async def get_approved_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    category: Optional[str] = None,
    city: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    دریافت موقعیت‌های تایید شده (برای نمایش در نقشه)
    - بدون نیاز به احراز هویت
    """
    locations = location_service.get_all_locations(
        db, skip, limit, status="approved", category=category, city=city
    )
    return locations

@router.get("/nearby", response_model=List[LocationResponse])
async def get_nearby_locations(
    lat: float = Query(..., description="عرض جغرافیایی"),
    lon: float = Query(..., description="طول جغرافیایی"),
    radius_km: float = Query(5.0, ge=0.5, le=50, description="شعاع بر حسب کیلومتر"),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    دریافت موقعیت‌های تایید شده نزدیک به مختصات داده شده
    - برای نمایش مکان‌های اطراف
    """
    locations = location_service.get_nearby_locations(db, lat, lon, radius_km, limit)
    return locations

# ========== ادمین ==========

@router.get("/admin/all", response_model=List[LocationAdminResponse])
async def admin_get_all_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = Query(None, description="pending, approved, rejected"),
    category: Optional[str] = None,
    city: Optional[str] = None,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    دریافت تمام موقعیت‌ها (فقط ادمین)
    """
    locations = location_service.get_all_locations(db, skip, limit, status, category, city)
    
    # اضافه کردن اطلاعات ایجادکننده
    result = []
    for loc in locations:
        creator = db.query(User).filter(User.id == loc.created_by).first()
        loc_dict = LocationAdminResponse.model_validate(loc).dict()
        loc_dict["creator_name"] = creator.full_name or creator.username
        loc_dict["creator_username"] = creator.username
        result.append(LocationAdminResponse(**loc_dict))
    
    return result

@router.get("/admin/pending", response_model=List[LocationAdminResponse])
async def admin_get_pending_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    دریافت موقعیت‌های در انتظار تایید (فقط ادمین)
    """
    locations = location_service.get_pending_locations(db, skip, limit)
    
    result = []
    for loc in locations:
        creator = db.query(User).filter(User.id == loc.created_by).first()
        loc_dict = LocationAdminResponse.model_validate(loc).dict()
        loc_dict["creator_name"] = creator.full_name or creator.username
        loc_dict["creator_username"] = creator.username
        result.append(LocationAdminResponse(**loc_dict))
    
    return result

@router.put("/admin/{location_id}/approve", response_model=LocationResponse)
async def admin_approve_location(
    location_id: int,
    approve_data: LocationApprove,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    تایید موقعیت توسط ادمین
    """
    location = location_service.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="موقعیت یافت نشد")
    
    if location.status != "pending":
        raise HTTPException(status_code=400, detail="این موقعیت قبلاً بررسی شده است")
    
    approved = location_service.approve_location(
        db, location_id, current_admin.id, approve_data.admin_notes
    )
    return approved

@router.put("/admin/{location_id}/reject", response_model=MessageResponse)
async def admin_reject_location(
    location_id: int,
    reject_data: LocationReject,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    رد موقعیت توسط ادمین با ذکر دلیل
    """
    location = location_service.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="موقعیت یافت نشد")
    
    if location.status != "pending":
        raise HTTPException(status_code=400, detail="این موقعیت قبلاً بررسی شده است")
    
    rejected = location_service.reject_location(
        db, location_id, current_admin.id, reject_data.r
```

_(truncated — file exceeds size limit)_

### app/__init__.py

```python

```

### app/main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine
from app.api.v2.models.base import Base

# IMPORTANT: همه مدل‌ها را import کن تا ثبت شوند
from app.api.v2.models import user, store, warehouse, inventory, product

from app.api.v2.router import router as v2_router

# ایجاد جداول
print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Database tables created/verified")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v2_router, prefix="/api/v2")

@app.get("/")
def root():
    return {"status": "ok", "project": settings.PROJECT_NAME}
```

### app/api/__init__.py

```python

```

### app/api/deps.py

```python

```

### app/api/v1/__init__.py

```python

```

### app/api/v1/dependencies.py

```python

from fastapi import Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.core.database import get_db
from app.services.auth import auth_service
from app.models.user import User
from app.models.api_key import APIKey

security = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = auth_service.verify_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توکن نامعتبر یا منقضی شده است",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توکن نامعتبر است"
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="کاربر یافت نشد"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="حساب کاربری شما هنوز توسط ادمین تایید نشده است"
        )

    return user

async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="شما دسترسی ادمین ندارید"
        )
    return current_user

async def get_api_key(
    api_key_header: str = Depends(api_key_header),
    api_key_query: str = Query(None, alias="api_key"),  
    db: Session = Depends(get_db)
) -> APIKey:
    """
    اعتبارسنجی هدر یا پارامتر آدرس API Key بدون محدودیت نرخ درخواست (Rate Limit)
    """
    
    api_key_val = api_key_header or api_key_query

    if not api_key_val:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="کلید دسترسی (API Key) در هدر یا پارامتر آدرس درخواست یافت نشد"
        )

    
    db_key = db.query(APIKey).filter(APIKey.key == api_key_val).first()
    if not db_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="کلید دسترسی وارد شده نامعتبر است"
        )

    
    if not db_key.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="این کلید دسترسی توسط مدیر سیستم غیرفعال شده است"
        )

    
    if not db_key.is_unlimited:
        if db_key.expires_at and db_key.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="مدت اعتبار این کلید دسترسی منقضی شده است"
            )

    
    owner = db_key.user
    if not owner or not owner.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="حساب کاربری مالک این کلید غیرفعال یا مسدود است"
        )

    
    db_key.last_used_at = datetime.now(timezone.utc)
    db.commit()

    return db_key
```

### app/api/v1/router.py

```python
# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.endpoints import (
    search, reverse, tiles, pois, auth, admin, api_keys, route, styles,
    public_locations, user_locations, admin_locations  # 🔑 وارد کردن ۳ روتر جدید تفکیک‌شده
)

api_router = APIRouter()

# ۱. ثبت روترهای دارای پیشوند داخلی
api_router.include_router(auth.router)
api_router.include_router(admin.router)
api_router.include_router(api_keys.router)
api_router.include_router(route.router)
api_router.include_router(styles.router)

# 🔑 ثبت روترهای تفکیک‌شده‌ی جدید برای MaaS لوکیشن‌ها
api_router.include_router(public_locations.router) # درگاه لوکیشن‌های عمومی نقشه و سرچ یدکچی
api_router.include_router(user_locations.router)   # درگاه پنل انبار داران شخصی
api_router.include_router(admin_locations.router)  # درگاه پنل تایید/رد ادمین سیستم

# ۲. ثبت روترهای عمومی
api_router.include_router(pois.router, prefix="/pois", tags=["POIs"])
api_router.include_router(reverse.router, prefix="/reverse", tags=["Reverse Geocoding"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(tiles.router, prefix="/tiles", tags=["Vector Tiles"])
```

### app/api/v1/endpoints/__init__.py

```python

```

### app/api/v1/endpoints/admin.py

```python
# app/api/v1/endpoints/admin.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User
from app.models.api_key import APIKey
from app.schemas.user import UserResponse, MessageResponse
from app.schemas.api_key import APIKeyResponse, APIKeyAdminUpdate
from app.api.v1.dependencies import get_current_admin

router = APIRouter(
    prefix="/admin", 
    tags=["Admin"], 
    dependencies=[Depends(get_current_admin)]
)

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = Query(0, ge=0, description="تعداد رد شده"),
    limit: int = Query(50, ge=1, le=100, description="تعداد در هر صفحه"),
    db: Session = Depends(get_db)
):
    """ دریافت لیست همه کاربران (فقط ادمین) """
    users = db.query(User).offset(skip).limit(limit).all()
    return [UserResponse.model_validate(user) for user in users]

@router.get("/users/pending", response_model=List[UserResponse])
async def get_pending_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """ دریافت لیست کاربران در انتظار تایید (is_active=False) """
    users = db.query(User).filter(User.is_active == False).offset(skip).limit(limit).all()
    return [UserResponse.model_validate(user) for user in users]

@router.put("/users/{user_id}/approve", response_model=MessageResponse)
async def approve_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """ تایید کاربر توسط ادمین """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")

    if user.is_active:
        return MessageResponse(message="کاربر قبلاً تایید شده است", success=True)

    user.is_active = True
    user.approved_at = datetime.now(timezone.utc)
    user.approved_by = current_admin.id

    db.commit()

    return MessageResponse(message=f"کاربر {user.username} با موفقیت تایید شد")

@router.put("/users/{user_id}/reject", response_model=MessageResponse)
async def reject_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """ رد درخواست کاربر (حذف کاربر) """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")

    db.delete(user)
    db.commit()

    return MessageResponse(message=f"درخواست کاربر {user.username} رد و حذف شد")

@router.put("/users/{user_id}/block", response_model=MessageResponse)
async def block_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """ مسدود کردن کاربر (is_active = False) """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")

    if user.is_admin:
        raise HTTPException(status_code=403, detail="نمی‌توانید ادمین را مسدود کنید")

    user.is_active = False
    db.commit()

    return MessageResponse(message=f"کاربر {user.username} مسدود شد")

@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """ حذف کامل کاربر """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")

    if user.is_admin:
        raise HTTPException(status_code=403, detail="نمی‌توانید ادمین را حذف کنید")

    db.delete(user)
    db.commit()

    return MessageResponse(message=f"کاربر {user.username} حذف شد")

# ========== مدیریت API Keyها توسط ادمین ==========

@router.get("/api-keys", response_model=List[APIKeyResponse])
async def admin_get_all_api_keys(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    دریافت لیست تمام کلیدهای صادر شده در کل سامانه (فقط ادمین)
    """
    keys = db.query(APIKey).offset(skip).limit(limit).all()
    return keys

@router.put("/api-keys/{key_id}", response_model=APIKeyResponse)
async def admin_update_api_key(
    key_id: int,
    update_data: APIKeyAdminUpdate,
    db: Session = Depends(get_db)
):
    """
    ویرایش و مدیریت وضعیت کلید دسترسی (فعال/غیرفعال‌سازی، تغییر انقضا، نرخ درخواست) (فقط ادمین)
    """
    db_key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not db_key:
        raise HTTPException(status_code=404, detail="کلید دسترسی یافت نشد")

    if update_data.is_active is not None:
        db_key.is_active = update_data.is_active
    if update_data.is_unlimited is not None:
        db_key.is_unlimited = update_data.is_unlimited
        if update_data.is_unlimited:
            db_key.expires_at = None
    if update_data.expires_at is not None and not db_key.is_unlimited:
        db_key.expires_at = update_data.expires_at
    if update_data.rate_limit is not None:
        db_key.rate_limit = update_data.rate_limit

    db.commit()
    db.refresh(db_key)
    return db_key

@router.delete("/api-keys/{key_id}", response_model=MessageResponse)
async def admin_delete_api_key(
    key_id: int,
    db: Session = Depends(get_db)
):
    """
    ابطال همیشگی و حذف کلید از دیتابیس توسط ادمین
    """
    db_key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not db_key:
        raise HTTPException(status_code=404, detail="کلید دسترسی یافت نشد")

    db.delete(db_key)
    db.commit()
    return MessageResponse(message=f"کلید دسترسی مربوط به کاربر با شناسه {db_key.user_id} حذف شد")
```

### app/api/v1/endpoints/admin_locations.py

```python
# app/api/v1/endpoints/admin_locations.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User
from app.schemas.location import (
    LocationCreate, LocationResponse, LocationAdminResponse, LocationApprove, LocationReject, MessageResponse
)
from app.services.location_service import location_service
from app.api.v1.dependencies import get_current_admin

router = APIRouter(prefix="/admin/locations", tags=["Admin Locations"])

def parse_location_to_dict(loc, db: Session = None) -> dict:
    """تبدیل ایمن آبجکت دیتابیس به دیکشنری برای Pydantic با تغییر نام فیلد metadata"""
    loc_data = {c.name: getattr(loc, c.name) for c in loc.__table__.columns}
    loc_data["metadata"] = loc_data.pop("meta_data", None)
    
    if db:
        if loc.created_by:
            creator = db.query(User).filter(User.id == loc.created_by).first()
            if creator:
                loc_data["creator_name"] = creator.full_name or creator.username
                loc_data["creator_username"] = creator.username
        else:
            loc_data["creator_name"] = "کاربر مهمان (Anonymous)"
            loc_data["creator_username"] = "guest"
            
    return loc_data

@router.post("/", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def admin_create_location_on_behalf(
    location_data: LocationCreate,
    creator_id: Optional[int] = Query(None, description="شناسه کاربری فرد مالک در دیتابیس نقشه (در صورت وجود)"),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    owner_id = creator_id if creator_id is not None else current_admin.id
    
    location = location_service.create_location(db, location_data, user_id=owner_id)
    location.status = "approved"
    location.approved_by = current_admin.id
    location.approved_at = datetime.utcnow()
    db.commit()
    db.refresh(location)
    
    return LocationResponse(**parse_location_to_dict(location))


@router.get("/all", response_model=List[LocationAdminResponse])
async def admin_get_all_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = Query(None, description="pending, approved, rejected"),
    category: Optional[str] = None,
    city: Optional[str] = None,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    locations = location_service.get_all_locations(db, skip, limit, status, category, city)
    return [LocationAdminResponse(**parse_location_to_dict(loc, db)) for loc in locations]


@router.get("/pending", response_model=List[LocationAdminResponse])
async def admin_get_pending_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    locations = location_service.get_pending_locations(db, skip, limit)
    return [LocationAdminResponse(**parse_location_to_dict(loc, db)) for loc in locations]


@router.put("/{location_id}/approve", response_model=LocationResponse)
async def admin_approve_location(
    location_id: int,
    approve_data: LocationApprove,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    location = location_service.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="موقعیت یافت نشد")
    
    if location.status != "pending":
        raise HTTPException(status_code=400, detail="این موقعیت قبلاً بررسی شده است")
    
    approved = location_service.approve_location(
        db, location_id, current_admin.id, approve_data.admin_notes
    )
    return LocationResponse(**parse_location_to_dict(approved))


@router.put("/{location_id}/reject", response_model=MessageResponse)
async def admin_reject_location(
    location_id: int,
    reject_data: LocationReject,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    location = location_service.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="موقعیت یافت نشد")
    
    if location.status != "pending":
        raise HTTPException(status_code=400, detail="این موقعیت قبلاً بررسی شده است")
    
    location_service.reject_location(
        db, location_id, current_admin.id, reject_data.reason, reject_data.admin_notes
    )
    return MessageResponse(
        message=f"موقعیت {location.title} رد شد",
        success=True,
        location_id=location_id
    )


@router.delete("/{location_id}", response_model=MessageResponse)
async def admin_delete_location(
    location_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    location = location_service.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="موقعیت یافت نشد")
    
    location_service.delete_location(db, location_id)
    return MessageResponse(message=f"موقعیت {location.title} حذف شد", location_id=location_id)
```

### app/api/v1/endpoints/api_keys.py

```python
# app/api/v1/endpoints/api_keys.py
import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from app.core.database import get_db
from app.models.user import User
from app.models.api_key import APIKey
from app.schemas.api_key import APIKeyCreate, APIKeyResponse, APIKeyCreateResponse
from app.schemas.user import MessageResponse
from app.api.v1.dependencies import get_current_user

router = APIRouter(prefix="/api-keys", tags=["API Keys"])

@router.post("/", response_model=APIKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_user_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    تولید یک کلید دسترسی جدید برای کاربر جاری
    """
    # تولید کلید تصادفی منحصر‌به‌فرد
    raw_key = f"yk_live_{secrets.token_urlsafe(32)}"
    masked_key = f"yk_live_{raw_key[8:12]}****{raw_key[-4:]}"

    # بررسی صحت منطقی فیلد انقضا
    if not key_data.is_unlimited and not key_data.expires_at:
        raise HTTPException(
            status_code=400, 
            detail="در صورت محدود بودن کلید، تعیین تاریخ انقضا الزامی است"
        )

    new_key = APIKey(
        key=raw_key,
        masked_key=masked_key,
        name=key_data.name,
        user_id=current_user.id,
        is_active=True,
        is_unlimited=key_data.is_unlimited,
        expires_at=key_data.expires_at if not key_data.is_unlimited else None,
        rate_limit=key_data.rate_limit
    )

    db.add(new_key)
    db.commit()
    db.refresh(new_key)

    # تغییر اعمال‌شده: تبدیل به دیکشنری و اضافه کردن فیلد خام پیش از ولیدیشن نهایی
    key_data_dict = APIKeyResponse.model_validate(new_key).dict()
    key_data_dict["raw_key"] = raw_key  # تزریق کلید خام به صورت ایمن

    return APIKeyCreateResponse(**key_data_dict)

@router.get("/", response_model=List[APIKeyResponse])
async def get_my_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    مشاهده لیست کلیدهای ساخته‌شده توسط کاربر جاری (به صورت ماسک‌شده)
    """
    keys = db.query(APIKey).filter(APIKey.user_id == current_user.id).all()
    return keys

@router.delete("/{key_id}", response_model=MessageResponse)
async def delete_my_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    حذف و ابطال همیشگی کلید دسترسی توسط مالک آن
    """
    db_key = db.query(APIKey).filter(APIKey.id == key_id, APIKey.user_id == current_user.id).first()
    if not db_key:
        raise HTTPException(status_code=404, detail="کلید دسترسی یافت نشد")

    db.delete(db_key)
    db.commit()
    return MessageResponse(message="کلید دسترسی با موفقیت حذف و ابطال شد")
```

### app/api/v1/endpoints/auth.py

```python
# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, TokenResponse, UserResponse, MessageResponse, ChangePassword, UserUpdate
from app.services.auth import auth_service
from app.api.v1.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    ثبت‌نام کاربر جدید
    """
    # بررسی وجود نام کاربری تکراری
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این نام کاربری قبلاً ثبت شده است"
        )
    
    # بررسی وجود ایمیل تکراری
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این ایمیل قبلاً ثبت شده است"
        )
    
    # هش کردن رمز عبور
    hashed_password = auth_service.hash_password(user_data.password)
    
    # ایجاد کاربر جدید (is_active = False به صورت پیش‌فرض)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        phone_number=user_data.phone_number,
        is_active=False,
        is_admin=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return MessageResponse(
        message="ثبت‌نام با موفقیت انجام شد. حساب کاربری شما منتظر تایید ادمین است.",
        success=True
    )

@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    ورود کاربر به سیستم
    """
    user = db.query(User).filter(
        (User.username == login_data.username) | (User.email == login_data.username)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="نام کاربری یا رمز عبور اشتباه است"
        )
    
    if not auth_service.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="نام کاربری یا رمز عبور اشتباه است"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="حساب کاربری شما هنوز توسط ادمین تایید نشده است"
        )
    
    # تغییر اعمال‌شده: اصلاح تو رفتگی خطوط زیر
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    
    access_token = auth_service.create_access_token(user.id, user.username)
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    دریافت اطلاعات کاربر جاری
    """
    return UserResponse.model_validate(current_user)

@router.put("/me", response_model=UserResponse)
async def update_me(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ویرایش اطلاعات کاربر جاری
    """
    if user_data.full_name is not None:
        current_user.full_name = user_data.full_name
    if user_data.phone_number is not None:
        current_user.phone_number = user_data.phone_number
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    تغییر رمز عبور
    """
    if not auth_service.verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="رمز عبور فعلی اشتباه است"
        )
    
    current_user.hashed_password = auth_service.hash_password(password_data.new_password)
    db.commit()
    
    return MessageResponse(message="رمز عبور با موفقیت تغییر کرد")
```

### app/api/v1/endpoints/pois.py

```python
# app/api/v1/endpoints/pois.py
from fastapi import APIRouter, HTTPException, Query, Depends
from app.services.postgis_service import postgis_service
from app.models.api_key import APIKey
from app.api.v1.dependencies import get_api_key  # وارد کردن وابستگی کلید دسترسی

router = APIRouter()

@router.get("/nearest", summary="یافتن نزدیک‌ترین مکان‌های اطراف کاربر (POI)")
async def get_nearest_pois(
    lat: float = Query(..., description="عرض جغرافیایی کاربر"),
    lon: float = Query(..., description="طول جغرافیایی کاربر"),
    category: str = Query(None, description="دسته‌بندی مکان (مثال: fuel, atm, hospital, restaurant)"),
    radius: float = Query(5000.0, description="شعاع جستجو به متر (پیش‌فرض: ۵۰۰۰ متر)"),
    limit: int = Query(10, description="حداکثر تعداد نتایج (پیش‌فرض: ۱۰)"),
    api_key: APIKey = Depends(get_api_key)  # اجباری کردن دریافت کلید معتبر
):
    # فراخوانی متد فضایی PostGIS
    results = postgis_service.get_nearest_pois(
        lat=lat,
        lon=lon,
        category=category,
        radius_meters=radius,
        limit=limit
    )
    
    if not results:
        return []
        
    return results
```

### app/api/v1/endpoints/public_locations.py

```python
# app/api/v1/endpoints/public_locations.py
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.api_key import APIKey
from app.schemas.location import LocationCreate, LocationResponse
from app.services.location_service import location_service
from app.api.v1.dependencies import get_api_key

router = APIRouter(prefix="/locations", tags=["Public Locations"])

def parse_public_location_to_dict(loc) -> dict:
    """تبدیل ایمن آبجکت دیتابیس به دیکشنری برای Pydantic"""
    return {c.name: getattr(loc, c.name) for c in loc.__table__.columns}

@router.post("/public", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_public_location_suggestion(
    location_data: LocationCreate,
    api_key: APIKey = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    ثبت پیشنهاد موقعیت جدید توسط کاربران مهمان (بدون نیاز به لاگین)
    """
    location = location_service.create_location(db, location_data, user_id=None)
    return LocationResponse(**parse_public_location_to_dict(location))

@router.get("/search", response_model=List[LocationResponse])
async def search_and_filter_locations(
    lat: float = Query(..., description="عرض جغرافیایی مرکز جستجو"),
    lon: float = Query(..., description="طول جغرافیایی مرکز جستجو"),
    radius_km: float = Query(5.0, description="شعاع جستجو بر حسب کیلومتر"),
    is_return_usage: Optional[bool] = Query(None, description="فیلتر قابلیت مرجوعی کالا"),
    api_key: APIKey = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    موتور جستجوی همزمان جغرافیایی در یک محدوده جغرافیایی خاص
    """
    locations = location_service.search_locations(
        db=db,
        lat=lat,
        lon=lon,
        radius_km=radius_km,
        is_return_usage=is_return_usage
    )
    return [LocationResponse(**parse_public_location_to_dict(loc)) for loc in locations]

@router.get("/approved", response_model=List[LocationResponse])
async def get_approved_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    category: Optional[str] = None,
    city: Optional[str] = None,
    api_key: APIKey = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    دریافت تمام موقعیت‌های تایید شده جهت نمایش عمومی بر روی نقشه
    """
    locations = location_service.get_all_locations(
        db, skip, limit, status="approved", category=category, city=city
    )
    return [LocationResponse(**parse_public_location_to_dict(loc)) for loc in locations]
```

### app/api/v1/endpoints/reverse.py

```python
# app/api/v1/endpoints/reverse.py
import re
from fastapi import APIRouter, Query, Depends
from app.services.postgis_service import postgis_service
from app.models.api_key import APIKey
from app.api.v1.dependencies import get_api_key

router = APIRouter()

def convert_digits_to_persian(text: str) -> str:
    if not text:
        return ""
    translation = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
    return text.translate(translation)

def is_numeric_plate(text: str) -> bool:
    if not text:
        return False
    clean_text = str(text).strip()
    if re.match(r'^[\d]{2,5}$|^\d+[-\s]?\d+$', clean_text):
        return True
    persian_letters = re.findall(r'[آ-ی]', clean_text)
    if len(persian_letters) > 3:
        return False
    return any(char.isdigit() for char in clean_text) and len(clean_text) < 15

def clean_city_name(city: str) -> str:
    if not city:
        return ""
    city = re.sub(r'^شهرستان\s+', '', city)
    city = re.sub(r'^شهر\s+', '', city)
    city = re.sub(r'^بخش\s+مرکزی\s+', '', city)
    return city

def get_landmark_prefix(amenity: str, shop: str) -> str:
    """تولید توصیف‌گر فارسی هوشمند برای لندمارک‌های مجاور"""
    if amenity == 'mosque':
        return "جنب مسجد"
    elif amenity in ['hospital', 'clinic']:
        return "نزدیک بیمارستان"
    elif amenity == 'pharmacy':
        return "جنب داروخانه"
    elif amenity in ['bank', 'atm']:
        return "نزدیک بانک"
    elif amenity in ['school', 'university']:
        return "نزدیک مدرسه/دانشگاه"
    elif shop in ['supermarket', 'convenience']:
        return "جنب سوپرمارکت"
    elif shop == 'mall' or amenity == 'mall':
        return "نزدیک مرکز خرید"
    return "نزدیک"

@router.get("", summary="آدرس‌یابی معکوس هوشمند بومی و فوق دقیق")
async def reverse_geocoding(
    lat: float = Query(..., description="عرض جغرافیایی نقطه"),
    lon: float = Query(..., description="طول جغرافیایی نقطه"),
    include_poi: bool = Query(False, description="آیا نام اماکن تجاری در آدرس نمایش داده شود؟"),
    api_key: APIKey = Depends(get_api_key)
):
    # ۱. استخراج ۱۰۰٪ بومی، آفلاین و فوق‌سریع اطلاعات سلسله‌مراتبی از PostGIS دیتابیس iran_map
    smart_result = postgis_service.smart_reverse_geocode(lat=lat, lon=lon)
    
    if not smart_result:
        return {"address": "آدرسی یافت نشد", "source_type": "none"}

    # ۲. ساختاردهی آدرس سلسله‌مراتب کارتوگرافی بومی ایران
    parts = []
    
    # الف) استان
    if smart_result.get('province'):
        province = re.sub(r'^استان\s+', '', smart_result['province'])
        parts.append(province)
    
    # ب) شهر
    if smart_result.get('city'):
        city = clean_city_name(smart_result['city'])
        parts.append(city)
    
    # ج) منطقه شهرداری
    if smart_result.get('district'):
        district = smart_result['district'].replace(" شهر تهران", "").replace("منطقه ", "منطقهٔ ")
        parts.append(district)

    # د) محله دقیق
    if smart_result.get('neighbourhood'):
        neighbourhood = smart_result['neighbourhood']
        if not neighbourhood.startswith("محلهٔ") and not neighbourhood.startswith("شهر"):
            parts.append(f"محلهٔ {neighbourhood}")
        else:
            parts.append(neighbourhood)

    # هـ) بزرگراه / بلوار شریانی اصلی
    if smart_result.get('highway_street'):
        parts.append(smart_result['highway_street'])

    # و) خیابان اصلی
    if smart_result.get('major_street'):
        major_street = smart_result['major_street']
        if major_street != smart_result.get('highway_street'):
            parts.append(major_street)

    # ز) معبر فرعی (کوچه / بن‌بست)
    if smart_result.get('minor_street'):
        minor_street = smart_result['minor_street']
        if minor_street != smart_result.get('major_street') and minor_street != smart_result.get('highway_street'):
            parts.append(minor_street)

    # ح) نام مجتمع مسکونی، اداری، تجاری یا برج
    if smart_result.get('building_name'):
        parts.append(smart_result['building_name'])

    # ط) پلاک خانه
    if smart_result.get('house_number'):
        house_num = smart_result['house_number']
        if is_numeric_plate(str(house_num)):
            persian_plate = convert_digits_to_persian(str(house_num))
            parts.append(f"پلاک {persian_plate}")

    # ی) توصیف‌گر موقعیت نسبی مجاور (لندمارک)
    if smart_result.get('landmark_name'):
        prefix = get_landmark_prefix(
            smart_result.get('landmark_amenity') or '', 
            smart_result.get('landmark_shop') or ''
        )
        parts.append(f"{prefix} {smart_result['landmark_name']}")

    # ساخت آدرس زنجیره‌ای کامل فارسی
    final_address = "، ".join(parts)

    response = {
        "address": final_address,
        "nearest_street": smart_result.get('minor_street') or smart_result.get('major_street') or smart_result.get('highway_street'),
        "parent_street": smart_result.get('major_street') or smart_result.get('highway_street'),
        "building_name": smart_result.get('building_name'),
        "landmark": f"{prefix} {smart_result['landmark_name']}" if smart_result.get('landmark_name') else None,
        "distance_to_street_meters": smart_result.get('distance'),
        "confidence_score": smart_result.get('final_score'),
        "source_type": smart_result.get('source_type'),
    }
    
    return response
```

### app/api/v1/endpoints/route.py

```python
# app/api/v1/endpoints/route.py
from fastapi import APIRouter, Depends, Query
from app.api.v1.dependencies import get_api_key
from app.models.api_key import APIKey
from app.services.osrm_service import osrm_service

router = APIRouter(prefix="/route", tags=["Routing"])

@router.get("/directions", summary="مسیریابی هوشمند و سخنگوی جاده‌ای ایران")
async def get_directions(
    start_lat: float = Query(..., description="عرض جغرافیایی مبدا"),
    start_lon: float = Query(..., description="طول جغرافیایی مبدا"),
    end_lat: float = Query(..., description="عرض جغرافیایی مقصد"),
    end_lon: float = Query(..., description="طول جغرافیایی مقصد"),
    api_key: APIKey = Depends(get_api_key) # 🔒 تفویض امنیت و بررسی اعتبار کلید دسترسی و Rate Limit
):
    """
    استعلام مسیر جاده‌ای خودرویی بین دو نقطه مبدا و مقصد به همراه لیست گام‌به‌گام خیابان‌ها
    """
    route_data = await osrm_service.get_route(
        start_lat=start_lat,
        start_lon=start_lon,
        end_lat=end_lat,
        end_lon=end_lon
    )
    return route_data
```

### app/api/v1/endpoints/search.py

```python
# app/api/v1/endpoints/search.py
from enum import Enum
from fastapi import APIRouter, HTTPException, Query, Depends
from app.services.nominatim import nominatim_service
from app.models.api_key import APIKey
from app.api.v1.dependencies import get_api_key  # وارد کردن وابستگی کلید دسترسی

router = APIRouter()

# تعریف حالت‌های مجاز جستجو به صورت Enum جهت ولیدیشن خودکار و منوی کشویی در Swagger
class SearchMode(str, Enum):
    global_search = "global"
    proximity_search = "proximity"
    viewport_search = "viewport"
    city_search = "city"

@router.get("/", summary="موتور جستجوی هوشمند چندحالته نقشه ایران")
async def search_address(
    q: str = Query(..., description="متن مورد جستجو (مثال: رستوران، آزادی)"),
    mode: SearchMode = Query(SearchMode.global_search, description="حالت جستجو: یکی از موارد مجاز کشویی"),
    lat: float = Query(None, description="عرض جغرافیایی (برای حالت proximity)"),
    lon: float = Query(None, description="طول جغرافیایی (برای حالت proximity)"),
    viewbox: str = Query(None, description="کادر نقشه فعلی به فرمت minLon,maxLat,maxLon,minLat (برای حالت viewport)"),
    city: str = Query(None, description="نام شهر مشخص جهت محدودسازی نتایج (برای حالت city)"),
    api_key: APIKey = Depends(get_api_key)  # اجباری کردن ارائه کلید معتبر
):
    # بررسی ولیدیشن منطقی پارامترها بر اساس Enum انتخاب شده
    if mode == SearchMode.proximity_search and (lat is None or lon is None):
        raise HTTPException(status_code=400, detail="برای جستجوی اطراف لوکیشن، ارسال lat و lon الزامی است.")
        
    if mode == SearchMode.viewport_search and viewbox is None:
        raise HTTPException(status_code=400, detail="برای جستجوی کادر نقشه، ارسال پارامتر viewbox الزامی است.")
        
    if mode == SearchMode.city_search and city is None:
        raise HTTPException(status_code=400, detail="برای جستجوی مقید به شهر، ارسال پارامتر city الزامی است.")

    try:
        # مقدار واقعی متنی Enum با ویژگی mode.value ارسال می‌شود
        results = nominatim_service.search_places(
            query=q,
            mode=mode.value, 
            lat=lat,
            lon=lon,
            viewbox=viewbox,
            city=city
        )
        return results
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
```

### app/api/v1/endpoints/styles.py

```python
# app/api/v1/endpoints/styles.py
import os
import json
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from app.api.v1.dependencies import get_api_key
from app.models.api_key import APIKey

router = APIRouter(prefix="/styles", tags=["Map Styles"])

# بررسی هوشمند و چندمرحله‌ای آدرس‌های احتمالی فایل روی هارد (با پشتیبانی از پوشه ریشه OSM شما)
possible_paths = [
    # ۱. مسیر ریشه اصلی پروژه OSM شما (C:\Users\Raven\OSM\styles\default.json)
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))), "styles", "default.json"),
    # ۲. مسیر نسبی مستقیم ریشه
    "./styles/default.json",
    # ۳. مسیر استاندارد در پوشه static/styles روت app
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "static", "styles", "default.json"),
    # ۴. مسیر مستقیم نسبی در فرآیند اجرای uvicorn
    "./app/static/styles/default.json"
]

# پیدا کردن مسیر معتبر فعال روی سیستم شما
STYLE_FILE_PATH = None
for path in possible_paths:
    if os.path.exists(path):
        STYLE_FILE_PATH = path
        break

@router.get("/default", summary="ارائه پویا و امن فایل استایل نقشه برداری")
async def get_default_style(
    request: Request,
    api_key: APIKey = Depends(get_api_key) # 🔒 بررسی اعتبار کلید دسترسی
):
    """
    سرویس‌دهی پویای استایل نقشه به اپلیکیشن موبایل یا فرانت وب بر اساس آی‌پی کلاینت و کلید فعال
    """
    # اگر فایل در هیچ‌کدام از مسیرها پیدا نشد
    if STYLE_FILE_PATH is None:
        raise HTTPException(
            status_code=404, 
            detail="فایل استایل default.json یافت نشد. مطمئن شوید فایل را در مسیر OSM/styles/default.json ساخته‌اید."
        )
    
    try:
        # ۱. خواندن فایل خام
        with open(STYLE_FILE_PATH, "r", encoding="utf-8") as f:
            style_content = f.read()
        
        # ۲. محاسبه خودکار آدرس دامنه و پورت پایتون به صورت داینامیک
        base_url = f"{request.url.scheme}://{request.url.netloc}/api/v1"
        
        # ۳. جایگذاری هوشمند آدرس‌ها و کلید دسترسی کلاینت در داخل مشخصات استایل
        style_content = style_content.replace("{{BASE_URL}}", base_url)
        style_content = style_content.replace("{{API_KEY}}", api_key.key)
        
        # ۴. بازگرداندن فایل نهایی به صورت فرمت استاندارد JSON
        return JSONResponse(content=json.loads(style_content))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در پردازش فایل استایل نقشه: {str(e)}")
```

### app/api/v1/endpoints/tiles.py

```python
# app/api/v1/endpoints/tiles.py
from fastapi import APIRouter, Response, HTTPException, Depends, Request
from app.services.tile_service import tile_service
from app.api.v1.dependencies import get_api_key
from app.models.api_key import APIKey

router = APIRouter()

@router.get("/{table}.json", summary="دریافت خودکار و استاندارد مشخصات TileJSON")
async def get_tile_json(
    request: Request,
    table: str,
    api_key: APIKey = Depends(get_api_key)
):
    base_url = f"{request.url.scheme}://{request.url.netloc}/api/v1"
    return {
        "tilejson": "2.2.0",
        "name": f"Vector Source: {table}",
        "tiles": [
            f"{base_url}/tiles/{table}/{{z}}/{{x}}/{{y}}?api_key={api_key.key}"
        ],
        "minzoom": 0,
        "maxzoom": 18,
        "bounds": [-180.0, -85.0, 180.0, 85.0],
        "type": "vector"
    }

@router.get("/{table}/{z}/{x}/{y}", summary="دریافت تایل‌های برداری نقشه")
async def get_tile(
    table: str, 
    z: str, 
    x: str, 
    y: str,
    api_key: APIKey = Depends(get_api_key)
):
    # پاسخ هوشمند به تست‌های اولیه مپوتنیک
    if not (z.isdigit() and x.isdigit() and y.isdigit()):
        return Response(content=b"", media_type="application/x-protobuf")
    
    # تبدیل به عدد صحیح
    z_int = int(z)
    x_int = int(x)
    y_int = int(y)

    # دریافت تایل برداری از دیتابیس PostGIS
    tile_bytes, headers = await tile_service.get_vector_tile(table, z_int, x_int, y_int)
    
    # اگر تایل فاقد داده بود، پاسخ 200 خالی بازگردان
    if not tile_bytes:
        return Response(
            content=b"",
            media_type="application/x-protobuf",
            headers={"Cache-Control": "public, max-age=86400"}
        )

    # ادغام هوشمند هدرها و حذف هدرهای طول، فشرده‌سازی و انتقال تداخل‌دار (حل قطعی کراش‌های دکودینگ)
    response_headers = {**headers} if headers else {}
    response_headers.pop("Content-Length", None)
    response_headers.pop("content-length", None)
    
    # 🔑 حذف هدر فشرده‌سازی قدیمی چون httpx خودش فایل را از حالت فشرده خارج کرده است
    response_headers.pop("Content-Encoding", None)
    response_headers.pop("content-encoding", None)
    response_headers.pop("Transfer-Encoding", None)
    response_headers.pop("transfer-encoding", None)
    
    response_headers["Cache-Control"] = "public, max-age=86400"

    return Response(
        content=tile_bytes,
        media_type="application/x-protobuf",
        headers=response_headers
    )
```

### app/api/v1/endpoints/user_locations.py

```python
# app/api/v1/endpoints/user_locations.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User
from app.schemas.location import LocationCreate, LocationUpdate, LocationResponse, MessageResponse
from app.services.location_service import location_service
from app.api.v1.dependencies import get_current_user

router = APIRouter(prefix="/user/locations", tags=["User Locations"])

def parse_user_location_to_dict(loc) -> dict:
    """تبدیل ایمن آبجکت دیتابیس به دیکشنری برای ارسال به Pydantic"""
    return {c.name: getattr(loc, c.name) for c in loc.__table__.columns}

@router.post("/", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_user_location(
    location_data: LocationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ثبت موقعیت مکانی انبار/فروشگاه جدید توسط کاربر لاگین شده
    """
    location = location_service.create_location(db, location_data, current_user.id)
    return LocationResponse(**parse_user_location_to_dict(location))

@router.get("/", response_model=List[LocationResponse])
async def get_my_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None, description="pending, approved, rejected"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    دریافت موقعیت‌های ثبت شده توسط خود کاربر جاری
    """
    locations = location_service.get_user_locations(db, current_user.id, skip, limit, status)
    return [LocationResponse(**parse_user_location_to_dict(loc)) for loc in locations]

@router.get("/{location_id}", response_model=LocationResponse)
async def get_my_location_detail(
    location_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    دریافت جزئیات کامل یکی از موقعیت‌های انبار شخصی
    """
    location = location_service.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="موقعیت یافت نشد")
    if location.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="شما دسترسی به این موقعیت ندارید")
    return LocationResponse(**parse_user_location_to_dict(location))

@router.put("/{location_id}", response_model=LocationResponse)
async def update_my_location(
    location_id: int,
    location_data: LocationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ویرایش موقعیت شخصی (فقط اگر انبار در وضعیت pending باشد قابل ویرایش است)
    """
    location = location_service.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="موقعیت یافت نشد")
    if location.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="شما دسترسی به این موقعیت ندارید")
    if location.status != "pending":
        raise HTTPException(status_code=400, detail="فقط موقعیت‌های در انتظار تایید قابل ویرایش هستند")
    
    updated = location_service.update_location(db, location_id, location_data)
    return LocationResponse(**parse_user_location_to_dict(updated))

@router.delete("/{location_id}", response_model=MessageResponse)
async def delete_my_location(
    location_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    حذف موقعیت شخصی (فقط اگر انبار در وضعیت pending باشد قابل حذف است)
    """
    location = location_service.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="موقعیت یافت نشد")
    if location.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="شما دسترسی به این موقعیت ندارید")
    if location.status != "pending":
        raise HTTPException(status_code=400, detail="فقط موقعیت‌های در انتظار تایید قابل حذف هستند")
    
    location_service.delete_location(db, location_id)
    return MessageResponse(message="موقعیت با موفقیت حذف شد", location_id=location_id)
```

### app/api/v2/router.py

```python
# c:\Users\Raven\OSM\app\api\v2\router.py
from fastapi import APIRouter

from app.api.v2.endpoints.map import router as map_router
from app.api.v2.endpoints.stores import router as stores_router
from app.api.v2.endpoints.warehouses import router as warehouse_router
from app.api.v2.endpoints.inventory import router as inventory_router
from app.api.v2.endpoints.auth import router as auth_router

router = APIRouter()

router.include_router(map_router)
router.include_router(stores_router)
router.include_router(warehouse_router)
router.include_router(inventory_router)
router.include_router(auth_router)
```

### app/api/v2/core/__init__.py

```python

```

### app/api/v2/core/config.py

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "OSM Map Platform"
    VERSION: str = "2.0.0"

    API_V1_STR: str = "/api/v1"

    POSTGRES_URL: str = "postgresql://user:pass@localhost:5432/osm"

    JWT_SECRET: str = "change_me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    NOMINATIM_URL: str = "http://localhost:8080"
    OSRM_URL: str = "http://localhost:5000"
    MARTIN_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
```

### app/api/v2/core/deps.py

```python
from app.core.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### app/api/v2/endpoints/admin.py

```python

```

### app/api/v2/endpoints/auth.py

```python
# c:\Users\Raven\OSM\app\api\v2\endpoints\auth.py
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import APIRouter, Response, HTTPException, Cookie, Depends

from app.api.v2.schemas.auth import UserLogin, UserResponse
from app.api.v2.services.auth_service import verify_password, create_access_token, decode_access_token

DB_CONNECTION = "host=localhost port=5433 dbname=iran_map user=map_admin password=map_secure_pass"

router = APIRouter(prefix="/auth", tags=["Authentication"])


async def get_current_user(access_token: str | None = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    payload = decode_access_token(access_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token or session expired")
        
    user_id = payload.get("user_id")
    
    try:
        conn = psycopg2.connect(DB_CONNECTION)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id, username, full_name, role, is_active FROM users WHERE id=%s;", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        if not user["is_active"]:
            raise HTTPException(status_code=401, detail="User is inactive")
            
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/login")
async def login_endpoint(payload: UserLogin, response: Response):
    try:
        conn = psycopg2.connect(DB_CONNECTION)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id, username, password_hash, full_name, role, is_active FROM users WHERE username=%s;", (payload.username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            raise HTTPException(status_code=401, detail="Incorrect username or password")
            
        if not verify_password(user["password_hash"], payload.password):
            raise HTTPException(status_code=401, detail="Incorrect username or password")
            
        if not user["is_active"]:
            raise HTTPException(status_code=401, detail="Account is inactive")
            
        token_data = {"user_id": user["id"], "username": user["username"], "role": user["role"]}
        token = create_access_token(token_data)
        
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            max_age=14400,
            samesite="lax"
        )
        
        return {"status": "success", "user": {"id": user["id"], "username": user["username"], "role": user["role"]}}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/logout")
async def logout_endpoint(response: Response):
    response.delete_cookie("access_token")
    return {"status": "success", "detail": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me_endpoint(current_user: dict = Depends(get_current_user)):
    return current_user
```

### app/api/v2/endpoints/inventory.py

```python
# c:\Users\Raven\OSM\app\api\v2\endpoints\inventory.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v2.core.deps import get_db
from app.api.v2.schemas.inventory import InventoryCreate
from app.api.v2.services.inventory_service import (
    add_inventory,
    get_inventory
)
from app.api.v2.endpoints.auth import get_current_user

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.post("/{warehouse_id}")
def create(warehouse_id: int, data: InventoryCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["super_admin", "warehouse_manager"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    return add_inventory(db, warehouse_id, data)


@router.get("/{warehouse_id}")
def list_items(warehouse_id: int, db: Session = Depends(get_db)):
    return get_inventory(db, warehouse_id)
```

### app/api/v2/endpoints/locations.py

```python

```

### app/api/v2/endpoints/map.py

```python
# c:\Users\Raven\OSM\app\api\v2\endpoints\map.py
import os
import json
import urllib.request
import psycopg2
from fastapi import APIRouter, Response, HTTPException, Query

from app.api.v2.schemas.map import RouteRequest, RouteOptimizeRequest, PublicPublishRequest
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
            INSERT INTO stores (id, name, lat, lon, address, phone) 
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) 
            DO UPDATE SET 
                name = EXCLUDED.name, 
                lat = EXCLUDED.lat, 
                lon = EXCLUDED.lon, 
                address = EXCLUDED.address, 
                phone = EXCLUDED.phone
            RETURNING id, name, lat, lon, address, phone;
            """,
            (str(payload.id), payload.name, payload.lat, payload.lon, payload.address, payload.phone)
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
                "lon": updated_store[3]
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
```

### app/api/v2/endpoints/stores.py

```python
# c:\Users\Raven\OSM\app\api\v2\endpoints\stores.py
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel

from app.api.v2.schemas.store import StoreCreate, StoreUpdate, StoreResponse
from app.core.database import get_db
from app.api.v2.endpoints.auth import get_current_user

router = APIRouter(prefix="/stores", tags=["Stores"])


class AdminNotesRequest(BaseModel):
    admin_notes: str


@router.post("/", response_model=StoreResponse)
def create(store: StoreCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    
    new_uuid = str(uuid.uuid4())
    shop_id_str = str(store.shop_id) if store.shop_id else None
    
    try:
        db.execute(
            text(
                "INSERT INTO stores (id, name, lat, lon, address, phone, user_id, status, shop_id) "
                "VALUES (:id, :name, :lat, :lon, :address, :phone, :user_id, 'Approved', :shop_id) "
                "RETURNING id, name, lat, lon, address, phone, user_id, shop_id;"
            ),
            {
                "id": new_uuid,
                "name": store.name,
                "lat": store.lat,
                "lon": store.lon,
                "address": store.address,
                "phone": store.phone,
                "user_id": current_user["id"],
                "shop_id": shop_id_str
            }
        )
        db.commit()
        
        result = db.execute(
            text("SELECT id, name, lat, lon, address, phone, user_id, status, admin_notes, shop_id FROM stores WHERE id = :id;"),
            {"id": new_uuid}
        )
        return result.mappings().one()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[StoreResponse])
def list_stores(db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT id, name, lat, lon, address, phone, user_id, status, admin_notes, shop_id FROM stores WHERE status = 'Approved';")
    ).mappings().all()
    return result


@router.get("/admin/pending", response_model=list[StoreResponse])
def list_pending_stores(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    result = db.execute(
        text("SELECT id, name, lat, lon, address, phone, user_id, status, admin_notes, shop_id FROM stores WHERE status = 'Pending';")
    ).mappings().all()
    return result


@router.put("/{store_id}/approve", response_model=StoreResponse)
def approve(store_id: str, payload: AdminNotesRequest, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    
    check_store = db.execute(
        text("SELECT id FROM stores WHERE id = :store_id;"),
        {"store_id": store_id}
    ).fetchone()
    
    if not check_store:
        raise HTTPException(status_code=404, detail="Store not found")
        
    db.execute(
        text("UPDATE stores SET status = 'Approved', admin_notes = :admin_notes WHERE id = :store_id;"),
        {"admin_notes": payload.admin_notes, "store_id": store_id}
    )
    db.commit()
    
    result = db.execute(
        text("SELECT id, name, lat, lon, address, phone, user_id, status, admin_notes, shop_id FROM stores WHERE id = :store_id;"),
        {"store_id": store_id}
    )
    return result.mappings().one()


@router.put("/{store_id}/reject", response_model=StoreResponse)
def reject(store_id: str, payload: AdminNotesRequest, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Permission denied")
        
    check_store = db.execute(
        text("SELECT id FROM stores WHERE id = :store_id;"),
        {"store_id": store_id}
    ).fetchone()
    
    if not check_store:
        raise HTTPException(status_code=404, detail="Store not found")
        
    db.execute(
        text("UPDATE stores SET status = 'Rejected', admin_notes = :admin_notes WHERE id = :store_id;"),
        {"admin_notes": payload.admin_notes, "store_id": store_id}
    )
    db.commit()
    
    result = db.execute(
        text("SELECT id, name, lat, lon, address, phone, user_id, status, admin_notes, shop_id FROM stores WHERE id = :store_id;"),
        {"store_id": store_id}
    )
    return result.mappings().one()


@router.get("/{store_id}", response_model=StoreResponse)
def get(store_id: str, db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT id, name, lat, lon, address, phone, user_id, status, admin_notes, shop_id FROM stores WHERE id = :store_id;"),
        {"store_id": store_id}
    )
    store = result.mappings().one_or_none()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store


@router.put("/{store_id}", response_model=StoreResponse)
def update(store_id: str, data: StoreUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    
    update_fields = []
    update_values = {}
    
    for field, value in data.dict(exclude_unset=True).items():
        if field == "shop_id":
            update_fields.append("shop_id = :shop_id")
            update_values["shop_id"] = str(value) if value else None
        else:
            update_fields.append(f"{field} = :{field}")
            update_values[field] = value
        
    if update_fields:
        update_values["store_id"] = store_id
        sql = f"UPDATE stores SET {', '.join(update_fields)} WHERE id = :store_id;"
        db.execute(text(sql), update_values)
        db.commit()
        
    result = db.execute(
        text("SELECT id, name, lat, lon, address, phone, user_id, status, admin_notes, shop_id FROM stores WHERE id = :store_id;"),
        {"store_id": store_id}
    )
    return result.mappings().one()


@router.delete("/{store_id}")
def delete(store_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Permission denied")
        
    db.execute(text("DELETE FROM stores WHERE id = :store_id;"), {"store_id": store_id})
    db.commit()
    return {"message": "deleted"}
```

### app/api/v2/endpoints/warehouses.py

```python
# c:\Users\Raven\OSM\app\api\v2\endpoints\warehouses.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from app.api.v2.schemas.warehouse import WarehouseCreate, WarehouseUpdate, WarehouseResponse
from app.core.database import get_db
from app.api.v2.endpoints.auth import get_current_user

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])


@router.post("/{store_id}", response_model=WarehouseResponse)
def create(store_id: str, warehouse: WarehouseCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        db.execute(
            text(
                "INSERT INTO warehouses (name, lat, lon, address, phone, store_id) "
                "VALUES (:name, :lat, :lon, :address, :phone, :store_id);"
            ),
            {
                "name": warehouse.name,
                "lat": warehouse.lat,
                "lon": warehouse.lon,
                "address": warehouse.address,
                "phone": warehouse.phone,
                "store_id": store_id
            }
        )
        db.commit()
        
        result = db.execute(
            text("SELECT id, name, lat, lon, address, phone, store_id FROM warehouses WHERE store_id = :store_id ORDER BY id DESC LIMIT 1;"),
            {"store_id": store_id}
        )
        return result.mappings().one()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{store_id}", response_model=List[WarehouseResponse])
def list_warehouses(store_id: str, db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT id, name, lat, lon, address, phone, store_id FROM warehouses WHERE store_id = :store_id;"),
        {"store_id": store_id}
    ).mappings().all()
    return result


@router.get("/detail/{warehouse_id}", response_model=WarehouseResponse)
def get(warehouse_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT id, name, lat, lon, address, phone, store_id FROM warehouses WHERE id = :warehouse_id;"),
        {"warehouse_id": warehouse_id}
    )
    warehouse = result.mappings().one_or_none()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse


@router.put("/{warehouse_id}", response_model=WarehouseResponse)
def update(warehouse_id: int, data: WarehouseUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["super_admin", "warehouse_manager"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    update_fields = []
    update_values = {}
    for field, value in data.dict(exclude_unset=True).items():
        update_fields.append(f"{field} = :{field}")
        update_values[field] = value
        
    if update_fields:
        update_values["warehouse_id"] = warehouse_id
        sql = f"UPDATE warehouses SET {', '.join(update_fields)} WHERE id = :warehouse_id;"
        db.execute(text(sql), update_values)
        db.commit()
        
    result = db.execute(
        text("SELECT id, name, lat, lon, address, phone, store_id FROM warehouses WHERE id = :warehouse_id;"),
        {"warehouse_id": warehouse_id}
    )
    return result.mappings().one()


@router.delete("/{warehouse_id}")
def delete(warehouse_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Permission denied")
        
    db.execute(text("DELETE FROM warehouses WHERE id = :warehouse_id;"), {"warehouse_id": warehouse_id})
    db.commit()
    return {"message": "Warehouse deleted successfully"}
```

### app/api/v2/models/__init__.py

```python
from app.api.v2.models.user import User
from app.api.v2.models.store import Store
from app.api.v2.models.warehouse import Warehouse
from app.api.v2.models.inventory import Inventory
from app.api.v2.models.product import Product

__all__ = ["User", "Store", "Warehouse", "Inventory", "Product"]
```

### app/api/v2/models/base.py

```python
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime, func

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
```

### app/api/v2/models/inventory.py

```python
from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.api.v2.models.base import Base, TimestampMixin

class Inventory(Base, TimestampMixin):
    __tablename__ = "inventories"
    
    id = Column(Integer, primary_key=True, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity = Column(Float, default=0)
    min_stock = Column(Float, default=0)
    max_stock = Column(Float, default=0)
    
    warehouse = relationship("Warehouse", back_populates="inventories")
    product = relationship("Product", back_populates="inventories")
```

### app/api/v2/models/product.py

```python
from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.orm import relationship
from app.api.v2.models.base import Base, TimestampMixin

class Product(Base, TimestampMixin):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    price = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    
    inventories = relationship("Inventory", back_populates="product", cascade="all, delete-orphan")
```

### app/api/v2/models/store.py

```python
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.api.v2.models.base import Base, TimestampMixin

class Store(Base, TimestampMixin):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    user = relationship("User", back_populates="stores")
    warehouses = relationship("Warehouse", back_populates="store", cascade="all, delete-orphan")
```

### app/api/v2/models/store_product.py

```python
from sqlalchemy import Column, Integer, ForeignKey
from app.api.v2.models.base import Base


class StoreProduct(Base):
    __tablename__ = "store_products"

    store_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, primary_key=True)
```

### app/api/v2/models/user.py

```python
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.api.v2.models.base import Base, TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    stores = relationship("Store", back_populates="user", cascade="all, delete-orphan")
```

### app/api/v2/models/warehouse.py

```python
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.api.v2.models.base import Base, TimestampMixin

class Warehouse(Base, TimestampMixin):
    __tablename__ = "warehouses"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    
    store = relationship("Store", back_populates="warehouses")
    inventories = relationship("Inventory", back_populates="warehouse", cascade="all, delete-orphan")
```

### app/api/v2/schemas/auth.py

```python
# c:\Users\Raven\OSM\app\api\v2\schemas\auth.py
from pydantic import BaseModel


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str | None = None
    role: str
    is_active: bool

    class Config:
        from_attributes = True
```

### app/api/v2/schemas/inventory.py

```python
from pydantic import BaseModel


class InventoryCreate(BaseModel):
    product_id: int
    quantity: int = 0


class InventoryOut(BaseModel):
    id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True
```

### app/api/v2/schemas/map.py

```python
# c:\Users\Raven\OSM\app\api\v2\schemas\map.py
from pydantic import BaseModel
from typing import List
from uuid import UUID


class RouteRequest(BaseModel):
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float


class LocationCoordinate(BaseModel):
    lat: float
    lon: float


class RouteOptimizeRequest(BaseModel):
    locations: List[LocationCoordinate]


class PublicPublishRequest(BaseModel):
    id: UUID
    name: str
    lat: float
    lon: float
    address: str
    phone: str
```

### app/api/v2/schemas/settings.py

```python
# c:\Users\Raven\OSM\app\api\v2\schemas\settings.py
from pydantic import BaseModel


class SettingsUpdate(BaseModel):
    map_pitch: float
    map_bearing: float
    map_zoom: float
    building_multiplier: float
    trigram_threshold: float
    avoid_traffic_zones: bool
    traffic_time_multiplier: float


class SettingsResponse(SettingsUpdate):
    id: int

    class Config:
        from_attributes = True
```

### app/api/v2/schemas/store.py

```python
# c:\Users\Raven\OSM\app\api\v2\schemas\store.py
from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class StoreBase(BaseModel):
    name: str
    lat: float
    lon: float
    address: Optional[str] = None
    phone: Optional[str] = None
    shop_id: Optional[UUID] = None


class StoreCreate(StoreBase):
    pass


class StoreUpdate(BaseModel):
    name: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    shop_id: Optional[UUID] = None


class StoreResponse(StoreBase):
    id: UUID
    user_id: Optional[int] = None
    status: Optional[str] = None
    admin_notes: Optional[str] = None

    class Config:
        from_attributes = True
```

### app/api/v2/schemas/warehouse.py

```python
# c:\Users\Raven\OSM\app\api\v2\schemas\warehouse.py
from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class WarehouseBase(BaseModel):
    name: str
    lat: float
    lon: float
    address: Optional[str] = None
    phone: Optional[str] = None


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    address: Optional[str] = None
    phone: Optional[str] = None


class WarehouseResponse(WarehouseBase):
    id: int
    store_id: UUID

    class Config:
        from_attributes = True
```

### app/api/v2/services/auth_client.py

```python
import httpx


AUTH_BASE_URL = "http://localhost:8001"  # سرویس auth جدا


async def get_user(user_id: int):
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.get(f"{AUTH_BASE_URL}/users/{user_id}")

        if r.status_code != 200:
            return None

        return r.json()
```

### app/api/v2/services/auth_service.py

```python
# c:\Users\Raven\OSM\app\api\v2\services\auth_service.py
import hashlib
import os
import hmac
import base64
import json
import time

SECRET_KEY = "yadakchi_super_secret_key_change_me_in_production"


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return salt.hex() + ":" + key.hex()


def verify_password(stored_password: str, provided_password: str) -> bool:
    try:
        salt_hex, key_hex = stored_password.split(":")
        salt = bytes.fromhex(salt_hex)
        key = bytes.fromhex(key_hex)
        new_key = hashlib.pbkdf2_hmac("sha256", provided_password.encode("utf-8"), salt, 100000)
        return hmac.compare_digest(key, new_key)
    except Exception:
        return False


def base64_url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").replace("=", "")


def base64_url_decode(data: str) -> bytes:
    padding = "=" * (4 - (len(data) % 4))
    return base64.urlsafe_b64decode(data + padding)


def create_access_token(data: dict, expires_in: int = 14400) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = data.copy()
    payload["exp"] = int(time.time()) + expires_in
    
    header_json = json.dumps(header).encode("utf-8")
    payload_json = json.dumps(payload).encode("utf-8")
    
    unsigned_token = base64_url_encode(header_json) + "." + base64_url_encode(payload_json)
    signature = hmac.new(SECRET_KEY.encode("utf-8"), unsigned_token.encode("utf-8"), hashlib.sha256).digest()
    
    return unsigned_token + "." + base64_url_encode(signature)


def decode_access_token(token: str) -> dict | None:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
            
        unsigned_token = parts[0] + "." + parts[1]
        signature = base64_url_decode(parts[2])
        
        expected_signature = hmac.new(SECRET_KEY.encode("utf-8"), unsigned_token.encode("utf-8"), hashlib.sha256).digest()
        if not hmac.compare_digest(signature, expected_signature):
            return None
            
        payload_json = base64_url_decode(parts[1])
        payload = json.loads(payload_json.decode("utf-8"))
        
        if payload.get("exp", 0) < int(time.time()):
            return None
            
        return payload
    except Exception:
        return None
```

### app/api/v2/services/inventory_service.py

```python
from app.api.v2.models.inventory import Inventory


def add_inventory(db, warehouse_id: int, data):
    item = Inventory(
        warehouse_id=warehouse_id,
        product_id=data.product_id,
        quantity=data.quantity
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_inventory(db, warehouse_id: int):
    return db.query(Inventory).filter(
        Inventory.warehouse_id == warehouse_id
    ).all()
```

### app/api/v2/services/reverse_service.py

```python
# c:\Users\Raven\OSM\app\api\v2\services\reverse_service.py
"""
Reverse Geocoder — نسخه Hybrid addr:* + Interpolation
=====================================================
روش کار:
  ۱. addr_context  : نزدیک‌ترین نقطه یا ساختمان که addr:street/quarter/suburb داره
  ۲. snapped       : نزدیک‌ترین خیابان با وزن‌دهی (با یا بدون name)
  ۳. street_chain  : زنجیره خیابان‌ها از توپولوژی OSM (تا ۴ سطح)
  ۴. interpolation : وقتی snapped بدون name بود، از addr:street جایگزین می‌کنیم
  ۵. boundaries    : مرزهای اداری با اولویت‌بندی area
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import re
import time
from dataclasses import dataclass
from typing import Any

import asyncpg
import structlog

# ─── تنظیمات ──────────────────────────────────────────────────────────────────
DB_DSN               = "postgresql://map_admin:map_secure_pass@localhost:5433/iran_map"
POOL_MIN_SIZE        = 2
POOL_MAX_SIZE        = 10
POOL_COMMAND_TIMEOUT = 8.0

CACHE_MAX_SIZE       = 4096
CACHE_TTL_SEC        = 3600
CACHE_GRID_DEG       = 0.0001

ADDR_CONTEXT_RADIUS  = 120   # شعاع جستجو برای addr_context (متر)
CHAIN_SNAP_RADIUS    = 8     # شعاع اتصال بین خیابان‌ها در زنجیره (متر)

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.BoundLogger,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)
log = structlog.get_logger("reverse_geocoder")


# ─── مدل خروجی ────────────────────────────────────────────────────────────────
@dataclass
class ReverseResult:
    address: str
    province: str | None        = None
    city: str | None            = None
    district: str | None        = None
    neighbourhood: str | None   = None
    street_level1: str | None   = None   # بلوار / بزرگراه
    street_level2: str | None   = None   # خیابان اصلی
    street_level3: str | None   = None   # کوچه
    street_level4: str | None   = None   # کوچه فرعی‌تر
    building_name: str | None   = None
    house_number: str | None    = None
    landmark: str | None        = None
    distance_to_street_m: float | None = None
    addr_source: str | None     = None   # osm_line | addr_interpolated
    traffic_zone: str | None    = None
    confidence: float           = 1.0
    source_type: str            = "hybrid_v1"
    cached: bool                = False
    elapsed_ms: float           = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


# ─── خطاها ────────────────────────────────────────────────────────────────────
class GeocoderError(Exception): pass
class DatabaseError(GeocoderError): pass
class NoResultError(GeocoderError): pass


# ─── connection pool ───────────────────────────────────────────────────────────
_pool: asyncpg.Pool | None = None
_pool_lock = asyncio.Lock()


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is not None:
        return _pool
    async with _pool_lock:
        if _pool is None:
            try:
                _pool = await asyncpg.create_pool(
                    dsn=DB_DSN,
                    min_size=POOL_MIN_SIZE,
                    max_size=POOL_MAX_SIZE,
                    command_timeout=POOL_COMMAND_TIMEOUT,
                )
                log.info("db_pool_created")
            except Exception as e:
                raise DatabaseError("db pool failed") from e
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


# ─── cache ────────────────────────────────────────────────────────────────────
@dataclass
class _CacheEntry:
    result: ReverseResult
    expires_at: float


class _GeoCache:
    def __init__(self, max_size: int, ttl: float) -> None:
        self._store: dict[str, _CacheEntry] = {}
        self._max_size = max_size
        self._ttl = ttl

    def _key(self, lat: float, lon: float) -> str:
        glat = round(lat / CACHE_GRID_DEG) * CACHE_GRID_DEG
        glon = round(lon / CACHE_GRID_DEG) * CACHE_GRID_DEG
        return hashlib.md5(f"{glat:.6f},{glon:.6f}".encode()).hexdigest()

    def get(self, lat: float, lon: float) -> ReverseResult | None:
        key = self._key(lat, lon)
        entry = self._store.get(key)
        if entry is None or time.monotonic() > entry.expires_at:
            if entry:
                del self._store[key]
            return None
        return entry.result

    def set(self, lat: float, lon: float, result: ReverseResult) -> None:
        if len(self._store) >= self._max_size:
            oldest = min(self._store, key=lambda k: self._store[k].expires_at)
            del self._store[oldest]
        self._store[self._key(lat, lon)] = _CacheEntry(
            result=result,
            expires_at=time.monotonic() + self._ttl,
        )


_cache = _GeoCache(max_size=CACHE_MAX_SIZE, ttl=CACHE_TTL_SEC)


# ─── regex / helpers ──────────────────────────────────────────────────────────
_EN_TO_FA     = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
_RE_PROVINCE  = re.compile(r"^استان\s+")
_RE_CITY      = re.compile(r"^(شهرستان|شهر|بخش\s+مرکزی)\s+")
_RE_TEHRAN    = re.compile(r"\s*شهر\s*تهران$")
_RE_DISTRICT  = re.compile(r"^منطقه\s+")
_RE_NUMERIC   = re.compile(r"^[\d۰-۹]{1,5}([/-][\d۰-۹]{1,4})?$")


def _fa(text: str) -> str:
    return text.translate(_EN_TO_FA) if text else ""


def _abbrev(t: str) -> str:
    if not t:
        return ""
    t = t.replace("بزرگراه شهید سلیمانی (جاده ملارد)", "بل. شهید سلیمانی")
    t = t.replace("بلوار", "بل.")
    t = t.replace("خیابان", "خ.")
    t = t.replace("کوچه", "ک.")
    t = t.replace("بن‌بست", "ب.ب")
    return t


def _valid_hn(text: str | None) -> bool:
    if not text:
        return False
    t = str(text).strip()
    if not (1 <= len(t) <= 12):
        return False
    if len(re.findall(r"[آ-ی]", t)) > 2:
        return False
    return bool(_RE_NUMERIC.match(t) or re.match(r"^\d{1,5}$", t))


def _clean_province(n: str) -> str:
    return _RE_PROVINCE.sub("", n).strip() if n else ""


def _clean_city(n: str) -> str:
    if not n:
        return ""
    n = _RE_CITY.sub("", n).strip()
    if re.search(r"\s*[-–]\s*", n):
        n = re.split(r"\s*[-–]\s*", n, 1)[-1].strip()
    return n


def _clean_district(n: str) -> str:
    n = _RE_TEHRAN.sub("", n)
    n = _RE_DISTRICT.sub("منطقهٔ ", n)
    return n.strip()


# ─── landmark prefix ──────────────────────────────────────────────────────────
_LM_MAP: list[tuple[tuple[str, ...], str]] = [
    (("mosque",),                               "جنب مسجد"),
    (("hospital", "clinic", "doctors"),         "نزدیک بیمارستان"),
    (("pharmacy",),                             "جنب داروخانه"),
    (("bank", "atm", "bureau_de_change"),       "نزدیک بانک"),
    (("school", "university", "college"),       "نزدیک مدرسه/دانشگاه"),
    (("fire_station",),                         "نزدیک آتش‌نشانی"),
    (("police",),                               "نزدیک کلانتری"),
    (("post_office",),                          "نزدیک پست"),
    (("fuel",),                                 "نزدیک پمپ بنزین"),
    (("park",),                                 "نزدیک پارک"),
    (("restaurant", "cafe", "fast_food"),       "جنب رستوران"),
    (("supermarket", "convenience", "grocery"), "جنب سوپرمارکت"),
    (("mall", "department_store", "marketplace"), "نزدیک مرکز خرید"),
]
_TOURISM_MAP = {"hotel": "جنب هتل", "museum": "نزدیک موزه", "attraction": "نزدیک جاذبه"}


def _lm_prefix(amenity: str, shop: str, tourism: str) -> str:
    for keys, prefix in _LM_MAP:
        if amenity in keys or shop in keys:
            return prefix
    return _TOURISM_MAP.get(tourism, "نزدیک")


# ─── کوئری اصلی ───────────────────────────────────────────────────────────────
_MASTER_QUERY = """
WITH
  pt AS (
    SELECT ST_Transform(ST_SetSRID(ST_MakePoint($1, $2), 4326), 3857) AS geom
  ),

  boundaries AS (
    SELECT
      p.name,
      p.admin_level,
      p.landuse,
      p.tags -> 'place'  AS place_tag,
      ST_Area(p.way)     AS area
    FROM planet_osm_polygon p, pt
    WHERE (
        p.boundary = 'administrative'
        OR p.landuse IN ('residential','commercial','retail')
        OR p.tags -> 'place' IN ('city','town','suburb','quarter','neighbourhood','village')
      )
      AND p.name IS NOT NULL
      AND ST_Contains(p.way, pt.geom)
    ORDER BY ST_Area(p.way) ASC
  ),

  -- addr_context: نزدیک‌ترین شیء با تگ addr:*
  addr_context_raw AS (
    SELECT
      COALESCE(tags -> 'addr:street', tags -> 'addr:place')  AS addr_street,
      tags -> 'addr:quarter'                                  AS addr_quarter,
      tags -> 'addr:suburb'                                   AS addr_suburb,
      tags -> 'addr:neighbourhood'                            AS addr_neighbourhood,
      tags -> 'addr:city'                                     AS addr_city,
      tags -> 'addr:housenumber'                              AS addr_hn,
      ST_Distance(pt.geom, way)                               AS dist
    FROM planet_osm_point, pt
    WHERE (
        tags -> 'addr:street'           IS NOT NULL
        OR tags -> 'addr:place'         IS NOT NULL
        OR tags -> 'addr:quarter'       IS NOT NULL
        OR tags -> 'addr:suburb'        IS NOT NULL
        OR tags -> 'addr:neighbourhood' IS NOT NULL
      )
      AND ST_DWithin(pt.geom, way, $3)

    UNION ALL

    SELECT
      COALESCE(tags -> 'addr:street', tags -> 'addr:place')  AS addr_street,
      tags -> 'addr:quarter'                                  AS addr_quarter,
      tags -> 'addr:suburb'                                   AS addr_suburb,
      tags -> 'addr:neighbourhood'                            AS addr_neighbourhood,
      tags -> 'addr:city'                                     AS addr_city,
      tags -> 'addr:housenumber'                              AS addr_hn,
      ST_Distance(pt.geom, way)                               AS dist
    FROM planet_osm_polygon, pt
    WHERE (
        tags -> 'addr:street'           IS NOT NULL
        OR tags -> 'addr:place'         IS NOT NULL
        OR tags -> 'addr:quarter'       IS NOT NULL
        OR tags -> 'addr:suburb'        IS NOT NULL
        OR tags -> 'addr:neighbourhood' IS NOT NULL
      )
      AND ST_DWithin(pt.geom, way, $3)
  ),

  addr_context AS (
    SELECT * FROM addr_context_raw ORDER BY dist ASC LIMIT 1
  ),

  -- snapped: نزدیک‌ترین خیابان (با یا بدون name)
  snapped AS (
    SELECT
      l.name,
      l.highway,
      l.way,
      ST_Distance(pt.geom, l.way) AS dist
    FROM planet_osm_line l, pt
    WHERE l.highway IN (
        'motorway','trunk','primary','secondary','tertiary',
        'residential','service','unclassified','living_street','pedestrian'
      )
      AND ST_DWithin(pt.geom, l.way, 300)
    ORDER BY
      ST_Distance(pt.geom, l.way) *
      CASE l.highway
        WHEN 'motorway'     THEN 0.25
        WHEN 'trunk'        THEN 0.35
        WHEN 'primary'      THEN 0.70
        WHEN 'secondary'    THEN 1.00
        WHEN 'tertiary'     THEN 1.50
        WHEN 'unclassified' THEN 2.20
        ELSE 3.80
      END
    LIMIT 1
  ),

  -- chain1: خیابانی که به snapped متصله و به نقطه نزدیک‌تره
  chain1 AS (
    SELECT l.name, l.highway, l.way,
           ST_Distance(pt.geom, l.way) AS dist
    FROM planet_osm_line l, pt, snapped
    WHERE l.name IS NOT NULL
      AND (snapped.name IS NULL OR l.name != snapped.name)
      AND ST_DWithin(l.way, snapped.way, $4)
      AND l.highway IN (
        'residential','service','tertiary','secondary',
        'primary','living_street','pedestrian'
      )
    ORDER BY ST_Distance(pt.geom, l.way) ASC
    LIMIT 1
  ),

  -- chain2: خیابانی که به chain1 متصله
  chain2 AS (
    SELECT l.name, l.highway, l.way,
           ST_Distance(pt.geom, l.way) AS dist
    FROM planet_osm_line l, pt, chain1
    WHERE chain1.way IS NOT NULL
      AND l.name IS NOT NULL
      AND l.name != chain1.name
      AND ST_DWithin(l.way, chain1.way, $4)
      AND l.highway IN (
        'residential','service','tertiary','secondary',
        'primary','living_street','pedestrian'
      )
    ORDER BY ST_Distance(pt.geom, l.way) ASC
    LIMIT 1
  ),

  -- chain3: خیابانی که به chain2 متصله
  chain3 AS (
    SELECT l.name, l.highway, l.way,
           ST_Distance(pt.geom, l.way) AS dist
    FROM planet_osm_line l, pt, chain2
    WHERE chain2.way IS NOT NULL
      AND l.name IS NOT NULL
      AND l.name != chain2.name
      AND ST_DWithin(l.way, chain2.way, $4)
      AND l.highway IN ('residential','service','living_street','pedestrian')
    ORDER BY ST_Distance(pt.geom, l.way) ASC
    LIMIT 1
  ),

  -- parent: بلوار/بزرگراه اصلی نزدیک snapped
  parent AS (
    SELECT l.name, l.highway
    FROM planet_osm_line l
    CROSS JOIN pt
    CROSS JOIN snapped
    LEFT JOIN chain1 ON TRUE
    WHERE l.highway IN ('motorway','trunk','primary','secondary')
      AND l.name IS NOT NULL
      AND (snapped.name IS NULL OR l.name != snapped.name)
      AND (chain1.name  IS NULL OR l.name != chain1.name)
      AND (
        ST_DWithin(l.way, snapped.way, $4)
        OR (chain1.way IS NOT NULL AND ST_DWithin(l.way, chain1.way, $4))
        OR ST_DWithin(pt.geom, l.way, 350)
      )
    ORDER BY
      CASE
        WHEN ST_DWithin(l.way, snapped.way, $4)                              THEN 0
        WHEN chain1.way IS NOT NULL AND ST_DWithin(l.way, chain1.way, $4)   THEN 1
        ELSE 2
      END,
      ST_Distance(pt.geom, l.way) ASC
    LIMIT 1
  ),

  building AS (
    SELECT
      p.name,
      p.tags -> 'addr:housenumber'                                AS house_number,
      COALESCE(p.tags->'addr:housename', p.tags->'name:fa')      AS house_name
    FROM planet_osm_polygon p, pt
    WHERE (p.building IS NOT NULL OR p.tags->'addr:housenumber' IS NOT NULL)
      AND ST_DWithin(pt.geom, p.way, 40)
    ORDER BY ST_Distance(pt.geom, p.way) ASC
    LIMIT 1
  ),

  landmark AS (
    SELECT name, amenity, shop, tourism FROM (
      SELECT name, amenity, shop, tourism, ST_Distance(pt.geom, way) AS dist
      FROM planet_osm_point, pt
      WHERE (amenity IS NOT NULL OR shop IS NOT NULL OR tourism IS NOT NULL)
        AND name IS NOT NULL AND ST_DWithin(pt.geom, way, 50)
      UNION ALL
      SELECT name, amenity, shop, tourism, ST_Distance(pt.geom, way) AS dist
      FROM planet_osm_polygon, pt
      WHERE (amenity IS NOT NULL OR shop IS NOT NULL OR tourism IS NOT NULL)
        AND name IS NOT NULL AND ST_DWithin(pt.geom, way, 50)
    ) lm ORDER BY dist ASC LIMIT 1
  ),

  traffic_zone AS (
    SELECT name, description
    FROM tehran_traffic_zones, pt
    WHERE ST_Contains(way, pt.geom)
    LIMIT 1
  )

SELECT
  (SELECT json_agg(json_build_object(
            'name',name,'level',admin_level,
            'landuse',landuse,'place',place_tag,'area',area))
   FROM boundaries)                   AS boundaries,

  (SELECT json_build_object('name',name,'highway',highway,'dist',dist)
   FROM snapped)                      AS snapped,

  (SELECT json_build_object(
            'addr_street',addr_street,
            'addr_quarter',addr_quarter,
            'addr_suburb',addr_suburb,
            'addr_neighbourhood',addr_neighbourhood,
            'addr_city',addr_city,
            'addr_hn',addr_hn,
            'dist',dist)
   FROM addr_context)                 AS addr_context,

  (SELECT json_build_object('name',name,'highway',highway,'dist',dist)
   FROM chain1)                       AS chain1,

  (SELECT json_build_object('name',name,'highway',highway,'dist',dist)
   FROM chain2)                       AS chain2,

  (SELECT json_build_object('name',name,'highway',highway,'dist',dist)
   FROM chain3)                       AS chain3,

  (SELECT json_build_object('name',name,'highway',highway)
   FROM parent)                       AS parent,

  (SELECT json_build_object(
            'name',COALESCE(name,house_name),
            'house_number',house_number)
   FROM building)                     AS building,

  (SELECT json_build_object(
            'name',name,'amenity',amenity,'shop',shop,'tourism',tourism)
   FROM landmark)                     AS landmark,

  (SELECT json_build_object('name',name,'description',description)
   FROM traffic_zone)                 AS traffic_zone;
"""


# ─── پردازش مرزها ─────────────────────────────────────────────────────────────
def _parse_boundaries(rows: list[dict]) -> tuple[str, str, str, str]:
    province = city = district = neighbourhood = ""
    rows_sorted = sorted(rows, key=lambda r: float(r.get("area") or 0))

    for r in rows_sorted:
        level   = str(r.get("level") or "")
        name    = r.get("name") or ""
        place   = r.get("place") or ""
        landuse = r.get("landuse") or ""

        if level == "4":
            province = _clean_province(name)

        elif level in ("6", "7", "8") or place in ("town", "city"):
            if not city:
                city = _clean_city(name)

        elif level in ("9", "10") or place in ("suburb", "quarter"):
            if not district:
                district = _clean_district(name)

        elif (
            place in ("neighbourhood", "village")
            or landuse == "residential"
            or "فاز" in name
        ):
            if not neighbourhood:
                neighbourhood = name.strip()

    return province, city, district, neighbourhood


# ─── resolve زنجیره خیابان ────────────────────────────────────────────────────
def _resolve_street_chain(
    snapped_name: str,
    chain1_name: str,
    chain2_name: str,
    chain3_name: str,
    parent_name: str,
    addr_street: str,
    addr_quarter: str,
    addr_suburb: str,
    addr_neighbourhood: str,
) -> tuple[list[str], str]:
    """
    ترتیب خروجی: از بزرگ‌ترین به کوچیک‌ترین (parent → ... → snapped)
    اگر snapped اسم نداشت، از addr_context جایگزین می‌کنیم.
    """
    seen: set[str] = set()
    chain: list[str] = []

    def add(name: str) -> None:
        n = name.strip()
        if n and n not in seen:
            seen.add(n)
            chain.append(n)

    if snapped_name:
        # داده OSM کامل داریم
        add(parent_name)
        add(chain1_name)
        add(chain2_name)
        add(chain3_name)
        add(snapped_name)
        return chain, "osm_line"
    else:
        # snapped اسم نداره — interpolation از addr_context
        add(parent_name)
        add(addr_suburb)
        add(addr_quarter)
        add(addr_neighbourhood)
        add(addr_street)
        # chain های توپولوژیک رو هم اضافه کن اگه موجودن
        add(chain1_name)
        add(chain2_name)
        add(chain3_name)
        return chain, "addr_interpolated"


# ─── ساخت آدرس نهایی ─────────────────────────────────────────────────────────
def _build_address(
    province: str,
    city: str,
    district: str,
    neighbourhood: str,
    street_chain: list[str],
    dist_to_road: float,
    building_name: str,
    house_number: str,
    landmark_name: str,
    landmark_prefix: str,
    addr_city: str,
    addr_neighbourhood: str,
) -> tuple[str, float]:
    parts: list[str] = []
    conf = 0.0

    effective_city          = city or addr_city
    effective_neighbourhood = neighbourhood or addr_neighbourhood

    # ── جغرافیا ────────────────────────────────────────────────────────────
    if province:
        parts.append(province); conf += 0.08
    if effective_city and effective_city != province:
        parts.append(effective_city); conf += 0.12
    if district and district != effective_city:
        parts.append(district); conf += 0.08
    if effective_neighbourhood and effective_neighbourhood not in (effective_city, district):
        parts.append(effective_neighbourhood); conf += 0.08

    # ── زنجیره خیابان ──────────────────────────────────────────────────────
    chain_abbrev = [_abbrev(s) for s in street_chain]
    for i, seg in enumerate(chain_abbrev):
        is_last = (i == len(chain_abbrev) - 1)
        if is_last and dist_to_
```

_(truncated — file exceeds size limit)_

### app/api/v2/services/routing_service.py

```python
# c:\Users\Raven\OSM\app\api\v2\services\routing_service.py
import httpx
from fastapi import HTTPException

OSRM_URL = "http://127.0.0.1:5000"

async def get_route(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float
):
    url = f"{OSRM_URL}/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url,
                params={
                    "overview": "full",
                    "geometries": "geojson",
                    "steps": "true" 
                },
                timeout=12.0
            )
            
            if response.status_code == 200:
                return response.json()
                
            raise HTTPException(
                status_code=response.status_code,
                detail="Error receiving route from OSRM engine"
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail=f"Unable to connect to OSRM server: {str(e)}"
            )


async def optimize_trip(locations: list[dict]):
    if len(locations) < 2:
        raise HTTPException(status_code=400, detail="At least 2 locations are required for routing")

    coords_string = ";".join([f"{loc['lon']},{loc['lat']}" for loc in locations])
    
    url = f"{OSRM_URL}/trip/v1/driving/{coords_string}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url,
                params={
                    "source": "first",
                    "destination": "any",
                    "overview": "full",
                    "geometries": "geojson",
                    "steps": "true"
                },
                timeout=15.0
            )
            
            if response.status_code == 200:
                return response.json()
                
            raise HTTPException(
                status_code=response.status_code,
                detail="Error optimizing trip from OSRM"
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail=f"Error connecting to OSRM trip service: {str(e)}"
            )
```

### app/api/v2/services/search_service.py

```python
# c:\Users\Raven\OSM\app\api\v2\services\search_service.py
"""
search_service.py — نسخه فوق‌حرفه‌ای v3 (محدود شده به حریم فضایی ۸۰ کیلومتری کاربر)
PostGIS Full-Text + Fuzzy Search | Iran Map
============================================
"""

from __future__ import annotations

import asyncio
import hashlib
import re
import time
import unicodedata
from dataclasses import dataclass
from typing import Any

import asyncpg
import structlog

# ─────────────────────────────────────────────
# پیکربندی دیتابیس
# ─────────────────────────────────────────────

DB_DSN = "postgresql://map_admin:map_secure_pass@localhost:5433/iran_map"

POOL_MIN_SIZE = 2
POOL_MAX_SIZE = 10
POOL_COMMAND_TIMEOUT = 10.0

IRAN_CENTER_LAT = 32.4
IRAN_CENTER_LON = 53.7

# شعاع فیلتر محلی: ۸۰,۰۰۰ متر (۸۰ کیلومتر) که معادل محدوده یک کلان‌شهر و شهرهای حومه است
LOCAL_SEARCH_RADIUS_METERS = 80000.0

# شعاع dedup مختصاتی (درجه ≈ ۵۰ متر)
DEDUP_GRID_DEG = 0.0005

MAX_CANDIDATES = 60   # قبل از dedup و رتبه‌بندی
MAX_RESULTS    = 10   # خروجی نهایی

# ─────────────────────────────────────────────
# Logging ساختاریافته
# ─────────────────────────────────────────────

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.BoundLogger,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)
log = structlog.get_logger("search_service")

# ─────────────────────────────────────────────
# Connection Pool بهینه asyncpg
# ─────────────────────────────────────────────

_pool: asyncpg.Pool | None = None
_pool_lock = asyncio.Lock()


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is not None:
        return _pool
    async with _pool_lock:
        if _pool is None:
            _pool = await asyncpg.create_pool(
                dsn=DB_DSN,
                min_size=POOL_MIN_SIZE,
                max_size=POOL_MAX_SIZE,
                command_timeout=POOL_COMMAND_TIMEOUT,
            )
            log.info("search_pool_created")
    return _pool

# ─────────────────────────────────────────────
# لایه‌های ترجمه تگ‌های OSM ایران
# ─────────────────────────────────────────────

_AMENITY_FA: dict[str, str] = {
    "hospital": "بیمارستان",
    "clinic": "درمانگاه",
    "pharmacy": "داروخانه",
    "doctors": "مطب پزشک",
    "dentist": "مطب دندانپزشک",
    "restaurant": "رستوران",
    "cafe": "کافه",
    "fast_food": "فست‌فود",
    "bank": "بانک",
    "atm": "عابربانک",
    "fuel": "پمپ بنزین",
    "school": "مدرسه",
    "kindergarten": "مهدکودک",
    "university": "دانشگاه",
    "college": "دانشکده",
    "library": "کتابخانه",
    "parking": "پارکینگ",
    "hotel": "هتل",
    "mosque": "مسجد",
    "place_of_worship": "مکان مذهبی",
    "bus_station": "پایانه اتوبوس",
    "bus_stop": "ایستگاه اتوبوس",
    "subway_entrance": "ورودی مترو",
    "taxi": "ایستگاه تاکسی",
    "police": "کلانتری",
    "fire_station": "آتش‌نشانی",
    "post_office": "اداره پست",
    "townhall": "شهرداری",
    "theatre": "تئاتر",
    "cinema": "سینما",
    "community_centre": "خانه فرهنگ",
    "sports_centre": "مرکز ورزشی",
    "swimming_pool": "استخر",
    "park": "بوستان",
}

_SHOP_FA: dict[str, str] = {
    "supermarket": "سوپرمارکت",
    "convenience": "هایپرمارکت",
    "bakery": "نانوایی",
    "butcher": "قصابی",
    "greengrocer": "میوه‌فروشی",
    "mall": "مرکز خرید",
    "department_store": "فروشگاه بزرگ",
    "clothes": "فروشگاه پوشاک",
    "electronics": "فروشگاه لوازم الکترونیک",
    "mobile_phone": "فروشگاه موبایل",
    "car_repair": "تعمیرگاه خودرو",
    "car_parts": "لوازم یدکی",
    "hairdresser": "آرایشگاه",
    "optician": "عینک‌سازی",
    "jewelry": "جواهرفروشی",
    "books": "کتاب‌فروشی",
}

_TOURISM_FA: dict[str, str] = {
    "hotel": "هتل",
    "hostel": "مهمانپذیر",
    "motel": "متل",
    "museum": "موزه",
    "attraction": "جاذبه گردشگری",
    "viewpoint": "دیدگاه",
    "information": "مرکز اطلاعات گردشگری",
}

_PLACE_FA: dict[str, str] = {
    "city": "کلان‌شهر",
    "town": "شهر",
    "village": "روستا",
    "hamlet": "دهکده",
    "suburb": "محله",
    "quarter": "محله",
    "neighbourhood": "محله",
    "district": "منطقه",
    "county": "شهرستان",
    "state": "استان",
    "country": "کشور",
}

_PLACE_WEIGHT: dict[str, float] = {
    "country": 1.0,
    "state": 0.95,
    "county": 0.90,
    "city": 0.88,
    "town": 0.82,
    "district": 0.75,
    "suburb": 0.65,
    "quarter": 0.60,
    "neighbourhood": 0.55,
    "village": 0.50,
    "hamlet": 0.40,
}

_HIGHWAY_WEIGHT: dict[str, float] = {
    "motorway": 0.85,
    "trunk": 0.80,
    "primary": 0.72,
    "secondary": 0.65,
    "tertiary": 0.55,
    "residential": 0.40,
    "service": 0.25,
    "unclassified": 0.20,
}

_AMENITY_WEIGHT: dict[str, float] = {
    "hospital": 0.75,
    "university": 0.75,
    "bus_station": 0.70,
    "subway_entrance": 0.70,
    "townhall": 0.68,
    "school": 0.60,
    "bank": 0.55,
    "mosque": 0.55,
    "pharmacy": 0.50,
    "fuel": 0.45,
    "restaurant": 0.40,
    "cafe": 0.35,
    "parking": 0.30,
}


def translate_tag(amenity: str, shop: str, tourism: str, highway: str, place: str) -> tuple[str, float]:
    if place:
        return _PLACE_FA.get(place, place), _PLACE_WEIGHT.get(place, 0.45)
    if amenity:
        return _AMENITY_FA.get(amenity, amenity), _AMENITY_WEIGHT.get(amenity, 0.40)
    if shop:
        label = _SHOP_FA.get(shop, shop)
        return f"فروشگاه {label}", 0.38
    if tourism:
        return _TOURISM_FA.get(tourism, tourism), 0.50
    if highway:
        return "معبر", _HIGHWAY_WEIGHT.get(highway, 0.25)
    return "", 0.30

# ─────────────────────────────────────────────
# پاکسازی متون فارسی
# ─────────────────────────────────────────────

_RE_PROVINCE  = re.compile(r"^استان\s+")
_RE_COUNTY    = re.compile(r"^شهرستان\s+")
_RE_DISTRICT  = re.compile(r"^(بخش\s+مرکزی|بخش|منطقه)\s+")
_RE_SUBURB    = re.compile(r"^(محله|ناحیه)\s+")
_RE_MULTISPACE = re.compile(r"\s{2,}")


def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("ي", "ی").replace("ك", "ک").replace("‌", "")
    return _RE_MULTISPACE.sub(" ", text).strip().lower()


def clean_boundary(text: str, pattern: re.Pattern) -> str:
    return pattern.sub("", text).strip() if text else ""

# ─────────────────────────────────────────────
# آدرس‌ساز سلسله‌مراتب ایرانی
# ─────────────────────────────────────────────

def build_address(row: dict[str, Any]) -> str:
    name = (row.get("name") or "").strip() or "مکان بدون نام"

    province = clean_boundary(row.get("province") or "", _RE_PROVINCE)
    county   = clean_boundary(row.get("county") or "", _RE_COUNTY)
    district = clean_boundary(row.get("district") or "", _RE_DISTRICT)
    suburb   = clean_boundary(row.get("suburb") or "", _RE_SUBURB)
    street   = (row.get("street") or "").strip()

    poi_fa, _ = translate_tag(
        row.get("amenity") or "",
        row.get("shop") or "",
        row.get("tourism") or "",
        row.get("highway") or "",
        row.get("place") or "",
    )

    display_name = name
    if poi_fa and normalize_text(poi_fa) not in normalize_text(name):
        display_name = f"{poi_fa} {name}"

    addr_parts: list[str] = []
    if province:
        addr_parts.append(province)
    if county and county != province and county != name:
        addr_parts.append(county)
    if district and district not in (county, name):
        if district.strip().lower() not in ("مرکزی", "مركزي"):
            addr_parts.append(district)
    if suburb and suburb not in addr_parts and suburb != name:
        addr_parts.append(suburb)
    if street and street != name:
        addr_parts.append(street)

    if addr_parts:
        return f"{display_name} ({', '.join(addr_parts)})"

    geo_label = {"point": "مکان", "line": "معبر", "polygon": "منطقه"}.get(
        row.get("source_type", "point"), "مکان"
    )
    return f"{display_name} ({geo_label})"

# ─────────────────────────────────────────────
# سیستم رتبه‌بندی پیشرفته با فاکتور نزدیکی به موقعیت کاربر
# ─────────────────────────────────────────────

def score_result(
    row: dict[str, Any],
    query_tokens: list[str],
    trgm_score: float,
    user_lat: float | None = None,
    user_lon: float | None = None
) -> float:
    _, type_weight = translate_tag(
        row.get("amenity") or "",
        row.get("shop") or "",
        row.get("tourism") or "",
        row.get("highway") or "",
        row.get("place") or "",
    )

    display = normalize_text(row.get("display_name") or "")
    addr    = normalize_text(
        (row.get("province") or "") + " " +
        (row.get("county") or "") + " " +
        (row.get("district") or "")
    )
    combined_text = f"{display} {addr}"
    matched = sum(
        1 for t in query_tokens
        if normalize_text(t) in combined_text
    )
    token_ratio = matched / max(len(query_tokens), 1)

    lat = row.get("lat") or 32.4
    lon = row.get("lon") or 53.7
    
    # 🔴 اصلاح شد: در صورتی که موقعیت زنده کاربر ارسال شده باشد، نزدیکی به کاربر اولویت اول می‌شود
    if user_lat and user_lon:
        dist_deg = ((lat - user_lat) ** 2 + (lon - user_lon) ** 2) ** 0.5
        # محدوده شعاع حدود ۱ درجه جغرافیایی (نزدیک ۱۱۰ کیلومتر)
        proximity = max(0.0, 1.0 - dist_deg / 1.0)
    else:
        dist_deg = ((lat - IRAN_CENTER_LAT) ** 2 + (lon - IRAN_CENTER_LON) ** 2) ** 0.5
        proximity = max(0.0, 1.0 - dist_deg / 25.0)

    score = (
        trgm_score   * 35 +
        type_weight  * 30 +
        token_ratio  * 25 +
        proximity    * 10
    )
    return round(score, 3)

# ─────────────────────────────────────────────
# کوئری ترکیبی مجهز به فیلتر هرمی شعاع فضایی (ST_DWithin)
# ─────────────────────────────────────────────

_SEARCH_SQL = """
WITH
  boundaries_prep AS (
    SELECT name, admin_level, way
    FROM planet_osm_polygon
    WHERE boundary = 'administrative'
      AND admin_level IN ('4','6','8','10','11')
      AND name IS NOT NULL
  ),

  pts AS (
    SELECT
      p.name,
      p.tags -> 'place'   AS place,
      p.tags -> 'amenity'  AS amenity,
      p.tags -> 'shop'     AS shop,
      p.tags -> 'tourism'  AS tourism,
      p.tags -> 'highway'  AS highway,
      p.tags -> 'addr:suburb'  AS suburb,
      p.tags -> 'addr:street'  AS street,
      NULL::text         AS landuse,
      p.way,
      'point'            AS source_type,
      similarity(p.name, $1) AS score
    FROM planet_osm_point p
    WHERE p.name IS NOT NULL
      AND p.name % ANY($2)
      -- 🔴 فیلتر فضایی هوشمند: اگر لوکیشن کاربر (پارامتر ۴ و ۵) ارسال شده باشد، جستجو به شعاع ۸۰ کیلومتری محدود می‌شود
      AND ($4::double precision IS NULL OR ST_DWithin(p.way, ST_Transform(ST_SetSRID(ST_MakePoint($4, $5), 4326), 3857), $6))
      AND similarity(p.name, $1) > 0.12
  ),

  lns AS (
    SELECT
      l.name,
      NULL              AS place,
      NULL              AS amenity,
      NULL              AS shop,
      NULL              AS tourism,
      l.highway,
      NULL              AS suburb,
      NULL              AS street,
      NULL              AS landuse,
      ST_Centroid(l.way)  AS way,
      'line'            AS source_type,
      similarity(l.name, $1) AS score
    FROM planet_osm_line l
    WHERE l.name IS NOT NULL
      AND l.name % ANY($2)
      -- 🔴 فیلتر فضایی هوشمند: محدودسازی معابر به حریم ۸۰ کیلومتری کاربر
      AND ($4::double precision IS NULL OR ST_DWithin(l.way, ST_Transform(ST_SetSRID(ST_MakePoint($4, $5), 4326), 3857), $6))
      AND l.highway IS NOT NULL
      AND similarity(l.name, $1) > 0.12
  ),

  polys AS (
    SELECT
      poly.name,
      poly.tags -> 'place'   AS place,
      poly.amenity,
      poly.shop,
      poly.tourism,
      NULL              AS highway,
      poly.tags -> 'addr:suburb' AS suburb,
      poly.tags -> 'addr:street' AS street,
      poly.landuse,
      ST_Centroid(poly.way)  AS way,
      'polygon'         AS source_type,
      similarity(poly.name, $1) AS score
    FROM planet_osm_polygon poly
    WHERE poly.name IS NOT NULL
      AND poly.name % ANY($2)
      -- 🔴 فیلتر فضایی هوشمند: محدودسازی مناطق به حریم ۸۰ کیلومتری کاربر
      AND ($4::double precision IS NULL OR ST_DWithin(poly.way, ST_Transform(ST_SetSRID(ST_MakePoint($4, $5), 4326), 3857), $6))
      AND poly.boundary IS DISTINCT FROM 'administrative'
      AND similarity(poly.name, $1) > 0.12
  ),

  candidates AS (
    SELECT * FROM pts
    UNION ALL
    SELECT * FROM lns
    UNION ALL
    SELECT * FROM polys
    ORDER BY score DESC
    LIMIT $3
  )

SELECT
  c.name,
  c.place,
  c.amenity,
  c.shop,
  c.tourism,
  c.highway,
  c.suburb,
  c.street,
  c.source_type,
  c.score,
  ST_Y(ST_Transform(c.way, 4326)) AS lat,
  ST_X(ST_Transform(c.way, 4326)) AS lon,

  -- استعلام تقسیمات اداری فقط برای ۳۰ کاندیدای برتر نهایی
  (SELECT b.name FROM boundaries_prep b
   WHERE b.admin_level = '4' AND ST_Contains(b.way, c.way)
   LIMIT 1) AS province,

  (SELECT b.name FROM boundaries_prep b
   WHERE b.admin_level = '6' AND ST_Contains(b.way, c.way)
   LIMIT 1) AS county,

  (SELECT b.name FROM boundaries_prep b
   WHERE b.admin_level = '8' AND ST_Contains(b.way, c.way)
   LIMIT 1) AS district

FROM candidates c;
"""

# ─────────────────────────────────────────────
# سیستم حذف رکوردهای تکراری چندسطحی (Dedup)
# ─────────────────────────────────────────────

def _coord_key(lat: float, lon: float) -> str:
    """grid ۱لب متری برای فیلتر نقاط همپوشان فیزیکی"""
    glat = round(lat / 0.001) * 0.001
    glon = round(lon / 0.001) * 0.001
    return f"{glat:.3f},{glon:.3f}"


def _name_key(name: str, place: str, amenity: str) -> str:
    return hashlib.md5((normalize_text(name) + "|" + (place or "") + "|" + (amenity or "")).encode()).hexdigest()


def dedup_results(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen_coords: set[str] = set()
    name_best: dict[str, dict] = {}
    seen_addresses: set[str] = set()

    for row in rows:
        lat = row.get("lat") or 0.0
        lon = row.get("lon") or 0.0
        ck = _coord_key(lat, lon)
        nk = _name_key(
            row.get("name") or "",
            row.get("place") or "",
            row.get("amenity") or "",
        )
        addr_name = row.get("display_name")

        if ck in seen_coords or addr_name in seen_addresses:
            continue
        seen_coords.add(ck)
        seen_addresses.add(addr_name)

        existing = name_best.get(nk)
        if existing is None or row.get("final_score", 0) > existing.get("final_score", 0):
            name_best[nk] = row

    return list(name_best.values())

# ─────────────────────────────────────────────
# تابع اصلی جستجو با قابلیت محدودسازی شعاع جغرافیایی
# ─────────────────────────────────────────────

async def search(
    query: str, 
    limit: int = MAX_RESULTS,
    user_lat: float | None = None,
    user_lon: float | None = None
) -> list[dict[str, Any]]:
    """
    جستجوی هوشمند در نقشه ایران همراه با فیلتر هرمی موقعیت مکانی کاربر.
    """
    t0 = time.perf_counter()

    clean_query = str(query).strip()
    if len(clean_query) < 2:
        return []

    query_tokens = [t for t in clean_query.split() if len(t) >= 2]
    if not query_tokens:
        return []

    pool = await get_pool()
    try:
        async with pool.acquire() as conn:
            # 🟢 فراخوانی دیتابیس با انتقال متغیرهای طول، عرض جغرافیایی کاربر و شعاع ۸۰ کیلومتر
            rows = await conn.fetch(
                _SEARCH_SQL, 
                clean_query, 
                query_tokens, 
                MAX_CANDIDATES,
                user_lon,
                user_lat,
                LOCAL_SEARCH_RADIUS_METERS
            )
    except asyncpg.PostgresError as e:
        log.error("search_db_error", query=query, error=str(e))
        return []
    except asyncio.TimeoutError:
        log.warning("search_timeout", query=query)
        return []

    processed: list[dict[str, Any]] = []
    for r in rows:
        row = dict(r)

        # ساخت آدرس دقیق
        row["display_name"] = build_address(row)

        poi_fa, _ = translate_tag(
            row.get("amenity") or "",
            row.get("shop") or "",
            row.get("tourism") or "",
            row.get("highway") or "",
            row.get("place") or "",
        )
        row["place_type"] = poi_fa or None

        # امتیاز نهایی بهینه شده بر اساس نزدیکی به موقعیت زنده کاربر
        row["final_score"] = score_result(row, query_tokens, float(row.get("score") or 0), user_lat, user_lon)

        processed.append(row)

    # فیلتر تکراری‌ها
    unique = dedup_results(processed)

    # مرتب‌سازی بر اساس برترین امتیاز ترکیبی حاصل شده
    unique.sort(key=lambda x: x["final_score"], reverse=True)
    top = unique[:limit]

    elapsed = (time.perf_counter() - t0) * 1000
    log.info(
        "search_done",
        query=query,
        raw=len(rows),
        after_dedup=len(unique),
        returned=len(top),
        elapsed_ms=round(elapsed, 1),
    )

    return [
        {
            "display_name": item["display_name"],
            "lat": round(item["lat"], 7),
            "lon": round(item["lon"], 7),
            "score": item["final_score"],
            "place_type": item.get("place_type"),
        }
        for item in top
    ]
```

### app/api/v2/services/store_service.py

```python
from sqlalchemy.orm import Session
from typing import Optional, List
from app.api.v2.models.store import Store
from app.api.v2.schemas.store import StoreUpdate


def create_store(db: Session, user_id: int, data):
    store = Store(
        user_id=user_id,
        name=data.name,
        lat=data.lat,
        lon=data.lon,
        address=data.address,
        phone=data.phone
    )

    db.add(store)
    db.commit()
    db.refresh(store)
    return store


def get_stores(db: Session, user_id: int | None = None) -> List[Store]:
    query = db.query(Store)

    if user_id:
        query = query.filter(Store.user_id == user_id)

    return query.all()


def get_store(db: Session, store_id: int) -> Optional[Store]:
    """دریافت یک فروشگاه با شناسه"""
    return db.query(Store).filter(Store.id == store_id).first()


def update_store(db: Session, store_id: int, data: StoreUpdate) -> Optional[Store]:
    """به‌روزرسانی فروشگاه"""
    store = get_store(db, store_id)
    if not store:
        return None
    
    # فقط فیلدهایی که ارسال شده‌اند را به‌روز می‌کنیم
    if data.name is not None:
        store.name = data.name
    if data.lat is not None:
        store.lat = data.lat
    if data.lon is not None:
        store.lon = data.lon
    if data.address is not None:
        store.address = data.address
    if data.phone is not None:
        store.phone = data.phone
    
    db.commit()
    db.refresh(store)
    return store


def delete_store(db: Session, store_id: int) -> bool:
    """حذف فروشگاه"""
    store = get_store(db, store_id)
    if not store:
        return False
    
    db.delete(store)
    db.commit()
    return True
```

### app/api/v2/services/tile_service.py

```python
from app.api.v2.core.config import settings


def get_tile_url(z: int, x: int, y: int):
    return f"{settings.MARTIN_URL}/osm/{z}/{x}/{y}"
```

### app/api/v2/services/warehouse_service.py

```python
from sqlalchemy.orm import Session
from typing import Optional, List
from app.api.v2.models.warehouse import Warehouse
from app.api.v2.schemas.warehouse import WarehouseCreate, WarehouseUpdate


def create_warehouse(db: Session, store_id: int, data: WarehouseCreate):
    """ایجاد انبار جدید با داده‌های کامل"""
    warehouse = Warehouse(
        store_id=store_id,
        name=data.name,
        lat=data.lat,
        lon=data.lon,
        address=data.address,
        phone=data.phone
    )
    
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    return warehouse


def get_warehouses(db: Session, store_id: int) -> List[Warehouse]:
    """دریافت لیست انبارهای یک فروشگاه"""
    return db.query(Warehouse).filter(Warehouse.store_id == store_id).all()


def get_warehouse(db: Session, warehouse_id: int) -> Optional[Warehouse]:
    """دریافت یک انبار با شناسه"""
    return db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()


def update_warehouse(db: Session, warehouse_id: int, data: WarehouseUpdate) -> Optional[Warehouse]:
    """به‌روزرسانی انبار"""
    warehouse = get_warehouse(db, warehouse_id)
    if not warehouse:
        return None
    
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(warehouse, field, value)
    
    db.commit()
    db.refresh(warehouse)
    return warehouse


def delete_warehouse(db: Session, warehouse_id: int) -> bool:
    """حذف انبار"""
    warehouse = get_warehouse(db, warehouse_id)
    if not warehouse:
        return False
    
    db.delete(warehouse)
    db.commit()
    return True
```

### app/core/__init__.py

```python

```

### app/core/config.py

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Map API V2"
    VERSION: str = "1.0.0"  # اضافه شد
    DEBUG: bool = True  # اضافه شد
    
    # تنظیمات دیتابیس دقیقاً بر اساس docker-compose شما
    POSTGRES_USER: str = "map_admin"
    POSTGRES_PASSWORD: str = "map_secure_pass"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5433"
    POSTGRES_DB: str = "iran_map"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # اضافه کردن برای راحتی
    @property
    def SYNC_DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
```

### app/core/database.py

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# IMPORTANT: Import Base از models.base
from app.api.v2.models.base import Base

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency برای استفاده در Endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### app/models/__init__.py

```python
# app/models/__init__.py
from app.models.user import User
from app.models.location import Location

__all__ = ["User", "Location"]
```

### app/models/api_key.py

```python
# app/models/api_key.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, index=True, nullable=False)  # کلید اصلی (تولید شده تصادفی)
    masked_key = Column(String(50), nullable=False)  # کلید ماسک شده برای نمایش‌های بعدی
    name = Column(String(100), nullable=True)  # نام یا برچسب اختیاری
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_active = Column(Boolean, default=True)
    is_unlimited = Column(Boolean, default=False)  # بدون تاریخ انقضا
    expires_at = Column(DateTime(timezone=True), nullable=True)
    rate_limit = Column(Integer, default=60)  # سقف درخواست در دقیقه
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    # روابط با جدول کاربران
    user = relationship("User", backref="api_keys")

    def __repr__(self):
        return f"<APIKey {self.masked_key} - User {self.user_id}>"
```

### app/models/location.py

```python
# app/models/location.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    province = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    category = Column(String(50), nullable=True)
    tags = Column(Text, nullable=True)
    phone_number = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    website = Column(String(200), nullable=True)
    working_hours = Column(Text, nullable=True)
    images = Column(Text, nullable=True)
    status = Column(String(20), default="pending")
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    rejected_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)

    shop_id = Column(String(100), nullable=True)
    plaque = Column(String(50), nullable=True)
    unit = Column(String(50), nullable=True)
    tell = Column(String(50), nullable=True)
    is_return_usage = Column(Boolean, default=False)

    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])
    rejecter = relationship("User", foreign_keys=[rejected_by])
    
    def __repr__(self):
        return f"<Location {self.title} ({self.latitude}, {self.longitude})>"
```

### app/models/user.py

```python
# app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    full_name = Column(String(100), nullable=True)
    phone_number = Column(String(15), nullable=True)
    
    # فیلدهای وضعیت
    is_active = Column(Boolean, default=False)  # تایید توسط ادمین
    is_admin = Column(Boolean, default=False)   # آیا خودش ادمین است
    
    # فیلدهای زمانی
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(Integer, nullable=True)  # ID ادمین تایید کننده
    
    def __repr__(self):
        return f"<User {self.username}>"
```

### app/models/user_location.py

```python
# app/models/user_location.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class LocationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class UserLocation(Base):
    __tablename__ = "user_locations"

    id = Column(Integer, primary_key=True, index=True)
    
    # اطلاعات موقعیت
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    province = Column(String(100), nullable=True)
    
    # اطلاعات تماس
    phone_number = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    
    # دسته‌بندی و تگ‌ها
    category = Column(String(50), nullable=True)
    tags = Column(Text, nullable=True)
    
    # وضعیت
    status = Column(Enum(LocationStatus), default=LocationStatus.PENDING)
    is_visible = Column(Boolean, default=False)
    
    # روابط
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # زمان‌ها
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<UserLocation {self.title}>"
```

### app/schemas/api_key.py

```python
# app/schemas/api_key.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class APIKeyCreate(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="نام یا برچسب کلید")
    expires_at: Optional[datetime] = Field(None, description="تاریخ انقضا (در صورت داشتن انقضا)")
    is_unlimited: bool = Field(False, description="آیا کلید بدون تاریخ انقضا است؟")
    rate_limit: int = Field(60, ge=1, description="تعداد درخواست مجاز در دقیقه")

class APIKeyResponse(BaseModel):
    id: int
    masked_key: str
    name: Optional[str]
    is_active: bool
    is_unlimited: bool
    expires_at: Optional[datetime] = None
    rate_limit: int
    created_at: datetime
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class APIKeyCreateResponse(APIKeyResponse):
    raw_key: str  # کلید متنی که فقط یک‌بار در زمان ساخت برای کاربر نمایش داده می‌شود

class APIKeyAdminUpdate(BaseModel):
    is_active: Optional[bool] = None
    is_unlimited: Optional[bool] = None
    expires_at: Optional[datetime] = None
    rate_limit: Optional[int] = None
```

### app/schemas/location.py

```python
# app/schemas/location.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class LocationBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200, description="عنوان موقعیت")
    description: Optional[str] = Field(None, description="توضیحات اختیاری")
    latitude: float = Field(..., ge=-90, le=90, description="عرض جغرافیایی")
    longitude: float = Field(..., ge=-180, le=180, description="طول جغرافیایی")
    category: Optional[str] = Field("shop", description="دسته‌بندی")
    
    shop_id: Optional[str] = Field(None, description="شناسه مغازه در سیستم یدکچی")
    plaque: Optional[str] = Field(None, description="پلاک")
    unit: Optional[str] = Field(None, description="واحد")
    tell: Optional[str] = Field(None, description="تلفن تماس")
    is_return_usage: Optional[bool] = Field(False, description="قابلیت مرجوعی کالا")

class LocationCreate(LocationBase):
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None

class LocationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category: Optional[str] = None
    shop_id: Optional[str] = None
    plaque: Optional[str] = None
    unit: Optional[str] = None
    tell: Optional[str] = None
    is_return_usage: Optional[bool] = None
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None

class LocationApprove(BaseModel):
    admin_notes: Optional[str] = None

class LocationReject(BaseModel):
    reason: str = Field(..., min_length=3, max_length=500, description="دلیل رد موقعیت")
    admin_notes: Optional[str] = None

class LocationResponse(LocationBase):
    id: int
    address: Optional[str]
    city: Optional[str]
    province: Optional[str]
    postal_code: Optional[str]
    status: Optional[str] = "pending"
    is_active: Optional[bool] = True
    created_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

    class Config:
        from_attributes = True

class LocationAdminResponse(LocationResponse):
    creator_name: Optional[str] = None
    creator_username: Optional[str] = None
    approver_name: Optional[str] = None
    admin_notes: Optional[str] = None

class LocationListResponse(BaseModel):
    total: int
    items: List[LocationResponse]

class MessageResponse(BaseModel):
    message: str
    success: bool = True
    location_id: Optional[int] = None
```

### app/schemas/user.py

```python
# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

# ========== درخواست‌ها (Requests) ==========
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    phone_number: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None

class ChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)

# ========== پاسخ‌ها (Responses) ==========
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class MessageResponse(BaseModel):
    message: str
    success: bool = True
```

### app/services/__init__.py

```python

```

### app/services/auth.py

```python
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.core.config import settings

# تعریف سیستم هش کلمات عبور با الگوریتم صنعتی Bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self):
        self.secret_key = settings.JWT_SECRET
        self.algorithm = settings.JWT_ALGORITHM
        self.expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    def hash_password(self, password: str) -> str:
        """
        تبدیل کلمه عبور متنی به کد هش شده غیرقابل بازگشت
        """
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        بررسی همخوانی کلمه عبور وارد شده با پسورد هش شده دیتابیس
        """
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, user_id: int, username: str) -> str:
        """
        تولید توکن امنیتی JWT به مدت اعتبار مشخص شده در تنظیمات (.env)
        """
        # محاسبه زمان دقیق انقضای توکن (تاریخ فعلی + ۲۴ ساعت)
        expire = datetime.utcnow() + timedelta(minutes=self.expire_minutes)
        
        # بدنه داخلی توکن (Payload) حاوی شناسه کاربر و زمان انقضا
        to_encode = {
            "sub": str(user_id), # شناسه یکتای کاربر در دیتابیس
            "username": username,
            "exp": expire
        }
        
        # رمزگذاری و امضای توکن با استفاده از کلید مخفی (JWT_SECRET)
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_access_token(self, token: str) -> dict | None:
        """
        اعتبارسنجی و دیکود کردن توکن دریافتی از کلاینت‌ها
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            # اگر توکن منقضی یا توسط هکرها دستکاری شده باشد
            return None

# ایجاد شیء یکتا برای استفاده در کل پلتفرم
auth_service = AuthService()
```

### app/services/location_service.py

```python
# app/services/location_service.py
import math
from sqlalchemy.orm import Session
from app.models.location import Location
from app.schemas.location import LocationCreate, LocationUpdate
from datetime import datetime
from typing import Optional, List

class LocationService:
    
    @staticmethod
    def create_location(db: Session, location_data: LocationCreate, user_id: Optional[int]) -> Location:
        loc_dict = location_data.model_dump(exclude_unset=True) if hasattr(location_data, 'model_dump') else location_data.dict(exclude_unset=True)
        
        loc_dict.pop("created_by", None)
        loc_dict.pop("status", None)
        loc_dict.pop("is_active", None)
        
        try:
            # انتقال ایمپورت به داخل متد برای حل مشکل ایمپورت چرخشی (Circular Import)
            from app.services.postgis_service import postgis_service
            
            geo_info = postgis_service.smart_reverse_geocode(
                lat=location_data.latitude, 
                lon=location_data.longitude
            )
            if geo_info:
                loc_dict["address"] = location_data.address or geo_info.get("address")
                loc_dict["city"] = location_data.city or geo_info.get("city")
                loc_dict["province"] = location_data.province or geo_info.get("province")
                loc_dict["postal_code"] = location_data.postal_code or geo_info.get("postal_code")
        except Exception as e:
            print(f"Warning: Auto reverse-geocoding failed: {str(e)}")

        status_val = "pending"
        if user_id:
            from app.models.user import User
            user = db.query(User).filter(User.id == user_id).first()
            if user and user.is_admin:
                status_val = "approved"

        location = Location(
            **loc_dict,
            created_by=user_id,
            status=status_val,
            is_active=True
        )
        db.add(location)
        db.commit()
        db.refresh(location)
        return location
    
    @staticmethod
    def get_location(db: Session, location_id: int) -> Optional[Location]:
        return db.query(Location).filter(Location.id == location_id).first()
    
    @staticmethod
    def get_user_locations(db: Session, user_id: int, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Location]:
        query = db.query(Location).filter(Location.created_by == user_id)
        if status:
            query = query.filter(Location.status == status)
        return query.order_by(Location.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_pending_locations(db: Session, skip: int = 0, limit: int = 100) -> List[Location]:
        return db.query(Location).filter(Location.status == "pending").order_by(Location.created_at.asc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_all_locations(db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None, category: Optional[str] = None, city: Optional[str] = None) -> List[Location]:
        query = db.query(Location)
        if status:
            query = query.filter(Location.status == status)
        if category:
            query = query.filter(Location.category == category)
        if city:
            query = query.filter(Location.city == city)
        return query.order_by(Location.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def search_locations(db: Session, lat: float, lon: float, radius_km: float = 5.0, part_filter: Optional[str] = None, brand_filter: Optional[str] = None, is_return_usage: Optional[bool] = None, limit: int = 20) -> List[Location]:
        query = db.query(Location).filter(Location.status == "approved", Location.is_active == True)

        if is_return_usage is not None:
            query = query.filter(Location.is_return_usage == is_return_usage)

        all_locations = query.all()

        def calculate_distance(lat1, lon1, lat2, lon2):
            R = 6371.0
            phi1 = math.radians(lat1)
            phi2 = math.radians(lat2)
            delta_phi = math.radians(lat2 - lat1)
            delta_lambda = math.radians(lon2 - lon1)
            a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            return R * c

        nearby = []
        for loc in all_locations:
            distance = calculate_distance(lat, lon, loc.latitude, loc.longitude)
            if distance <= radius_km:
                nearby.append((distance, loc))
        
        nearby.sort(key=lambda x: x[0])
        return [loc for _, loc in nearby[:limit]]
    
    @staticmethod
    def update_location(db: Session, location_id: int, location_data: LocationUpdate) -> Optional[Location]:
        location = LocationService.get_location(db, location_id)
        if not location:
            return None
        
        update_data = location_data.model_dump(exclude_unset=True) if hasattr(location_data, 'model_dump') else location_data.dict(exclude_unset=True)
            
        for field, value in update_data.items():
            setattr(location, field, value)
        
        location.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(location)
        return location
    
    @staticmethod
    def approve_location(db: Session, location_id: int, admin_id: int, admin_notes: Optional[str] = None) -> Optional[Location]:
        location = LocationService.get_location(db, location_id)
        if not location:
            return None
        
        location.status = "approved"
        location.approved_by = admin_id
        location.approved_at = datetime.utcnow()
        location.admin_notes = admin_notes
        
        db.commit()
        db.refresh(location)
        return location
    
    @staticmethod
    def reject_location(db: Session, location_id: int, admin_id: int, reason: str, admin_notes: Optional[str] = None) -> Optional[Location]:
        location = LocationService.get_location(db, location_id)
        if not location:
            return None
        
        location.status = "rejected"
        location.rejected_by = admin_id
        location.rejected_at = datetime.utcnow()
        location.rejection_reason = reason
        location.admin_notes = admin_notes
        location.is_active = False
        
        db.commit()
        db.refresh(location)
        return location
    
    @staticmethod
    def delete_location(db: Session, location_id: int) -> bool:
        location = LocationService.get_location(db, location_id)
        if not location:
            return False
        db.delete(location)
        db.commit()
        return True

location_service = LocationService()
```

### app/services/nominatim.py

```python
import requests
from app.core.config import settings

class NominatimService:
    def __init__(self):
        self.base_url = f"{settings.NOMINATIM_URL}/search"

    def search_places(
        self, 
        query: str, 
        mode: str = "global", 
        lat: float = None, 
        lon: float = None, 
        viewbox: str = None, 
        city: str = None
    ) -> list:
        # کادر پیش‌فرض مرز جغرافیایی کل ایران
        iran_viewbox = "44.0,40.0,63.0,25.0"
        
        # پارامترهای پیش‌فرض وب‌سرویس
        params = {
            "format": "json",
            "accept-language": "fa",
            "limit": 5
        }

        # پردازش لایه منطق بر اساس حالت انتخاب‌شده (Mode)
        if mode == "global":
            # ۱. جستجوی سراسری در کل ایران
            params["q"] = query
            params["viewbox"] = iran_viewbox
            params["bounded"] = 1

        elif mode == "proximity":
            # ۲. جستجو در اطراف لوکیشن کاربر (Proximity)
            params["q"] = query
            if lat is not None and lon is not None:
                params["lat"] = lat
                params["lon"] = lon
                # اعمال یک باندینگ باکس کوچک فرضی دور کاربر برای اولویت‌دهی شدید محلی
                params["viewbox"] = f"{lon-0.1},{lat+0.1},{lon+0.1},{lat-0.1}"
                params["bounded"] = 0 # برای اینکه اگر در آن نزدیکی پیدا نشد، نتایج دورتر را بیاورد

        elif mode == "viewport":
            # ۳. جستجو دقیقاً درون کادر فعلی نقشه کاربر (Bounding Box)
            params["q"] = query
            if viewbox:
                params["viewbox"] = viewbox
                params["bounded"] = 1 # اجبار به عدم خروج از کادر نقشه فعلی

        elif mode == "city":
            # ۴. جستجوی مقید به یک شهر مشخص
            # در OSM، ادغام نام شهر با کلمه کلیدی، بهترین نتایج POI را در آن شهر می‌دهد
            if city:
                params["q"] = f"{city} {query}"
            else:
                params["q"] = query
            params["viewbox"] = iran_viewbox
            params["bounded"] = 1

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"خطا در پردازش موتور جستجوی Nominatim: {str(e)}")

            # متد جدید برای دریافت سلسله مراتب آدرس از Nominatim
    def reverse_geocode(self, lat: float, lon: float) -> dict:
        url = f"{settings.NOMINATIM_URL}/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "zoom": 18,
            "addressdetails": 1,
            "accept-language": "fa"
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"خطا در ارتباط با سرور Nominatim: {str(e)}")

nominatim_service = NominatimService()
```

### app/services/osrm.py

```python

```

### app/services/osrm_service.py

```python
import httpx
from fastapi import HTTPException

# اگر OSRM در کانتینر داکر هم‌شبکه است، می‌توانید از نام کانتینر یا localhost استفاده کنید
OSRM_URL = "http://127.0.0.1:5000"

class OSRMService:
    async def get_route(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float):
        # ساختن آدرس استاندارد OSRM
        url = f"{OSRM_URL}/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson&steps=true"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=10.0)
                if response.status_code == 200:
                    return response.json()
                raise HTTPException(
                    status_code=response.status_code, 
                    detail="خطا در دریافت پاسخ از موتور مسیریابی OSRM"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=502, 
                    detail=f"عدم امکان برقراری ارتباط با سرور OSRM: {str(e)}"
                )

osrm_service = OSRMService()
```

### app/services/postgis_service.py

```python
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
```

### app/services/tile_service.py

```python
import httpx
from app.core.config import settings

class TileService:
    def __init__(self):
        self.base_url = settings.MARTIN_URL
        # ایجاد یک کلاینت ناهم‌گام دائمی با قابلیت Connection Pooling برای سرعت بالا
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=10.0)

    async def get_vector_tile(self, table: str, z: int, x: int, y: int) -> tuple[bytes, dict]:
        """
        دریافت کاملاً ناهم‌گام (Async) بایت‌های تایل از مارتین بدون قفل کردن صف پردازش
        """
        url = f"/{table}/{z}/{x}/{y}"
        try:
            # ارسال درخواست ناهم‌گام با متد await
            response = await self.client.get(url)
            if response.status_code == 200:
                return response.content, dict(response.headers)
            return b"", {}
        except httpx.HTTPError:
            return b"", {}

tile_service = TileService()
```

### scripts/create_admin.py

```python
# scripts/create_admin.py
import sys
import os

# اضافه کردن مسیر اصلی به PATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.services.auth import auth_service

def create_tables():
    """حذف جداول قدیمی ناقص با تکنیک بومی CASCADE و ایجاد جداول کامل دیتابیس"""
    print("📦 در حال بازسازی جداول دیتابیس...")
    
    # استفاده از قابلیت بومی PostgreSQL DROP CASCADE برای قطع زنجیره رابطه‌ها
    from sqlalchemy import text
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            # حذف فیزیکی و زنجیره‌ای تمام جداول قدیمی نقشه و یدکچی
            connection.execute(text("DROP TABLE IF EXISTS locations, api_keys, users, user_locations CASCADE;"))
            transaction.commit()
            print("🗑️ جداول قدیمی با موفقیت حذف شدند (CASCADE)")
        except Exception as e:
            transaction.rollback()
            print(f"⚠️ خطایی در حذف جداول قدیمی رخ داد: {e}")
            
    # ایجاد مجدد جداول با تمام فیلدهای پیشرفته جدید
    Base.metadata.create_all(bind=engine)
    print("✅ جداول جدید دیتابیس با موفقیت ایجاد شدند")

def create_admin():
    db = SessionLocal()
    
    try:
        # بررسی وجود ادمین
        admin = db.query(User).filter(User.is_admin == True).first()
        if admin:
            print(f"⚠️ ادمین قبلاً وجود دارد:")
            print(f"   نام کاربری: {admin.username}")
            print(f"   ایمیل: {admin.email}")
            return
        
        # ایجاد ادمین
        admin_user = User(
            username="admin",
            email="admin@yadakchi.com",
            hashed_password=auth_service.hash_password("Admin@123456"),
            full_name="مدیر ارشد سیستم",
            phone_number="09123456789",
            is_active=True,
            is_admin=True
        )
        
        db.add(admin_user)
        db.commit()
        
        print("✅ ادمین با موفقیت ایجاد شد!")
        print("=" * 50)
        print("🔐 اطلاعات ورود به سیستم:")
        print(f"   نام کاربری: admin")
        print(f"   رمز عبور: Admin@123456")
        print("=" * 50)
        print("⚠️ لطفاً پس از اولین ورود، رمز عبور خود را تغییر دهید.")
        
    except Exception as e:
        print(f"❌ خطا در ایجاد ادمین: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 در حال راه‌اندازی...")
    create_tables()
    create_admin()
```

### styles/default.json

```json
{
  "version": 8,
  "name": "Standard Cartography Iran Style",
  "glyphs": "http://localhost:3000/font/{fontstack}/{range}",
  "sources": {
    "iran_polygons": {
      "type": "vector",
      "url": "{{BASE_URL}}/tiles/planet_osm_polygon.json?api_key={{API_KEY}}"
    },
    "iran_lines": {
      "type": "vector",
      "url": "{{BASE_URL}}/tiles/planet_osm_line.json?api_key={{API_KEY}}"
    },
    "iran_points": {
      "type": "vector",
      "url": "{{BASE_URL}}/tiles/planet_osm_point.json?api_key={{API_KEY}}"
    }
  },
  "layers": [
    {
      "id": "background",
      "type": "background",
      "paint": {
        "background-color": "#f4f1ea"
      }
    },
    {
      "id": "residential-areas",
      "type": "fill",
      "source": "iran_polygons",
      "source-layer": "planet_osm_polygon",
      "filter": ["==", "landuse", "residential"],
      "paint": {
        "fill-color": "#e5e0d8",
        "fill-opacity": 0.9
      }
    },
    {
      "id": "parks-forests",
      "type": "fill",
      "source": "iran_polygons",
      "source-layer": "planet_osm_polygon",
      "filter": ["any", ["==", "leisure", "park"], ["==", "landuse", "forest"], ["==", "landuse", "grass"]],
      "paint": {
        "fill-color": "#d0e4cc"
      }
    },
    {
      "id": "water-bodies",
      "type": "fill",
      "source": "iran_polygons",
      "source-layer": "planet_osm_polygon",
      "filter": ["any", ["==", "natural", "water"], ["==", "landuse", "reservoir"]],
      "paint": {
        "fill-color": "#aad3df"
      }
    },
    {
      "id": "buildings",
      "type": "fill",
      "source": "iran_polygons",
      "source-layer": "planet_osm_polygon",
      "minzoom": 13,
      "filter": ["has", "building"],
      "paint": {
        "fill-color": "#e0deda",
        "fill-opacity": 0.85
      }
    },
    {
      "id": "waterways",
      "type": "line",
      "source": "iran_lines",
      "source-layer": "planet_osm_line",
      "filter": ["has", "waterway"],
      "paint": {
        "line-color": "#aad3df",
        "line-width": [
          "interpolate",
          ["linear"],
          ["zoom"],
          11, 1,
          15, 3
        ]
      }
    },
    {
      "id": "motorway-casing",
      "type": "line",
      "source": "iran_lines",
      "source-layer": "planet_osm_line",
      "filter": ["any", ["==", "highway", "motorway"], ["==", "highway", "trunk"]],
      "paint": {
        "line-color": "#e07a1b",
        "line-width": [
          "interpolate",
          ["linear"],
          ["zoom"],
          10, 2,
          14, 5.5,
          18, 14
        ]
      }
    },
    {
      "id": "motorway-core",
      "type": "line",
      "source": "iran_lines",
      "source-layer": "planet_osm_line",
      "filter": ["any", ["==", "highway", "motorway"], ["==", "highway", "trunk"]],
      "paint": {
        "line-color": "#ffa042",
        "line-width": [
          "interpolate",
          ["linear"],
          ["zoom"],
          10, 1,
          14, 3.5,
          18, 10
        ]
      }
    },
    {
      "id": "primary-casing",
      "type": "line",
      "source": "iran_lines",
      "source-layer": "planet_osm_line",
      "filter": ["any", ["==", "highway", "primary"], ["==", "highway", "secondary"]],
      "paint": {
        "line-color": "#d6a100",
        "line-width": [
          "interpolate",
          ["linear"],
          ["zoom"],
          10, 1.5,
          14, 4.5,
          18, 11
        ]
      }
    },
    {
      "id": "primary-core",
      "type": "line",
      "source": "iran_lines",
      "source-layer": "planet_osm_line",
      "filter": ["any", ["==", "highway", "primary"], ["==", "highway", "secondary"]],
      "paint": {
        "line-color": "#ffe082",
        "line-width": [
          "interpolate",
          ["linear"],
          ["zoom"],
          10, 0.8,
          14, 2.5,
          18, 8
        ]
      }
    },
    {
      "id": "minor-roads",
      "type": "line",
      "source": "iran_lines",
      "source-layer": "planet_osm_line",
      "filter": ["any", ["==", "highway", "residential"], ["==", "highway", "tertiary"], ["==", "highway", "service"]],
      "paint": {
        "line-color": "#ffffff",
        "line-width": [
          "interpolate",
          ["linear"],
          ["zoom"],
          11, 0.5,
          14, 1.5,
          18, 5
        ]
      }
    },
    {
      "id": "province-labels",
      "type": "symbol",
      "source": "iran_points",
      "source-layer": "planet_osm_point",
      "minzoom": 4,
      "maxzoom": 8,
      "filter": ["==", "place", "state"],
      "layout": {
        "text-field": "{name}",
        "text-font": ["Vazirmatn Thin", "Arial Regular"],
        "text-size": [
          "interpolate",
          ["linear"],
          ["zoom"],
          4, 11,
          8, 15
        ]
      },
      "paint": {
        "text-color": "#424242",
        "text-halo-color": "#ffffff",
        "text-halo-width": 2
      }
    },
    {
      "id": "city-labels",
      "type": "symbol",
      "source": "iran_points",
      "source-layer": "planet_osm_point",
      "minzoom": 7,
      "maxzoom": 11,
      "filter": ["any", ["==", "place", "city"], ["==", "place", "town"]],
      "layout": {
        "text-field": "{name}",
        "text-font": ["Vazirmatn Thin", "Arial Regular"],
        "text-size": [
          "interpolate",
          ["linear"],
          ["zoom"],
          7, 10,
          11, 13
        ]
      },
      "paint": {
        "text-color": "#212121",
        "text-halo-color": "#ffffff",
        "text-halo-width": 2
      }
    },
    {
      "id": "neighborhood-labels",
      "type": "symbol",
      "source": "iran_points",
      "source-layer": "planet_osm_point",
      "minzoom": 11,
      "maxzoom": 14,
      "filter": ["any", ["==", "place", "suburb"], ["==", "place", "neighbourhood"]],
      "layout": {
        "text-field": "{name}",
        "text-font": ["Vazirmatn Thin", "Arial Regular"],
        "text-size": [
          "interpolate",
          ["linear"],
          ["zoom"],
          11, 10,
          14, 12
        ]
      },
      "paint": {
        "text-color": "#616161",
        "text-halo-color": "#ffffff",
        "text-halo-width": 1.5
      }
    },
    {
      "id": "road-labels",
      "type": "symbol",
      "source": "iran_lines",
      "source-layer": "planet_osm_line",
      "minzoom": 12,
      "filter": ["all", ["has", "name"], ["has", "highway"]],
      "layout": {
        "text-field": "{name}",
        "text-font": ["Vazirmatn Thin", "Arial Regular"],
        "text-size": [
          "interpolate",
          ["linear"],
          ["zoom"],
          12, 9,
          16, 12
        ],
        "symbol-placement": "line"
      },
      "paint": {
        "text-color": "#2c2c2c",
        "text-halo-color": "#ffffff",
        "text-halo-width": 1.5
      }
    },
    {
      "id": "poi-labels",
      "type": "symbol",
      "source": "iran_points",
      "source-layer": "planet_osm_point",
      "minzoom": 14,
      "filter": ["all", ["has", "name"], ["!", ["has", "place"]]],
      "layout": {
        "text-field": "{name}",
        "text-font": ["Vazirmatn Thin", "Arial Regular"],
        "text-size": [
          "interpolate",
          ["linear"],
          ["zoom"],
          14, 9,
          17, 12
        ],
        "symbol-placement": "point",
        "text-padding": 10
      },
      "paint": {
        "text-color": "#d32f2f",
        "text-halo-color": "#ffffff",
        "text-halo-width": 2
      }
    }
  ]
}
```
