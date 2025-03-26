from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Note(BaseModel):
    note: str


class NoteCreate(BaseModel):
    title: Optional[str] = None
    note: str


class NoteOut(BaseModel):
    id: int
    title: str
    note: str
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True


class NoteResponse(BaseModel):
    data: List[NoteOut]
    limit: int
    page: int
    total: int
