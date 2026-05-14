# Задания 6.4, 6.5, 7.1
import secrets
import random
from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter, HTTPException, Header, Request
from passlib.context import CryptContext
from slowapi import Limiter
from slowapi.util import get_remote_address
from schemas import User, UserWithRole

limiter = Limiter(key_func=get_remote_address)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "jwt_secret_key_456"
ALGORITHM = "HS256"

fake_users_db = {}

router = APIRouter(tags=["6.4 / 6.5 / 7.1 JWT + RBAC"])


def make_token(username: str, role: str = "user") -> str:
    expire = datetime.utcnow() + timedelta(minutes=60)
    payload = {"sub": username, "role": role, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(authorization: str):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Token missing")
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Bad token format")
    token = parts[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# --- 6.4 ---

@router.post("/login-jwt", summary="6.4 — JWT логин (заглушка)")
def login_64(username: str, password: str):
    # заглушка — рандомно возвращает True или False
    is_valid = random.choice([True, False])
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = make_token(username)
    return {"access_token": token}


@router.get("/protected-64", summary="6.4 — Защищённый ресурс")
def protected_64(authorization: str = Header(None)):
    payload = decode_token(authorization)
    return {"message": f"Access granted, {payload['sub']}!"}


# --- 6.5 ---

@router.post("/register", status_code=201, summary="6.5 — Регистрация")
@limiter.limit("1/minute")
def register(request: Request, user: User):
    for db_user in fake_users_db:
        if secrets.compare_digest(db_user, user.username):
            raise HTTPException(status_code=409, detail="User already exists")
    hashed = pwd_context.hash(user.password)
    fake_users_db[user.username] = {"hashed_password": hashed, "role": "user"}
    return {"message": "New user created"}


@router.post("/login", summary="6.5 — JWT логин")
@limiter.limit("5/minute")
def login_65(request: Request, user: User):
    found_user = None
    found_data = None
    for db_user, db_data in fake_users_db.items():
        if secrets.compare_digest(db_user, user.username):
            found_user = db_user
            found_data = db_data
            break

    if found_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not pwd_context.verify(user.password, found_data["hashed_password"]):
        raise HTTPException(status_code=401, detail="Authorization failed")

    token = make_token(found_user, found_data["role"])
    return {"access_token": token, "token_type": "bearer"}


@router.get("/protected_resource", summary="6.5 — Защищённый ресурс")
def protected_65(authorization: str = Header(None)):
    decode_token(authorization)
    return {"message": "Access granted"}


# --- 7.1 RBAC ---

@router.post("/register-rbac", status_code=201, summary="7.1 — Регистрация с ролью")
def register_rbac(user: UserWithRole):
    if user.role not in ("admin", "user", "guest"):
        raise HTTPException(status_code=400, detail="Неизвестная роль")
    for db_user in fake_users_db:
        if secrets.compare_digest(db_user, user.username):
            raise HTTPException(status_code=409, detail="User already exists")
    hashed = pwd_context.hash(user.password)
    fake_users_db[user.username] = {"hashed_password": hashed, "role": user.role}
    return {"message": f"User {user.username} registered with role '{user.role}'"}


@router.get("/resource", summary="7.1 — Читать (все роли)")
def read_resource(authorization: str = Header(None)):
    decode_token(authorization)
    return {"data": "Вот данные ресурса"}


@router.put("/resource", summary="7.1 — Обновить (admin, user)")
def update_resource(authorization: str = Header(None)):
    payload = decode_token(authorization)
    if payload["role"] not in ("admin", "user"):
        raise HTTPException(status_code=403, detail="Нет доступа")
    return {"message": "Ресурс обновлён"}


@router.post("/resource", summary="7.1 — Создать (только admin)")
def create_resource(authorization: str = Header(None)):
    payload = decode_token(authorization)
    if payload["role"] != "admin":
        raise HTTPException(status_code=403, detail="Нет доступа")
    return {"message": "Ресурс создан"}


@router.delete("/resource", summary="7.1 — Удалить (только admin)")
def delete_resource(authorization: str = Header(None)):
    payload = decode_token(authorization)
    if payload["role"] != "admin":
        raise HTTPException(status_code=403, detail="Нет доступа")
    return {"message": "Ресурс удалён"}
