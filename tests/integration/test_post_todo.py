"""
POST API 테스트

TODO 생성 API의 다양한 시나리오를 테스트합니다.
- 유효한 데이터로 TODO 생성
- 잘못된 데이터로 TODO 생성 (422)
- 필수 필드 누락 테스트
- 데이터 검증 규칙 테스트
"""

import pytest
from fastapi.testclient import TestClient


class TestPostTodoAPI:
    """TODO 생성 API 테스트 클래스"""

    def test_create_todo_with_valid_data(self, client: TestClient, sample_todo_data):
        """유효한 데이터로 TODO 생성 테스트"""
        response = client.post("/todos/", json=sample_todo_data)

        assert response.status_code == 201
        data = response.json()

        # 응답 구조 검증
        assert "status" in data
        assert "msg" in data
        assert "data" in data
        assert "meta" in data

        # 데이터 내용 검증
        assert data["status"] == 201
        assert data["msg"] == "Todo created successfully"
        assert data["data"]["title"] == sample_todo_data["title"]
        assert data["data"]["description"] == sample_todo_data["description"]
        assert data["data"]["priority"] == sample_todo_data["priority"]
        assert data["data"]["completed"] == sample_todo_data["completed"]
        assert "id" in data["data"]
        assert "created_at" in data["data"]
        assert "updated_at" in data["data"]

        # Location 헤더 검증
        assert "Location" in response.headers
        assert f"/todos/{data['data']['id']}" in response.headers["Location"]

    def test_create_todo_with_minimal_data(self, client: TestClient):
        """최소 데이터로 TODO 생성 테스트"""
        minimal_data = {"title": "최소 데이터 TODO"}

        response = client.post("/todos/", json=minimal_data)

        assert response.status_code == 201
        data = response.json()

        # 기본값이 적용되었는지 확인
        assert data["data"]["title"] == "최소 데이터 TODO"
        assert data["data"]["description"] is None
        assert data["data"]["priority"] == 1  # 기본값
        assert data["data"]["completed"] == False  # 기본값

    def test_create_todo_with_all_fields(self, client: TestClient):
        """모든 필드가 포함된 TODO 생성 테스트"""
        full_data = {
            "title": "완전한 TODO",
            "description": "모든 필드가 포함된 TODO 설명",
            "priority": 4,
            "completed": True
        }

        response = client.post("/todos/", json=full_data)

        assert response.status_code == 201
        data = response.json()

        # 모든 필드가 정확히 저장되었는지 확인
        assert data["data"]["title"] == full_data["title"]
        assert data["data"]["description"] == full_data["description"]
        assert data["data"]["priority"] == full_data["priority"]
        assert data["data"]["completed"] == full_data["completed"]

    def test_create_todo_with_empty_title(self, client: TestClient):
        """빈 제목으로 TODO 생성 테스트 (422)"""
        invalid_data = {
            "title": "",
            "description": "빈 제목 테스트",
            "priority": 1
        }

        response = client.post("/todos/", json=invalid_data)

        assert response.status_code == 422
        data = response.json()

        # 검증 오류 확인
        assert "validation_errors" in data["data"]
        assert any("String should have at least 1 character" in str(error)
                  for error in data["data"]["validation_errors"])

    def test_create_todo_with_too_long_title(self, client: TestClient):
        """너무 긴 제목으로 TODO 생성 테스트 (422)"""
        invalid_data = {
            "title": "a" * 201,  # 200자 초과
            "description": "긴 제목 테스트",
            "priority": 1
        }

        response = client.post("/todos/", json=invalid_data)

        assert response.status_code == 422
        data = response.json()

        # 검증 오류 확인
        assert "validation_errors" in data["data"]
        assert any("String should have at most 200 characters" in str(error)
                  for error in data["data"]["validation_errors"])

    def test_create_todo_with_too_long_description(self, client: TestClient):
        """너무 긴 설명으로 TODO 생성 테스트 (422)"""
        invalid_data = {
            "title": "긴 설명 테스트",
            "description": "a" * 1001,  # 1000자 초과
            "priority": 1
        }

        response = client.post("/todos/", json=invalid_data)

        assert response.status_code == 422
        data = response.json()

        # 검증 오류 확인
        assert "validation_errors" in data["data"]
        assert any("String should have at most 1000 characters" in str(error)
                  for error in data["data"]["validation_errors"])

    def test_create_todo_with_invalid_priority_too_high(self, client: TestClient):
        """너무 높은 우선순위로 TODO 생성 테스트 (422)"""
        invalid_data = {
            "title": "높은 우선순위 테스트",
            "description": "우선순위 6 테스트",
            "priority": 6  # 5 초과
        }

        response = client.post("/todos/", json=invalid_data)

        assert response.status_code == 422
        data = response.json()

        # 검증 오류 확인
        assert "validation_errors" in data["data"]
        assert any("Input should be less than or equal to 5" in str(error)
                  for error in data["data"]["validation_errors"])

    def test_create_todo_with_invalid_priority_too_low(self, client: TestClient):
        """너무 낮은 우선순위로 TODO 생성 테스트 (422)"""
        invalid_data = {
            "title": "낮은 우선순위 테스트",
            "description": "우선순위 0 테스트",
            "priority": 0  # 1 미만
        }

        response = client.post("/todos/", json=invalid_data)

        assert response.status_code == 422
        data = response.json()

        # 검증 오류 확인
        assert "validation_errors" in data["data"]
        assert any("Input should be greater than or equal to 1" in str(error)
                  for error in data["data"]["validation_errors"])

    def test_create_todo_with_negative_priority(self, client: TestClient):
        """음수 우선순위로 TODO 생성 테스트 (422)"""
        invalid_data = {
            "title": "음수 우선순위 테스트",
            "description": "음수 우선순위 테스트",
            "priority": -1
        }

        response = client.post("/todos/", json=invalid_data)

        assert response.status_code == 422
        data = response.json()

        # 검증 오류 확인
        assert "validation_errors" in data["data"]
        assert any("Input should be greater than or equal to 1" in str(error)
                  for error in data["data"]["validation_errors"])

    def test_create_todo_missing_required_fields(self, client: TestClient):
        """필수 필드 누락 테스트 (422)"""
        # title 필드 누락
        invalid_data = {
            "description": "제목 없음",
            "priority": 1
        }

        response = client.post("/todos/", json=invalid_data)

        assert response.status_code == 422
        data = response.json()

        # 검증 오류 확인
        assert "validation_errors" in data["data"]
        assert any("title" in str(error) for error in data["data"]["validation_errors"])

    def test_create_todo_with_invalid_field_types(self, client: TestClient):
        """잘못된 필드 타입 테스트 (422)"""
        invalid_data = {
            "title": 123,  # 숫자 (문자열이어야 함)
            "description": True,  # 불린 (문자열이어야 함)
            "priority": "high",  # 문자열 (숫자여야 함)
            "completed": "yes"  # 문자열 (불린이어야 함)
        }

        response = client.post("/todos/", json=invalid_data)

        assert response.status_code == 422
        data = response.json()

        # 검증 오류 확인
        assert "validation_errors" in data["data"]
        # 여러 필드에서 타입 오류가 발생해야 함 (completed 필드는 자동 변환될 수 있음)
        assert len(data["data"]["validation_errors"]) >= 3

    def test_create_multiple_todos_unique_ids(self, client: TestClient):
        """여러 TODO 생성 시 고유 ID 할당 테스트"""
        todo_titles = ["TODO 1", "TODO 2", "TODO 3"]
        created_ids = []

        for title in todo_titles:
            todo_data = {"title": title}
            response = client.post("/todos/", json=todo_data)

            assert response.status_code == 201
            data = response.json()
            created_ids.append(data["data"]["id"])

        # 모든 ID가 고유한지 확인
        assert len(set(created_ids)) == len(created_ids)
        assert all(isinstance(todo_id, int) for todo_id in created_ids)
        assert all(todo_id > 0 for todo_id in created_ids)

    def test_create_todo_with_unicode_characters(self, client: TestClient):
        """유니코드 문자 포함 TODO 생성 테스트"""
        unicode_data = {
            "title": "🚀 이모지 TODO",
            "description": "한글과 English mixed 설명! @#$%^&*()",
            "priority": 3,
            "completed": False
        }

        response = client.post("/todos/", json=unicode_data)

        assert response.status_code == 201
        data = response.json()

        # 유니코드 문자가 정확히 저장되었는지 확인
        assert data["data"]["title"] == unicode_data["title"]
        assert data["data"]["description"] == unicode_data["description"]

    def test_create_todo_response_timestamp_consistency(self, client: TestClient, sample_todo_data):
        """TODO 생성 시 타임스탬프 일관성 테스트"""
        response = client.post("/todos/", json=sample_todo_data)

        assert response.status_code == 201
        data = response.json()

        created_at = data["data"]["created_at"]
        updated_at = data["data"]["updated_at"]

        # 생성 시간과 수정 시간이 유사해야 함 (초 단위)
        assert created_at is not None
        assert updated_at is not None
        # TODO: 실제 시간 비교 로직 추가 가능
