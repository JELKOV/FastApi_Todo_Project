"""
PyTest 공통 픽스처 설정

이 파일은 모든 테스트에서 공통으로 사용되는 픽스처들을 정의합니다.
- 테스트용 데이터베이스 설정
- FastAPI 테스트 클라이언트
- 공통 테스트 데이터
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.users.application.services import UserService
from app.users.domain.entities import UserCreate

# 테스트용 인메모리 SQLite 데이터베이스
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    """테스트용 데이터베이스 엔진"""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine

@pytest.fixture(scope="function")
def session(engine):
    """테스트용 데이터베이스 세션"""
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(session):
    """FastAPI 테스트 클라이언트"""
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def sample_todo_data():
    """샘플 TODO 데이터"""
    return {
        "title": "테스트 할 일",
        "description": "테스트 설명",
        "priority": 3,
        "completed": False
    }

@pytest.fixture
def sample_todo_list():
    """샘플 TODO 목록 데이터"""
    return [
        {
            "title": "첫 번째 할 일",
            "description": "첫 번째 설명",
            "priority": 1,
            "completed": False
        },
        {
            "title": "두 번째 할 일",
            "description": "두 번째 설명",
            "priority": 2,
            "completed": True
        },
        {
            "title": "세 번째 할 일",
            "description": "세 번째 설명",
            "priority": 3,
            "completed": False
        }
    ]

@pytest.fixture
def test_user_data():
    """테스트용 사용자 데이터"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }

@pytest.fixture
def authenticated_client(client, session, test_user_data):
    """인증된 테스트 클라이언트"""
    # 테스트 사용자 생성
    user_service = UserService(session)
    user_create = UserCreate(**test_user_data)
    user = user_service.create_user(user_create)

    # 로그인하여 JWT 토큰 획득
    login_response = client.post("/users/login", json={
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    })

    assert login_response.status_code == 200
    token_data = login_response.json()
    access_token = token_data["access_token"]

    # Authorization 헤더가 포함된 클라이언트 반환
    class AuthenticatedClient:
        def __init__(self, client, token):
            self.client = client
            self.headers = {"Authorization": f"Bearer {token}"}

        def get(self, url, **kwargs):
            kwargs.setdefault("headers", {}).update(self.headers)
            return self.client.get(url, **kwargs)

        def post(self, url, **kwargs):
            kwargs.setdefault("headers", {}).update(self.headers)
            return self.client.post(url, **kwargs)

        def put(self, url, **kwargs):
            kwargs.setdefault("headers", {}).update(self.headers)
            return self.client.put(url, **kwargs)

        def patch(self, url, **kwargs):
            kwargs.setdefault("headers", {}).update(self.headers)
            return self.client.patch(url, **kwargs)

        def delete(self, url, **kwargs):
            kwargs.setdefault("headers", {}).update(self.headers)
            return self.client.delete(url, **kwargs)

    return AuthenticatedClient(client, access_token)
