from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from app import config
from app.db import get_conn

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.JWT_SECRET, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, config.JWT_SECRET, algorithms=[ALGORITHM])
    except JWTError:
        return None


def get_user_by_username(username: str):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row


def create_user(username: str, password: str):
    password_hash = hash_password(password)
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash),
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id
