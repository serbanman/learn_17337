from sqlalchemy import Column, Integer, String, ForeignKey, DATETIME, JSON
from database import Base


class Category(Base):
    __tablename__ = "content_category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)


class Tag(Base):
    __tablename__ = "content_tag"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(Integer, ForeignKey("content_category.id"))


class Video(Base):
    __tablename__ = "content_video"

    id = Column(String, primary_key=True, index=True)
    r_id = Column(String)
    title = Column(String)
    description = Column(String)
    created_at = Column(DATETIME)
    total_views = Column(Integer)
    unique_views = Column(Integer)
    category = Column(Integer)
    tags = Column(JSON)


class History(Base):
    __tablename__ = 'users_history'

    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer)
    """ SCHEMA: shard_id__video_id"""
    video_id = Column(String)
