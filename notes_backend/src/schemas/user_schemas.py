from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    name: Optional[str]
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str
