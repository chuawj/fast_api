from fastapi import FastAPI, Depends, HTTPException, status, Query, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Date, or_, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime, date
from pydantic import BaseModel, validator
from pydantic_settings import BaseSettings
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from typing import Optional
import bcrypt
import os
from sqlalchemy.orm import joinedload

# -------------------- 환경 변수 --------------------
class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_NAME: str

    class Config:
        env_file = "C:\\Users\\hanmy\\fast_api\\fastapi\\backend\\.env"

settings = Settings()

# -------------------- DB 연결 --------------------
DATABASE_URL = f"mysql+mysqlconnector://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}/{settings.DB_NAME}"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------- 모델 정의 --------------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)
    birth_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    content = Column(String(500))
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")

# -------------------- Pydantic --------------------
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    phone_number: str
    birth_date: date

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    phone_number: str
    birth_date: date
    created_at: datetime
    class Config:
        orm_mode = True

class UserFindRequest(BaseModel):
    phone_number: str
    birth_date: date

class IdentityVerificationRequest(BaseModel):
    username: Optional[str] = None
    phone_number: Optional[str] = None
    birth_date: date
    @validator('username', always=True)
    def check_username_or_phone(cls, v, values):
        if v is None and values.get('phone_number') is None:
            if 'phone_number' not in values or values['phone_number'] is None:
                raise ValueError('아이디(또는 이메일) 또는 전화번호 중 하나는 반드시 입력되어야 합니다.')
        return v

class PasswordChangeByIDRequest(BaseModel):
    user_id: int
    new_password: str

class PasswordChangeRequest(BaseModel):
    username: str
    phone_number: str
    birth_date: date
    new_password: str

# -------------------- 비밀번호 --------------------
def hash_password(password: str) -> str:
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# -------------------- FastAPI --------------------
app = FastAPI()
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "null"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- 라우트 --------------------

@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_file_path = os.path.join("frontend", "signup.html")
    if not os.path.exists(html_file_path):
        return HTMLResponse("<html><body><h1>Frontend HTML files not found!</h1></body></html>", status_code=404)
    return FileResponse(html_file_path)

@app.post("/signup/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(
        (User.username == user.username) |
        (User.email == user.email) |
        (User.phone_number == user.phone_number)
    ).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username, email, or phone number already registered")
    hashed_pw = hash_password(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_pw,
        phone_number=user.phone_number,
        birth_date=user.birth_date
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login/")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.username == form_data.username) |
        (User.email == form_data.username)
    ).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "id": user.id,
        "username": user.username,
        "message": "로그인 성공!"
    }

@app.post("/find-username/")
def find_username(request: UserFindRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.phone_number == request.phone_number,
        User.birth_date == request.birth_date
    ).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="제공된 정보와 일치하는 사용자를 찾을 수 없습니다.")
    return {"username": user.username}

@app.post("/verify-identity-for-pw-change/")
def verify_identity_for_pw_change(request: IdentityVerificationRequest, db: Session = Depends(get_db)):
    identifier_conditions = []
    if request.username:
        identifier_conditions.append(User.username == request.username)
        identifier_conditions.append(User.email == request.username)
    if request.phone_number:
        identifier_conditions.append(User.phone_number == request.phone_number)
    if not identifier_conditions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="아이디(또는 이메일) 또는 전화번호 중 하나는 필수입니다.")
    user = db.query(User).filter(
        (User.birth_date == request.birth_date) &
        (or_(*identifier_conditions))
    ).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="제공된 정보와 일치하는 사용자를 찾을 수 없습니다.")
    return {"message": "본인 확인 성공!", "user_id": user.id}

@app.post("/change-password-by-id/")
def change_password_by_id(request: PasswordChangeByIDRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="유효하지 않은 사용자 정보입니다.")
    user.password = hash_password(request.new_password)
    db.commit()
    return {"message": "비밀번호가 성공적으로 변경되었습니다."}

@app.post("/change-password/")
def change_password(request: PasswordChangeRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.username == request.username,
        User.phone_number == request.phone_number,
        User.birth_date == request.birth_date
    ).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found with provided information")
    user.password = hash_password(request.new_password)
    db.commit()
    return {"message": "Password updated successfully"}

# ------- 게시글 API: user_id → username 함께 내려주기 -------
@app.get("/posts/")
def get_posts(db: Session = Depends(get_db)):
    # Post와 User를 join해서 가져옴
    posts = db.query(Post).options(joinedload(Post.user)).order_by(Post.created_at.desc()).all()
    result = []
    for post in posts:
        result.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "user_id": post.user_id,
            "username": post.user.username if post.user else "탈퇴한 사용자",  # user가 없으면 예외처리
            "created_at": post.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return result

@app.post("/posts/")
def create_post(data: dict, db: Session = Depends(get_db)):
    title = data.get("title")
    content = data.get("content")
    user_id = data.get("user_id")
    if not title or not content or not user_id:
        raise HTTPException(status_code=400, detail="필수 데이터 누락")
    # 사용자 존재 여부 확인
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="유효하지 않은 사용자입니다.")
    post = Post(title=title, content=content, user_id=user_id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "user_id": post.user_id,
        "username": user.username,
        "created_at": post.created_at.isoformat()
    }

# --------- HTML 라우팅 ---------
@app.get("/login.html")
def serve_login_html():
    return FileResponse("frontend/login.html")

@app.get("/find_username.html")
def serve_find_username_html():
    return FileResponse("frontend/find_username.html")

@app.get("/change_password.html")
def serve_change_password_html():
    return FileResponse("frontend/change_password.html")

@app.get("/signup.html")
def serve_signup_html():
    return FileResponse("frontend/signup.html")

@app.get("/post.html")
def serve_post_html():
    return FileResponse("frontend/post.html")
