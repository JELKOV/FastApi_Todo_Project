"""
GET 단일 조회 API 테스트

특정 TODO 항목을 조회하는 API의 다양한 시나리오를 테스트합니다.
- 유효한 ID로 조회
- 존재하지 않는 ID로 조회 (404)
- 잘못된 ID 형식으로 조회 (422)
"""

import pytest
from fastapi.testclient import TestClient


class TestGetTodoAPI:
    """TODO 단일 조회 API 테스트 클래스"""

    def test_get_todo_by_valid_id(self, client: TestClient, sample_todo_data):
        """유효한 ID로 TODO 조회 테스트"""
        # TODO 생성
        create_response = client.post("/todos/", json=sample_todo_data)
        assert create_response.status_code == 201
        created_todo = create_response.json()["data"]
        todo_id = created_todo["id"]

        # TODO 조회
        response = client.get(f"/todos/{todo_id}")

        assert response.status_code == 200
        data = response.json()

        # 응답 구조 검증
        assert "status" in data
        assert "msg" in data
        assert "data" in data
        assert "meta" in data

        # 데이터 내용 검증
        assert data["status"] == 200
        assert data["msg"] == "Todo retrieved successfully"
        assert data["data"]["id"] == todo_id
        assert data["data"]["title"] == sample_todo_data["title"]
        assert data["data"]["description"] == sample_todo_data["description"]
        assert data["data"]["priority"] == sample_todo_data["priority"]
        assert data["data"]["completed"] == sample_todo_data["completed"]
        assert "created_at" in data["data"]
        assert "updated_at" in data["data"]

    def test_get_todo_by_nonexistent_id(self, client: TestClient):
        """존재하지 않는 ID로 TODO 조회 테스트 (404)"""
        nonexistent_id = 99999

        response = client.get(f"/todos/{nonexistent_id}")

        assert response.status_code == 404
        data = response.json()

        # 에러 응답 구조 검증
        assert "status" in data
        assert "msg" in data
        assert "data" in data
        assert "meta" in data
        assert "error_code" in data

        # 에러 내용 검증
        assert data["status"] == 404
        assert data["error_code"] == "E404T001"
        assert "not found" in data["msg"].lower()
        assert data["data"]["todo_id"] == nonexistent_id

    def test_get_todo_by_invalid_id_format(self, client: TestClient):
        """잘못된 ID 형식으로 TODO 조회 테스트 (422)"""
        invalid_ids = ["abc", "invalid", "1.5"]

        for invalid_id in invalid_ids:
            response = client.get(f"/todos/{invalid_id}")
            assert response.status_code == 422  # 잘못된 형식은 422

            data = response.json()
            assert "validation_errors" in data["data"]

    def test_get_todo_negative_id(self, client: TestClient):
        """음수 ID로 TODO 조회 테스트 (404)"""
        negative_id = -1

        response = client.get(f"/todos/{negative_id}")

        assert response.status_code == 404  # 음수 ID는 404로 처리
        data = response.json()

        # 음수 ID는 404 error
        assert data["status"] == 404

    def test_get_todo_zero_id(self, client: TestClient):
        """0 ID로 TODO 조회 테스트 (404)"""
        zero_id = 0

        response = client.get(f"/todos/{zero_id}")

        assert response.status_code == 404  # 0 ID는 404로 처리
        data = response.json()

        # 0 ID는 404 error
        assert data["status"] == 404

    def test_get_multiple_todos_and_retrieve_specific(self, client: TestClient, sample_todo_list):
        """여러 TODO 생성 후 특정 TODO 조회 테스트"""
        created_todos = []

        # 여러 TODO 생성
        for todo_data in sample_todo_list:
            create_response = client.post("/todos/", json=todo_data)
            assert create_response.status_code == 201
            created_todos.append(create_response.json()["data"])

        # 각 TODO를 개별적으로 조회
        for created_todo in created_todos:
            todo_id = created_todo["id"]
            response = client.get(f"/todos/{todo_id}")

            assert response.status_code == 200
            data = response.json()

            # 조회된 TODO가 생성된 TODO와 일치하는지 확인
            assert data["data"]["id"] == created_todo["id"]
            assert data["data"]["title"] == created_todo["title"]
            assert data["data"]["description"] == created_todo["description"]
            assert data["data"]["priority"] == created_todo["priority"]
            assert data["data"]["completed"] == created_todo["completed"]

    def test_get_todo_response_consistency(self, client: TestClient, sample_todo_data):
        """TODO 조회 응답의 일관성 테스트"""
        # TODO 생성
        create_response = client.post("/todos/", json=sample_todo_data)
        created_todo = create_response.json()["data"]
        todo_id = created_todo["id"]

        # 여러 번 조회하여 응답이 일관되는지 확인
        for _ in range(3):
            response = client.get(f"/todos/{todo_id}")
            assert response.status_code == 200

            data = response.json()

            # 매번 동일한 응답 구조와 내용을 반환하는지 확인
            assert data["data"]["id"] == todo_id
            assert data["data"]["title"] == sample_todo_data["title"]
            assert data["data"]["description"] == sample_todo_data["description"]
            assert data["data"]["priority"] == sample_todo_data["priority"]
            assert data["data"]["completed"] == sample_todo_data["completed"]

    def test_get_todo_after_modification(self, client: TestClient, sample_todo_data):
        """TODO 수정 후 조회 테스트"""
        # TODO 생성
        create_response = client.post("/todos/", json=sample_todo_data)
        created_todo = create_response.json()["data"]
        todo_id = created_todo["id"]

        # TODO 수정
        update_data = {
            "title": "수정된 제목",
            "priority": 5,
            "completed": True
        }
        update_response = client.put(f"/todos/{todo_id}", json=update_data)
        assert update_response.status_code == 200

        # 수정된 TODO 조회
        response = client.get(f"/todos/{todo_id}")
        assert response.status_code == 200

        data = response.json()

        # 수정된 내용이 반영되었는지 확인
        assert data["data"]["title"] == "수정된 제목"
        assert data["data"]["priority"] == 5
        assert data["data"]["completed"] == True
        # description은 수정하지 않았으므로 원래 값 유지
        assert data["data"]["description"] == sample_todo_data["description"]
