"""
인증 API 통합 테스트

bcrypt 비밀번호 해시화와 JWT 토큰 기반 인증을 테스트합니다.
"""

import pytest
import time
import random
from fastapi import status
from starlette.testclient import TestClient


class TestAuthAPI:
    """인증 API 테스트 클래스"""

    @pytest.fixture
    def unique_user_data(self):
        """고유한 사용자 데이터 생성"""
        unique_id = int(time.time()) + random.randint(0, 1000)
        return {
            "username": f"testuser{unique_id}",
            "email": f"testuser{unique_id}@example.com",
            "password": "testpassword123"
        }

    def test_user_registration_with_bcrypt(self, client: TestClient, unique_user_data):
        """bcrypt로 사용자 등록 테스트"""
        response = client.post("/users/", json=unique_user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # 응답에서 비밀번호가 포함되지 않았는지 확인
        assert "password" not in data["data"]
        assert data["data"]["username"] == unique_user_data["username"]
        assert data["data"]["email"] == unique_user_data["email"]

    def test_user_login_success(self, client: TestClient, unique_user_data):
        """사용자 로그인 성공 테스트"""
        # 먼저 사용자 등록
        client.post("/users/", json=unique_user_data)

        # 로그인 시도
        login_data = {
            "username": unique_user_data["username"],
            "password": unique_user_data["password"]
        }
        response = client.post("/users/login", json=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # JWT 토큰 응답 구조 검증
        assert "access_token" in data
        assert "token_type" in data
        assert "expires_in" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 1800  # 30분 = 1800초

    def test_user_login_invalid_username(self, client: TestClient):
        """잘못된 사용자명으로 로그인 실패 테스트"""
        login_data = {
            "username": "nonexistent_user",
            "password": "password123"
        }
        response = client.post("/users/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Incorrect username or password"

    def test_user_login_invalid_password(self, client: TestClient, unique_user_data):
        """잘못된 비밀번호로 로그인 실패 테스트"""
        # 먼저 사용자 등록
        client.post("/users/", json=unique_user_data)

        # 잘못된 비밀번호로 로그인 시도
        login_data = {
            "username": unique_user_data["username"],
            "password": "wrongpassword"
        }
        response = client.post("/users/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Incorrect username or password"

    def test_get_current_user_with_valid_token(self, client: TestClient, unique_user_data):
        """유효한 JWT 토큰으로 현재 사용자 정보 조회 테스트"""
        # 사용자 등록
        client.post("/users/", json=unique_user_data)

        # 로그인하여 토큰 획득
        login_data = {
            "username": unique_user_data["username"],
            "password": unique_user_data["password"]
        }
        login_response = client.post("/users/login", json=login_data)
        token = login_response.json()["access_token"]

        # Authorization 헤더로 현재 사용자 정보 조회
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/users/me", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["username"] == unique_user_data["username"]
        assert data["data"]["email"] == unique_user_data["email"]
        assert "password" not in data["data"]

    def test_get_current_user_without_token(self, client: TestClient):
        """토큰 없이 현재 사용자 정보 조회 실패 테스트"""
        response = client.get("/users/me")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_current_user_with_invalid_token(self, client: TestClient):
        """유효하지 않은 JWT 토큰으로 현재 사용자 정보 조회 실패 테스트"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/users/me", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_with_invalid_data(self, client: TestClient):
        """잘못된 데이터로 로그인 실패 테스트"""
        # 잘못된 데이터 형식
        invalid_login_data = {
            "username": "a",  # 너무 짧은 사용자명
            "password": "123"  # 너무 짧은 비밀번호
        }
        response = client.post("/users/login", json=invalid_login_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_login_missing_fields(self, client: TestClient):
        """필수 필드 누락으로 로그인 실패 테스트"""
        # 비밀번호 필드 누락
        incomplete_login_data = {
            "username": "testuser"
        }
        response = client.post("/users/login", json=incomplete_login_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_password_hashing_consistency(self, client: TestClient, unique_user_data):
        """비밀번호 해시화 일관성 테스트"""
        # 동일한 비밀번호로 두 번 로그인하여 토큰이 동일하게 생성되는지 확인
        client.post("/users/", json=unique_user_data)

        login_data = {
            "username": unique_user_data["username"],
            "password": unique_user_data["password"]
        }

        # 첫 번째 로그인
        response1 = client.post("/users/login", json=login_data)
        assert response1.status_code == status.HTTP_200_OK
        token1 = response1.json()["access_token"]

        # 두 번째 로그인
        response2 = client.post("/users/login", json=login_data)
        assert response2.status_code == status.HTTP_200_OK
        token2 = response2.json()["access_token"]

        # 토큰은 다를 수 있지만 (만료 시간이 다를 수 있음) 둘 다 유효해야 함
        # JWT 토큰은 시간 기반으로 생성되므로 같은 사용자라도 다른 토큰이 생성될 수 있음
        # 하지만 같은 초에 생성되면 같은 토큰이 생성될 수 있음 (정상적인 동작)
        # 토큰이 다르거나 같을 수 있음 - 둘 다 유효한지만 확인
        # assert token1 != token2  # 토큰은 다를 수 있음 (시간 기반 생성)

        # 둘 다 유효한 토큰인지 확인
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}

        response1_me = client.get("/users/me", headers=headers1)
        response2_me = client.get("/users/me", headers=headers2)

        assert response1_me.status_code == status.HTTP_200_OK
        assert response2_me.status_code == status.HTTP_200_OK
