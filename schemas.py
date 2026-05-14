from pydantic import BaseModel


class UserBase(BaseModel):
    username: str


class User(UserBase):
    password: str


class UserInDB(UserBase):
    hashed_password: str


class UserWithRole(UserBase):
    password: str
    role: str = "guest"


class TodoCreate(BaseModel):
    title: str
    description: str = ""


class TodoUpdate(BaseModel):
    title: str
    description: str = ""
    completed: bool = False
