
# Задание 6.1 и 6.2
import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from schemas import User, UserInDB

security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 6.1 — хардкод юзер
VALID_USERNAME = "admin"
VALID_PASSWORD = "secret"

# 6.2 — in-memory база
fake_users_db = {}

# роутер для 6.1
legacy_router = APIRouter(prefix="/login-basic", tags=["6.1 Basic Auth"])

# роутер для 6.2
router = APIRouter(prefix="/basic", tags=["6.2 Basic Auth + bcrypt"])


# --- 6.1 ---

def check_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, VALID_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, VALID_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@legacy_router.get("/login")
def login_61(username: str = Depends(check_credentials)):
    return "You got my secret, welcome"


# --- 6.2 ---

def auth_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = None
    for db_username, db_user in fake_users_db.items():
        if secrets.compare_digest(db_username, credentials.username):
            user = db_user
            break

    if user is None or not pwd_context.verify(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user


@router.post("/register")
def register(user: User):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed = pwd_context.hash(user.password)
    fake_users_db[user.username] = UserInDB(username=user.username, hashed_password=hashed)
    return {"message": f"User {user.username} registered successfully"}


@router.get("/login")
def login_62(user: UserInDB = Depends(auth_user)):
    return {"message": f"Welcome, {user.username}!"}
