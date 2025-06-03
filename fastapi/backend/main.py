from fastapi import FastAPI, Depends, HTTPException, status, Query, Request 
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Date, or_ 
from sqlalchemy.ext.declarative import declarative_base
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, date
from pydantic import BaseModel, validator 
from pydantic_settings import BaseSettings
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse 
from typing import Optional 
from sqlalchemy import or_ 
import bcrypt
import os

# --------------------
# 설정 클래스 정의 (환경 변수 로드용)
# --------------------

# Pydantic의 BaseSettings를 상속받아 설정 클래스를 정의합니다.
# .env 파일에 정의된 환경 변수들을 이 클래스의 변수로 자동 로드합니다.
class Settings(BaseSettings):
    DB_USER: str       # .env 파일의 DB_USER 값
    DB_PASSWORD: str   # .env 파일의 DB_PASSWORD 값
    DB_HOST: str       # .env 파일의 DB_HOST 값
    DB_NAME: str       # .env 파일의 DB_NAME 값

    # BaseSettings의 내부 클래스로 설정 관리 방식을 지정합니다.
    class Config:
        env_file = "C:\\Users\\hanmy\\fast_api\\fastapi\\backend\\.gitignore\\.env"
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
settings = Settings()

# --------------------
# 데이터베이스 설정
# --------------------

DATABASE_URL = f"mysql+mysqlconnector://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}/{settings.DB_NAME}"

engine = create_engine(DATABASE_URL)

Base = declarative_base()

# --------------------
# 데이터베이스 모델 정의 (테이블 구조)
# --------------------

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True) # 고유 식별자 (기본 키), 인덱스 생성
    username = Column(String(50), unique=True, nullable=False) # 사용자 이름 (고유해야 하며 비워둘 수 없음)
    email = Column(String(100), unique=True, nullable=False) # 이메일 주소 (고유해야 하며 비워둘 수 없음)
    password = Column(String(255), nullable=False) # 해싱된 비밀번호 저장 (비워둘 수 없음)
    # 아이디 찾기 및 비밀번호 변경 기능을 위해 전화번호와 생년월일 컬럼 추가
    phone_number = Column(String(20), unique=True, nullable=False) # 전화번호 (고유해야 하며 비워둘 수 없음)
    birth_date = Column(Date, nullable=False) # 생년월일 (비워둘 수 없음), DATE 타입 사용
    created_at = Column(DateTime, default=datetime.utcnow) # 사용자 생성 시각 (기본값은 현재 UTC 시각)

# --------------------
# 데이터베이스 세션 관리
# --------------------

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close() 

# --------------------
# 비밀번호 해싱 및 검증 함수
# --------------------

def hash_password(password: str) -> str:
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# --------------------
# Pydantic 모델 (데이터 유효성 검증 및 응답 형태 정의)
# --------------------

class UserCreate(BaseModel):
    username: str        # 사용자 이름
    email: str           # 이메일 주소
    password: str        # 비밀번호
    phone_number: str    # 전화번호 (새로 추가)
    birth_date: date     # 생년월일 (새로 추가), date 타입 사용

class UserResponse(BaseModel):
    id: int              # 사용자 ID
    username: str        # 사용자 이름
    email: str           # 이메일 주소
    phone_number: str    # 전화번호 
    birth_date: date     # 생년월일 
    created_at: datetime # 생성 시각


    class Config:
        orm_mode = True


class PasswordChangeRequest(BaseModel):
    username: str        # 아이디 (사용자 확인용)
    phone_number: str    # 전화번호 (본인 확인용)
    birth_date: date     # 생년월일 (본인 확인용)
    new_password: str    # 새 비밀번호

# --------------------
# FastAPI 애플리케이션 인스턴스 및 엔드포인트 정의
# --------------------

app = FastAPI()

app.mount("/static", StaticFiles(directory="frontend"), name="frontend")

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "null" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # 허용할 출처(Origin) 목록
    allow_credentials=True,     # 쿠키 등 자격 증명 허용 여부
    allow_methods=["*"],        # 허용할 HTTP 메서드 (GET, POST 등 모든 메서드)
    allow_headers=["*"],        # 허용할 HTTP 헤더 (모든 헤더)
)

@app.get("/", response_class=HTMLResponse) 
async def read_root():
    html_file_path = os.path.join("frontend", "signup.html") 
    if not os.path.exists(html_file_path):
        return HTMLResponse("<html><body><h1>Frontend HTML files not found!</h1></body></html>", status_code=404)
    return FileResponse(html_file_path)
# --------------------
# 엔드포인트 정의
# --------------------


@app.post("/signup/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
   
    db_user = db.query(User).filter(
        (User.username == user.username) |
        (User.email == user.email) |
        (User.phone_number == user.phone_number) |
        (User.birth_date == user.birth_date)
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

    return {"message": "Login successful!"}


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

# uvicorn backend.main:app --reload

