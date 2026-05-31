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