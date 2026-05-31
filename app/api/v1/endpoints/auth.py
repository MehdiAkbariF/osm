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