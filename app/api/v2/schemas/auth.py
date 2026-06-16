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