from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import hashlib
import secrets
from pydantic import BaseModel
import sqlite3
import json
import uuid

# Configuration JWT
SECRET_KEY = "votre-secret-key-tres-securisee-a-changer-en-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 jours

# Hashage simple avec hashlib (alternative à bcrypt)
def hash_password(password: str) -> str:
    """Hash un mot de passe avec SHA256 + sel"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((password + salt).encode())
    return f"{salt}:{hash_obj.hexdigest()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe"""
    try:
        salt, stored_hash = hashed_password.split(":")
        hash_obj = hashlib.sha256((plain_password + salt).encode())
        return hash_obj.hexdigest() == stored_hash
    except:
        return False

# Modèles
class User(BaseModel):
    id: str
    email: str
    name: str
    company: Optional[str] = None
    created_at: str

class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    company: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class TokenData(BaseModel):
    email: Optional[str] = None

# Base de données des utilisateurs
class UserDB:
    def __init__(self, db_path: str = "hireflow.db"):
        self.db_path = db_path
        self.init_user_table()
    
    def init_user_table(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    name TEXT NOT NULL,
                    company TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def get_user_by_email(self, email: str) -> Optional[dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "email": row[1],
                    "password": row[2],
                    "name": row[3],
                    "company": row[4],
                    "created_at": row[5]
                }
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "email": row[1],
                    "password": row[2],
                    "name": row[3],
                    "company": row[4],
                    "created_at": row[5]
                }
            return None
    
    def create_user(self, user: UserCreate) -> dict:
        user_id = str(uuid.uuid4())[:8]
        hashed_password = hash_password(user.password)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (id, email, password, name, company)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, user.email, hashed_password, user.name, user.company))
            conn.commit()
        
        return {
            "id": user_id,
            "email": user.email,
            "name": user.name,
            "company": user.company,
            "created_at": datetime.now().isoformat()
        }

user_db = UserDB()

def authenticate_user(email: str, password: str):
    user = user_db.get_user_by_email(email)
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            return None
        user = user_db.get_user_by_email(email)
        return user
    except JWTError:
        return None