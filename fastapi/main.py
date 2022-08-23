from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import sessions
from recommendations import HistoryService
from schemas import Category as CategorySchema
from models import Category as CategoryModel, Video as VideoModel
from typing import List


def get_default_db():
    db = sessions['default_db']()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


@app.get("/test")
async def test():
    return {"message": "test"}


@app.get("/test2")
async def test2(db: Session = Depends(get_default_db)):
    q = db.query(CategoryModel).all()
    return q


@app.get("/{user_id}")
async def test2(user_id: int):
    print(user_id)
    # result = []
    service = HistoryService(user_id)
    result = service.user_history
    # for session in sessions:
    #     if 'video' in session:
    #         s = sessions[session]()
    #         result.append(s.query(VideoModel).all())
    #         s.close()
    # q = db.query(CategoryModel).all()
    return result
