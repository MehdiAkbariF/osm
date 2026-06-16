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