"""
사용자 API 통합 테스트

사용자 관련 모든 API 엔드포인트의 통합 테스트를 수행합니다.
CRUD 작업, 검증, 에러 처리를 포함한 완전한 테스트 시나리오를 제공합니다.
"""

import pytest
import time
import random
from fastapi import status
from sqlalchemy.orm import Session
from app.users.domain.models import User


class TestUserAPIComplete:
    """사용자 API 완전 통합 테스트 클래스"""

    @pytest.fixture
    def unique_user_data(self):
        """고유한 사용자 데이터 생성"""
        unique_id = int(time.time()) + random.randint(0, 1000)
        return {
            "username": f"user{unique_id}",
            "email": f"user{unique_id}@example.com",
            "password": "testpassword123"
        }

    @pytest.fixture
    def updated_user_data(self):
        """수정된 사용자 데이터 생성"""
        unique_id = int(time.time()) + random.randint(1001, 2000)
        return {
            "username": f"updated_user{unique_id}",
            "email": f"updated_user{unique_id}@example.com"
        }

    def test_create_user_success(self, client, unique_user_data):
        """사용자 생성 성공 테스트"""
        response = client.post("/users/", json=unique_user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # 응답 구조 검증
        assert "status" in data
        assert "msg" in data
        assert "data" in data
        assert "meta" in data

        # 데이터 내용 검증
        user_data = data["data"]
        assert user_data["username"] == unique_user_data["username"]
        assert user_data["email"] == unique_user_data["email"]
        assert "id" in user_data
        assert "created_at" in user_data
        assert "updated_at" in user_data
        assert "password" not in user_data  # 비밀번호는 응답에 포함되지 않음

        # user_data["id"]는 다른 테스트에서 사용할 수 있음

    def test_create_user_duplicate_username(self, client, unique_user_data):
        """중복 사용자명으로 사용자 생성 실패 테스트"""
        # 첫 번째 사용자 생성
        client.post("/users/", json=unique_user_data)

        # 동일한 사용자명으로 두 번째 사용자 생성 시도
        duplicate_data = unique_user_data.copy()
        duplicate_data["email"] = "different@example.com"  # 이메일은 다르게

        response = client.post("/users/", json=duplicate_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data

    def test_create_user_duplicate_email(self, client, unique_user_data):
        """중복 이메일로 사용자 생성 실패 테스트"""
        # 첫 번째 사용자 생성
        client.post("/users/", json=unique_user_data)

        # 동일한 이메일로 두 번째 사용자 생성 시도
        duplicate_data = unique_user_data.copy()
        duplicate_data["username"] = "different_username"  # 사용자명은 다르게

        response = client.post("/users/", json=duplicate_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data

    def test_create_user_invalid_data(self, client):
        """잘못된 데이터로 사용자 생성 실패 테스트"""
        invalid_data = {
            "username": "a",  # 너무 짧은 사용자명
            "email": "invalid-email",  # 잘못된 이메일 형식
            "password": "123"  # 너무 짧은 비밀번호
        }

        response = client.post("/users/", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        data = response.json()
        assert "data" in data
        assert "validation_errors" in data["data"]

    def test_create_user_missing_required_fields(self, client):
        """필수 필드 누락으로 사용자 생성 실패 테스트"""
        incomplete_data = {
            "username": "testuser"
            # password 필드 누락
        }

        response = client.post("/users/", json=incomplete_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        data = response.json()
        assert "data" in data
        assert "validation_errors" in data["data"]

    def test_get_user_success(self, client, unique_user_data):
        """사용자 조회 성공 테스트"""
        # 사용자 생성
        create_response = client.post("/users/", json=unique_user_data)
        user_id = create_response.json()["data"]["id"]

        # 사용자 조회
        response = client.get(f"/users/{user_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # 응답 구조 검증
        assert "status" in data
        assert "msg" in data
        assert "data" in data

        # 데이터 내용 검증
        user_data = data["data"]
        assert user_data["id"] == user_id
        assert user_data["username"] == unique_user_data["username"]
        assert user_data["email"] == unique_user_data["email"]

    def test_get_user_not_found(self, client):
        """존재하지 않는 사용자 조회 실패 테스트"""
        response = client.get("/users/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data

    def test_get_user_invalid_id(self, client):
        """잘못된 ID 형식으로 사용자 조회 실패 테스트"""
        response = client.get("/users/invalid_id")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        data = response.json()
        assert "data" in data
        assert "validation_errors" in data["data"]

    def test_list_users_success(self, client, unique_user_data):
        """사용자 목록 조회 성공 테스트"""
        # 사용자 생성
        client.post("/users/", json=unique_user_data)

        # 사용자 목록 조회
        response = client.get("/users/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # 응답 구조 검증
        assert "status" in data
        assert "msg" in data
        assert "data" in data

        # 데이터 내용 검증
        list_data = data["data"]
        assert "users" in list_data
        assert "total" in list_data
        assert "page" in list_data
        assert "size" in list_data
        assert isinstance(list_data["users"], list)
        assert list_data["total"] >= 1

    def test_list_users_with_pagination(self, client):
        """페이지네이션을 사용한 사용자 목록 조회 테스트"""
        # 페이지네이션 파라미터로 조회
        response = client.get("/users/?skip=0&limit=5")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        list_data = data["data"]
        assert list_data["page"] == 1  # skip=0, limit=5이므로 page=1
        assert list_data["size"] == 5

    def test_update_user_success(self, client, unique_user_data, updated_user_data):
        """사용자 정보 수정 성공 테스트"""
        # 사용자 생성
        create_response = client.post("/users/", json=unique_user_data)
        user_id = create_response.json()["data"]["id"]

        # 사용자 정보 수정
        response = client.put(f"/users/{user_id}", json=updated_user_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # 수정된 데이터 검증
        user_data = data["data"]
        assert user_data["username"] == updated_user_data["username"]
        assert user_data["email"] == updated_user_data["email"]
        assert user_data["id"] == user_id

    def test_update_user_partial(self, client, unique_user_data):
        """부분 사용자 정보 수정 테스트"""
        # 사용자 생성
        create_response = client.post("/users/", json=unique_user_data)
        user_id = create_response.json()["data"]["id"]

        # 사용자명만 수정
        partial_data = {"username": "updated_username_only"}
        response = client.put(f"/users/{user_id}", json=partial_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        user_data = data["data"]
        assert user_data["username"] == "updated_username_only"
        assert user_data["email"] == unique_user_data["email"]  # 이메일은 변경되지 않음

    def test_update_user_not_found(self, client):
        """존재하지 않는 사용자 수정 실패 테스트"""
        update_data = {"username": "new_username"}
        response = client.put("/users/99999", json=update_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data

    def test_delete_user_success(self, client, unique_user_data):
        """사용자 삭제 성공 테스트"""
        # 사용자 생성
        create_response = client.post("/users/", json=unique_user_data)
        user_id = create_response.json()["data"]["id"]

        # 사용자 삭제
        response = client.delete(f"/users/{user_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["msg"] == "User deleted successfully"

        # 삭제 확인
        get_response = client.get(f"/users/{user_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_user_not_found(self, client):
        """존재하지 않는 사용자 삭제 실패 테스트"""
        response = client.delete("/users/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data

    def test_get_user_by_username_success(self, client, unique_user_data):
        """사용자명으로 사용자 조회 성공 테스트"""
        # 사용자 생성
        client.post("/users/", json=unique_user_data)

        # 사용자명으로 조회
        response = client.get(f"/users/username/{unique_user_data['username']}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        user_data = data["data"]
        assert user_data["username"] == unique_user_data["username"]
        assert user_data["email"] == unique_user_data["email"]

    def test_get_user_by_username_not_found(self, client):
        """존재하지 않는 사용자명으로 조회 실패 테스트"""
        response = client.get("/users/username/nonexistent_user")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data

    def test_get_user_by_email_success(self, client, unique_user_data):
        """이메일로 사용자 조회 성공 테스트"""
        # 사용자 생성
        client.post("/users/", json=unique_user_data)

        # 이메일로 조회
        response = client.get(f"/users/email/{unique_user_data['email']}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        user_data = data["data"]
        assert user_data["username"] == unique_user_data["username"]
        assert user_data["email"] == unique_user_data["email"]

    def test_get_user_by_email_not_found(self, client):
        """존재하지 않는 이메일로 조회 실패 테스트"""
        response = client.get("/users/email/nonexistent@example.com")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data

    def test_complete_user_workflow(self, client):
        """완전한 사용자 워크플로우 테스트"""
        # 1. 사용자 생성
        unique_id = int(time.time()) + random.randint(0, 1000)
        user_data = {
            "username": f"workflow_user{unique_id}",
            "email": f"workflow_user{unique_id}@example.com",
            "password": "testpassword123"
        }

        create_response = client.post("/users/", json=user_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        user_id = create_response.json()["data"]["id"]

        # 2. 사용자 조회
        get_response = client.get(f"/users/{user_id}")
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json()["data"]["username"] == user_data["username"]

        # 3. 사용자 정보 수정
        update_data = {
            "username": f"updated_workflow_user{unique_id}",
            "email": f"updated_workflow_user{unique_id}@example.com"
        }
        update_response = client.put(f"/users/{user_id}", json=update_data)
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["data"]["username"] == update_data["username"]

        # 4. 사용자명으로 조회
        username_response = client.get(f"/users/username/{update_data['username']}")
        assert username_response.status_code == status.HTTP_200_OK

        # 5. 이메일로 조회
        email_response = client.get(f"/users/email/{update_data['email']}")
        assert email_response.status_code == status.HTTP_200_OK

        # 6. 사용자 목록에서 확인
        list_response = client.get("/users/")
        assert list_response.status_code == status.HTTP_200_OK
        users = list_response.json()["data"]["users"]
        user_found = any(user["id"] == user_id for user in users)
        assert user_found

        # 7. 사용자 삭제
        delete_response = client.delete(f"/users/{user_id}")
        assert delete_response.status_code == status.HTTP_200_OK

        # 8. 삭제 확인
        final_get_response = client.get(f"/users/{user_id}")
        assert final_get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_user_response_consistency(self, client, unique_user_data):
        """사용자 응답 형식 일관성 테스트"""
        # 사용자 생성
        create_response = client.post("/users/", json=unique_user_data)
        user_id = create_response.json()["data"]["id"]

        # 다양한 엔드포인트에서 동일한 응답 형식 확인
        endpoints = [
            f"/users/{user_id}",
            f"/users/username/{unique_user_data['username']}",
            f"/users/email/{unique_user_data['email']}"
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            # 모든 응답이 동일한 구조를 가져야 함
            assert "status" in data
            assert "msg" in data
            assert "data" in data
            assert "meta" in data

            # data 필드의 내용도 일관되어야 함
            user_data = data["data"]
            assert "id" in user_data
            assert "username" in user_data
            assert "email" in user_data
            assert "created_at" in user_data
            assert "updated_at" in user_data
            assert "password" not in user_data  # 보안상 비밀번호는 포함되지 않음
