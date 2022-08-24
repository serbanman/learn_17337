from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import sessions
from .recommendations import RecommendationsService
from .models import Category as CategoryModel


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
async def get_recs(user_id: int):
    service = RecommendationsService(user_id)
    service.process()
    return service.result