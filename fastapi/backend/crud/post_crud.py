from sqlalchemy.orm import Session
from backend.models.post_model import Post
from backend.schemas.post_schema import PostCreate, PostUpdate

def create_post(db: Session, post: PostCreate):
    db_post = Post(**post.dict())  # user_id 제거 후에도 dict 그대로 사용 가능
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_post(db: Session, post_id: int):
    return db.query(Post).filter(Post.post_id == post_id).first()

def get_all_posts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Post).offset(skip).limit(limit).all()

def update_post(db: Session, post_id: int, post_data: PostUpdate):
    db_post = get_post(db, post_id)
    if not db_post:
        return None
    for field, value in post_data.dict().items():
        setattr(db_post, field, value)
    db.commit()
    db.refresh(db_post)
    return db_post

def delete_post(db: Session, post_id: int):
    db_post = get_post(db, post_id)
    if db_post:
        db.delete(db_post)
        db.commit()
    return db_post
