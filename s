
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
        db, location_id, current_admin.id, reject_data.reason, reject_data.admin_notes
    )
    return MessageResponse(
        message=f"موقعیت {location.title} رد شد",
        success=True,
        location_id=location_id
    )

@router.delete("/admin/{location_id}", response_model=MessageResponse)
async def admin_delete_location(
    location_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    حذف موقعیت توسط ادمین
    """
    location = location_service.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="موقعیت یافت نشد")
    
    location_service.delete_location(db, location_id)
    return MessageResponse(message=f"موقعیت {location.title} حذف شد")


c:\Users\Raven\OSM\app\api\v1\dependencies.py
# app/api/v1/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.auth import auth_service
from app.models.user import User

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    دریافت کاربر جاری از روی توکن JWT
    """
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
    
    # بررسی اینکه کاربر تایید شده باشد (is_active = True)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="حساب کاربری شما هنوز توسط ادمین تایید نشده است"
        )
    
    return user

async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    اطمینان از اینکه کاربر جاری ادمین است
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="شما دسترسی ادمین ندارید"
        )
    return current_user


c:\Users\Raven\OSM\app\core\database.py
# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# اتصال به SQLite برای ذخیره اطلاعات کاربران
# SQLite فایل سبکی است که در کنار پروژه قرار می‌گیرد
engine = create_engine(
    "sqlite:///./data/users.db",  # مسیر ذخیره فایل دیتابیس
    connect_args={"check_same_thread": False}  # لازم برای FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# تابع وابستگی (Dependency) برای دریافت نشست دیتابیس در هر درخواست
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

c:\Users\Raven\OSM\app\models\location.py
# app/models/location.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    
    # اطلاعات اصلی موقعیت
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # مختصات جغرافیایی
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # اطلاعات مکانی (برای نمایش در نقشه)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    province = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    
    # دسته‌بندی (اختیاری)
    category = Column(String(50), nullable=True)  # shop, office, warehouse, other
    tags = Column(Text, nullable=True)  # JSON array یا متن ساده با کاما
    
    # اطلاعات تماس
    phone_number = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    website = Column(String(200), nullable=True)
    
    # ساعت کاری (JSON)
    working_hours = Column(Text, nullable=True)
    
    # تصاویر (JSON array از URLها)
    images = Column(Text, nullable=True)
    
    # فیلدهای وضعیت
    status = Column(String(20), default="pending")  # pending, approved, rejected, blocked
    is_active = Column(Boolean, default=True)
    
    # فیلدهای مدیریتی
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    rejected_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # دلایل رد (اختیاری)
    rejection_reason = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)
    
    # فیلدهای زمانی
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    
    # روابط
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])
    rejecter = relationship("User", foreign_keys=[rejected_by])
    
    def __repr__(self):
        return f"<Location {self.title} ({self.latitude}, {self.longitude})>"

c:\Users\Raven\OSM\app\models\user_location.py
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

c:\Users\Raven\OSM\app\models\user.py
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


c:\Users\Raven\OSM\app\schemas\user.py
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
# app/schemas/location.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

# ========== مدل‌های ورودی (Request) ==========
class LocationBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200, description="عنوان موقعیت")
    description: Optional[str] = Field(None, description="توضیحات")
    latitude: float = Field(..., ge=-90, le=90, description="عرض جغرافیایی")
    longitude: float = Field(..., ge=-180, le=180, description="طول جغرافیایی")
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    working_hours: Optional[str] = None
    images: Optional[str] = None

class LocationCreate(LocationBase):
    pass

class LocationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    working_hours: Optional[str] = None
    images: Optional[str] = None

class LocationApprove(BaseModel):
    admin_notes: Optional[str] = None

class LocationReject(BaseModel):
    reason: str = Field(..., min_length=3, max_length=500, description="دلیل رد موقعیت")
    admin_notes: Optional[str] = None

# ========== مدل‌های خروجی (Response) ==========
class LocationResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    working_hours: Optional[str] = None
    images: Optional[str] = None
    status: str
    is_active: bool
    created_by: int
    created_at: datetime
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

xc:\Users\Raven\OSM\scripts\create_admin.py
# scripts/create_admin.py
import sys
import os

# اضافه کردن مسیر اصلی به PATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.services.auth import auth_service

def create_tables():
    """ایجاد جداول دیتابیس"""
    print("📦 در حال ایجاد جداول دیتابیس...")
    Base.metadata.create_all(bind=engine)
    print("✅ جداول دیتابیس ایجاد شدند")

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

# scripts/create_admin.py
import sys
import os

# اضافه کردن مسیر اصلی به PATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.services.auth import auth_service

def create_tables():
    """ایجاد جداول دیتابیس"""
    print("📦 در حال ایجاد جداول دیتابیس...")
    Base.metadata.create_all(bind=engine)
    print("✅ جداول دیتابیس ایجاد شدند")

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


xc:\Users\Raven\OSM\config.yaml

postgres:
  connection_string: 'postgres://map_admin:map_secure_pass@localhost:5433/iran_map'


fonts:
  - 'fonts'







cache_size_mb: 2048



preferred_encoding: gzip

c:\Users\Raven\OSM\docker-compose.yml
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


