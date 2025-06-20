# init_db.py
# 이 스크립트는 프로젝트의 최상위 디렉터리 (backend 및 frontend 폴더와 같은 레벨)에 위치해야 합니다.

import os
import sys

# 프로젝트의 루트 디렉터리(이 파일이 있는 디렉터리)를 Python 경로에 추가합니다.
# 이를 통해 'backend.main'과 같은 모듈을 임포트할 수 있습니다.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

# backend.main 모듈에서 필요한 요소들을 임포트합니다.
# 만약 main.py 파일 이름이 다르거나 backend 폴더 구조가 다르다면 이 부분을 수정해야 합니다.
try:
    # Base: SQLAlchemy 선언적 베이스 (모델 정의의 기반)
    # engine: 데이터베이스 연결 엔진
    # SessionLocal: 데이터베이스 세션 팩토리 (여기서는 직접 사용하지는 않지만 임포트 예시)
    # User: 정의된 SQLAlchemy 모델 클래스 (어떤 테이블이 있는지 확인하기 위해 임포트)
    # settings: 환경 변수 설정 (데이터베이스 URL 구성에 필요)
    from backend.main import Base, engine, SessionLocal, User, settings
    print("Successfully imported Base, engine, SessionLocal, User, settings from backend.main")
except ImportError as e:
    print(f"Error importing from backend.main: {e}")
    print("Please ensure:")
    print("1. 'init_db.py' is in the project root (same level as 'backend').")
    print("2. 'main.py' exists inside the 'backend' folder.")
    print("3. The necessary objects (Base, engine, SessionLocal, User, settings) are defined in 'backend.main.py'.")
    sys.exit(1) # 임포트 실패 시 스크립트 실행 중단

# 외래 키 제약 조건 비활성화를 위해 필요한 임포트 (MySQL 전용)
from sqlalchemy import text # SQL 텍스트 구문 실행을 위해 임포트

def create_tables():
    """
    정의된 모델에 따라 데이터베이스 테이블을 생성합니다.
    테이블이 이미 존재하면 오류 없이 건너뜁니다 (SQLAlchemy의 create_all 동작 방식).
    """
    print("Attempting to create database tables...")
    try:
        # Base.metadata에 등록된 모든 테이블에 대해 CREATE TABLE 문 실행
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully or already existed.")
    except Exception as e:
        print(f"An error occurred during table creation: {e}")
        print("Please check your database connection settings (.env file) and database server status.")


def drop_tables():
    """
    정의된 모든 데이터베이스 테이블을 삭제합니다.
    이것은 해당 테이블의 모든 데이터를 영구적으로 삭제합니다!
    외래 키 제약 조건이 있다면 순서에 주의하거나 비활성화해야 할 수 있습니다.
    """
    print("Attempting to drop all database tables...")
    try:
        # MySQL/MariaDB의 경우 외래 키 제약 조건 임시 비활성화 필요
        if engine.name == 'mysql':
            with engine.connect() as conn:
                 # 직접 SQL 구문 실행
                conn.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
                print("Foreign key checks temporarily disabled.")

        # Base.metadata에 등록된 모든 테이블에 대해 DROP TABLE 문 실행
        # drop_all은 외래 키 제약 조건이 있다면 순서 문제로 실패할 수 있습니다.
        # 보통 recreate_database 함수에서 drop_tables와 create_tables를 함께 사용합니다.
        Base.metadata.drop_all(bind=engine)
        print("All tables dropped successfully.")

        if engine.name == 'mysql':
             with engine.connect() as conn:
                conn.execute(text("SET FOREIGN_KEY_CHECKS=1;"))
                print("Foreign key checks re-enabled.")

    except Exception as e:
        print(f"An error occurred during table dropping: {e}")
        print("Check Foreign Key constraints or database permissions.")


def recreate_database():
    """
    데이터베이스를 초기 상태로 재구축합니다.
    주의: 이 작업을 실행하면 'Login_SignUp' 데이터베이스의 모든 데이터가 영구적으로 삭제됩니다!
    """
    print("\n--- Recreating database ---")
    confirm = input("WARNING: This will delete ALL data in your database. Type 'yes' to continue: ")
    if confirm.lower() == 'yes':
        drop_tables()
        create_tables()
        print("--- Database re-created successfully ---")
    else:
        print("Database re-creation cancelled.")


def truncate_tables():
    """
    모든 테이블의 데이터를 삭제합니다 (TRUNCATE). 테이블 구조는 유지됩니다.
    주의: 이 작업을 실행하면 해당 테이블의 모든 데이터가 영구적으로 삭제됩니다!
    외래 키 제약 조건에 주의하세요.
    """
    print("\n--- Truncating all table data ---")
    confirm = input("WARNING: This will delete ALL data from all tables. Type 'yes' to continue: ")
    if confirm.lower() == 'yes':
        try:
            with engine.connect() as conn:
                trans = conn.begin() # 트랜잭션 시작 (선택 사항이지만 안전)

                # MySQL/MariaDB의 경우 외래 키 제약 조건 임시 비활성화 필요
                if engine.name == 'mysql':
                    conn.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
                    print("Foreign key checks temporarily disabled.")

                # 테이블 목록을 가져와서 TRUNCATE 실행
                # Base.metadata.tables.values()는 매핑된 모든 Table 객체를 반환합니다.
                for table in Base.metadata.tables.values():
                    print(f"Truncating table: {table.name}")
                    # TRUNCATE TABLE SQL 구문 직접 실행
                    conn.execute(text(f"TRUNCATE TABLE {table.name};"))

                if engine.name == 'mysql':
                    conn.execute(text("SET FOREIGN_KEY_CHECKS=1;"))
                    print("Foreign key checks re-enabled.")

                trans.commit() # 변경사항 커밋
                print("All table data truncated successfully.")

        except Exception as e:
            if 'trans' in locals() and trans.is_active:
                 trans.rollback() # 오류 발생 시 롤백
            print(f"An error occurred during truncation: {e}")
            print("Check Foreign Key constraints or database permissions.")
    else:
        print("Table truncation cancelled.")


# 스크립트가 직접 실행될 때의 동작 정의
if __name__ == "__main__":
    print("Database Initialization Script")
    print("-----------------------------")
    print("Available actions:")
    print("1. Create tables (if they don't exist)")
    print("2. Drop all tables (Deletes all data!)")
    print("3. Recreate database (Drop all & Create all - Deletes all data!)")
    print("4. Truncate all table data (Keeps schema, deletes data!)")
    print("5. Exit")

    while True:
        choice = input("Enter action number (1-5): ")

        if choice == '1':
            create_tables()
        elif choice == '2':
            confirm = input("Are you sure you want to drop ALL tables? Type 'yes' to confirm: ")
            if confirm.lower() == 'yes':
                 drop_tables()
            else:
                 print("Action cancelled.")
        elif choice == '3':
            recreate_database() # recreate_database 함수 내에서 이미 확인 절차 포함
        elif choice == '4':
            truncate_tables() # truncate_tables 함수 내에서 이미 확인 절차 포함
        elif choice == '5':
            print("Exiting script.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")
        print("-" * 30) # 구분선 출력

