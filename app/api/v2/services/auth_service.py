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