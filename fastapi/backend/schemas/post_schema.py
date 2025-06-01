from pydantic import BaseModel
from datetime import datetime

class PostCreate(BaseModel):
    user_id: int
    title: str
    content: str
    status: str = "공개"

class PostUpdate(BaseModel):
    title: str
    content: str
    status: str

class PostResponse(BaseModel):
    post_id: int
    user_id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    views: int
    status: str

    class Config:
        orm_mode = True