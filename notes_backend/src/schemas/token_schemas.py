from typing import Optional

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    id: int
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None
    email: Optional[EmailStr] = None
