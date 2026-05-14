# Задание 8.1
from fastapi import APIRouter
from schemas import User
from database import get_db_connection

router = APIRouter(prefix="/db", tags=["8.1 SQLite регистрация"])


@router.post("/register")
def register(user: User):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (user.username, user.password)
    )
    conn.commit()
    conn.close()
    return {"message": "User registered successfully!"}
