import datetime

from pydantic import BaseModel


class Category(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class Tag(BaseModel):
    id: int
    category: int

    class Config:
        orm_mode = True


class VideoBase(BaseModel):
    id: str
    r_id: str
    title: str
    description: str
    created_at: datetime.datetime
    total_views: int
    unique_views: int
    category: int
    tags: list
