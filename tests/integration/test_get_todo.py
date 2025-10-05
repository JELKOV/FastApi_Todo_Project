"""
GET 단일 TODO API 테스트

TODO 단일 조회 API의 다양한 시나리오를 테스트합니다.
- 유효한 ID로 TODO 조회
- 존재하지 않는 ID로 TODO 조회 (404)
- 잘못된 ID 형식으로 TODO 조회 (422)
"""

import pytest
from fastapi.testclient import TestClient


class TestGetTodoAPI:
    """TODO 단일 조회 API 테스트 클래스"""

    def test_get_todo_by_valid_id(self, authenticated_client, sample_todo_data):
        """유효한 ID로 TODO 조회 테스트"""
        # TODO 생성
        create_response = authenticated_client.post("/todos/", json=sample_todo_data)
        assert create_response.status_code == 201
        created_todo = create_response.json()["data"]

        # 생성된 TODO 조회
        todo_id = created_todo["id"]
        response = authenticated_client.get(f"/todos/{todo_id}")

        assert response.status_code == 200
        data = response.json()

        # 응답 구조 검증
        assert "status" in data
        assert "msg" in data
        assert "data" in data
        assert "meta" in data

        # 데이터 내용 검증
        assert data["data"]["id"] == created_todo["id"]
        assert data["data"]["title"] == sample_todo_data["title"]
        assert data["data"]["description"] == sample_todo_data["description"]
        assert data["data"]["priority"] == sample_todo_data["priority"]
        assert data["data"]["completed"] == sample_todo_data["completed"]

    def test_get_todo_by_nonexistent_id(self, authenticated_client):
        """존재하지 않는 ID로 TODO 조회 테스트 (404)"""
        nonexistent_id = 99999
        response = authenticated_client.get(f"/todos/{nonexistent_id}")

        assert response.status_code == 404
        data = response.json()
        assert "data" in data

    def test_get_todo_by_invalid_id_format(self, authenticated_client):
        """잘못된 ID 형식으로 TODO 조회 테스트 (422)"""
        invalid_id = "not_a_number"
        response = authenticated_client.get(f"/todos/{invalid_id}")

        assert response.status_code == 422
        data = response.json()
        assert "validation_errors" in data["data"]

    def test_get_todo_negative_id(self, authenticated_client):
        """음수 ID로 TODO 조회 테스트 (404)"""
        negative_id = -1
        response = authenticated_client.get(f"/todos/{negative_id}")

        assert response.status_code == 404
        data = response.json()
        assert "data" in data

    def test_get_todo_zero_id(self, authenticated_client):
        """0 ID로 TODO 조회 테스트 (404)"""
        zero_id = 0
        response = authenticated_client.get(f"/todos/{zero_id}")

        assert response.status_code == 404
        data = response.json()
        assert "data" in data

    def test_get_multiple_todos_and_retrieve_specific(self, authenticated_client, sample_todo_list):
        """여러 TODO 생성 후 특정 TODO 조회 테스트"""
        created_todos = []

        # 여러 TODO 생성
        for todo_data in sample_todo_list:
            create_response = authenticated_client.post("/todos/", json=todo_data)
            assert create_response.status_code == 201
            created_todos.append(create_response.json()["data"])

        # 각 TODO를 개별적으로 조회
        for i, created_todo in enumerate(created_todos):
            todo_id = created_todo["id"]
            response = authenticated_client.get(f"/todos/{todo_id}")

            assert response.status_code == 200
            data = response.json()

            # 데이터 일치 검증
            assert data["data"]["id"] == created_todo["id"]
            assert data["data"]["title"] == sample_todo_list[i]["title"]
            assert data["data"]["description"] == sample_todo_list[i]["description"]
            assert data["data"]["priority"] == sample_todo_list[i]["priority"]
            assert data["data"]["completed"] == sample_todo_list[i]["completed"]

    def test_get_todo_response_consistency(self, authenticated_client, sample_todo_data):
        """TODO 조회 응답의 일관성 테스트"""
        # TODO 생성
        create_response = authenticated_client.post("/todos/", json=sample_todo_data)
        created_todo = create_response.json()["data"]

        # 여러 번 조회하여 응답 일관성 확인
        todo_id = created_todo["id"]
        responses = []
        for _ in range(3):
            response = authenticated_client.get(f"/todos/{todo_id}")
            assert response.status_code == 200
            responses.append(response.json())

        # 모든 응답이 동일한지 확인
        first_response = responses[0]
        for response in responses[1:]:
            assert response["data"] == first_response["data"]

    def test_get_todo_after_modification(self, authenticated_client, sample_todo_data):
        """TODO 수정 후 조회 테스트"""
        # TODO 생성
        create_response = authenticated_client.post("/todos/", json=sample_todo_data)
        created_todo = create_response.json()["data"]

        # TODO 수정 (토글)
        todo_id = created_todo["id"]
        toggle_response = authenticated_client.patch(f"/todos/{todo_id}/toggle")
        assert toggle_response.status_code == 200

        # 수정된 TODO 조회
        response = authenticated_client.get(f"/todos/{todo_id}")
        assert response.status_code == 200
        data = response.json()

        # completed 상태가 변경되었는지 확인
        assert data["data"]["completed"] != sample_todo_data["completed"]
        # updated_at이 존재하고 유효한 datetime인지 확인 (시간이 너무 빨라서 같을 수 있음)
        assert "updated_at" in data["data"]
        assert data["data"]["updated_at"] is not None
