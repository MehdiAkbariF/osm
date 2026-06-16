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