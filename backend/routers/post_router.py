from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.schemas import post_schema
from backend.crud import post_crud
from backend.models import post_model

router = APIRouter(prefix="/posts", tags=["게시글"])

# 데이터베이스 세션 주입
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 게시글 생성
@router.post("/", response_model=post_schema.PostResponse)
def create(post: post_schema.PostCreate, db: Session = Depends(get_db)):
    return post_crud.create_post(db, post)

# 단일 게시글 조회
@router.get("/{post_id}", response_model=post_schema.PostResponse)
def read(post_id: int, db: Session = Depends(get_db)):
    db_post = post_crud.get_post(db, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="게시글이 존재하지 않습니다.")
    return db_post

# 전체 게시글 목록 조회
@router.get("/", response_model=list[post_schema.PostResponse])
def read_all(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return post_crud.get_all_posts(db, skip, limit)

# 게시글 수정
@router.put("/{post_id}", response_model=post_schema.PostResponse)
def update(post_id: int, post: post_schema.PostUpdate, db: Session = Depends(get_db)):
    updated = post_crud.update_post(db, post_id, post)
    if not updated:
        raise HTTPException(status_code=404, detail="수정할 게시글이 없습니다.")
    return updated

# 게시글 삭제
@router.delete("/{post_id}")
def delete(post_id: int, db: Session = Depends(get_db)):
    deleted = post_crud.delete_post(db, post_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="삭제할 게시글이 없습니다.")
    return {"message": "삭제 성공"}
