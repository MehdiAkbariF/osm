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