from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.schemas import post_schema
from backend.crud import post_crud
from backend.models import post_model

router = APIRouter(prefix="/posts", tags=["게시글"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=post_schema.PostResponse)
def create(post: post_schema.PostCreate, db: Session = Depends(get_db)):
    return post_crud.create_post(db, post)

@router.get("/{post_id}", response_model=post_schema.PostResponse)
def read(post_id: int, db: Session = Depends(get_db)):
    db_post = post_crud.get_post(db, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="게시글이 존재하지 않습니다.")
    return db_post

@router.get("/", response_model=list[post_schema.PostResponse])
def read_all(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return post_crud.get_all_posts(db, skip, limit)

@router.put("/{post_id}", response_model=post_schema.PostResponse)
def update(post_id: int, post: post_schema.PostUpdate, db: Session = Depends(get_db)):
    updated = post_crud.update_post(db, post_id, post)
    if not updated:
        raise HTTPException(status_code=404, detail="수정할 게시글이 없습니다.")
    return updated

@router.delete("/{post_id}")
def delete(post_id: int, db: Session = Depends(get_db)):
    deleted = post_crud.delete_post(db, post_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="삭제할 게시글이 없습니다.")
    return {"message": "삭제 성공"}