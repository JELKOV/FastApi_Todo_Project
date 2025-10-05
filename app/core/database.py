"""
데이터베이스 설정 모듈

이 모듈은 SQLAlchemy를 사용하여 데이터베이스 연결을 설정하고 관리합니다.
데이터베이스 URL은 환경변수에서 가져오며, SQLite와 PostgreSQL을 지원합니다.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

# 숨은 문자 제거 및 안전한 URL 처리
url = (settings.DATABASE_URL or "").strip().replace("\ufeff", "")
print("DATABASE_URL(repr) =", repr(url))

connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
engine = create_engine(url, pool_pre_ping=True, connect_args=connect_args)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    """
    데이터베이스 세션을 생성하고 관리하는 의존성 주입 함수

    Yields:
        Session: SQLAlchemy 데이터베이스 세션

    사용 예시:
        @app.get("/todos/")
        def get_todos(db: Session = Depends(get_db)):
            return db.query(Todo).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
