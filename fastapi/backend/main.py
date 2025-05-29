from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from pydantic import BaseModel
import bcrypt
# 환경 변수 로드를 위해 BaseSettings 또는 python-dotenv 임포트
# Pydantic의 BaseSettings를 사용하는 것이 일반적입니다.
from pydantic_settings import BaseSettings # pydantic v2 이상에서는 pydantic_settings에서 임포트
# 또는 python-dotenv를 사용하는 경우:
# from dotenv import load_dotenv
# import os

# .env 파일에서 환경 변수 로드 (python-dotenv 사용하는 경우)
# load_dotenv()


# ----<설정 클래스 정의 (환경 변수 로드용)>------

# Pydantic의 BaseSettings를 상속받아 설정 클래스 정의
class Settings(BaseSettings):
    # .env 파일에서 DB_USER, DB_PASSWORD 등의 환경 변수 값을 자동으로 불러옵니다.
    # 환경 변수 이름과 클래스 변수 이름을 동일하게 설정합니다.
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_NAME: str

    # Pydantic BaseSettings의 내부 클래스 (설정 관리)
    class Config:
        # .env 파일 경로 지정
        env_file = "C:\\Users\\hanmy\\fast_api\\fastapi\\backend\\.gitignore\\.env"


# 설정 객체 생성
settings = Settings()


# ----<데이터베이스 설정>------
# MySQL 데이터베이스 연결 URL을 환경 변수에서 읽어온 값으로 조합
# settings 객체를 통해 .env 파일의 값에 접근합니다.
DATABASE_URL = f"mysql+mysqlconnector://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}/{settings.DB_NAME}"

# 또는 python-dotenv 사용 시:
# DATABASE_URL = f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"


# SQLAlchemy 엔진 생성
engine = create_engine(DATABASE_URL)

# SQLAlchemy 선언적 베이스 생성
Base = declarative_base()

# 사용자 모델 정의 (users 테이블)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False) # 해싱된 비밀번호 저장
    created_at = Column(DateTime, default=datetime.utcnow)

# 테이블 생성 (이미 존재하면 이 부분은 건너뛰거나 오류 발생)
# Base.metadata.create_all(bind=engine) # 이미 테이블이 있음을 확인하셨으므로 주석 처리하거나 제거하셔도 됩니다.

# 데이터베이스 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 데이터베이스 세션 의존성 주입 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----<비밀번호 해싱 및 검증 함수>----


def hash_password(password: str) -> str:
    # 비밀번호를 바이트로 인코딩하고 해싱합니다.
    # bcrypt.gensalt()는 솔트(Salt)를 생성하여 동일한 비밀번호라도 매번 다른 해시 값을 갖도록 합니다.
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    # 해시된 바이트를 문자열로 디코딩하여 반환합니다.
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # 입력된 비밀번호(평문)와 저장된 해시된 비밀번호를 비교합니다.
    # 내부적으로 해시된 비밀번호에서 솔트를 추출하여 평문을 다시 해싱한 후 비교합니다.
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


# ----<Pydantic 모델 (스키마 정의)>----


# 회원가입 요청 스키마
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

# 사용자 정보 응답 스키마 (비밀번호 제외)
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        orm_mode = True # SQLAlchemy 모델 객체를 Pydantic 모델로 변환 가능하게 함


# -----<FastAPI 애플리케이션 및 엔드포인트>----


app = FastAPI()

# 회원가입 엔드포인트
@app.post("/signup/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # 사용자 이름 또는 이메일이 이미 존재하는지 확인
    db_user = db.query(User).filter((User.username == user.username) | (User.email == user.email)).first()
    if db_user:
        # 이미 존재하는 경우 에러 응답
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already registered")

    # 비밀번호 해싱
    hashed_pw = hash_password(user.password)

    # 새로운 사용자 객체 생성 및 데이터베이스에 추가
    new_user = User(username=user.username, email=user.email, password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user) # 데이터베이스에서 자동 생성된 id 등을 가져옴

    # 회원가입 성공 응답 (비밀번호는 제외하고 응답)
    return new_user

# 로그인 엔드포인트 (OAuth2PasswordRequestForm 사용)
@app.post("/login/")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # username 또는 email로 사용자를 찾음 (form_data의 username 필드를 사용)
    # 실제로는 username/email 중 하나로 로그인 가능하도록 구현하는 것이 일반적
    # 여기서는 OAuth2PasswordRequestForm의 username 필드를 사용하며, 사용자가 username이나 email을 입력한다고 가정
    user = db.query(User).filter((User.username == form_data.username) | (User.email == form_data.username)).first()

    # 사용자가 없거나 비밀번호가 일치하지 않는 경우
    if not user or not verify_password(form_data.password, user.password):
        # 인증 실패 에러 응답
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


    return {"message": "Login successful!"}

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


# uvicorn backend.main:app --reload

