"""
PATCH API 테스트

TODO 상태 토글 API의 다양한 시나리오를 테스트합니다.
- 완료 상태 토글 (False → True, True → False)
- 존재하지 않는 TODO 토글 (404)
- 잘못된 ID 형식으로 토글 (422)
- 여러 번 토글 테스트
- 다른 필드 보존 확인
"""

import pytest
from fastapi.testclient import TestClient


class TestPatchTodoAPI:
    """TODO 토글 API 테스트 클래스"""

    def test_toggle_todo_from_false_to_true(self, authenticated_client, sample_todo_data):
        """TODO 상태를 False에서 True로 토글 테스트"""
        # 미완료 TODO 생성
        todo_data = {**sample_todo_data, "completed": False}
        create_response = authenticated_client.post("/todos/", json=todo_data)
        assert create_response.status_code == 201
        created_todo = create_response.json()["data"]

        # TODO 토글
        todo_id = created_todo["id"]
        response = authenticated_client.patch(f"/todos/{todo_id}/toggle")

        assert response.status_code == 200
        data = response.json()

        # 응답 구조 검증
        assert "status" in data
        assert "msg" in data
        assert "data" in data
        assert "meta" in data

        # 상태 변경 확인
        assert data["data"]["completed"] is True
        assert data["data"]["id"] == todo_id

        # 다른 필드들이 보존되었는지 확인
        assert data["data"]["title"] == todo_data["title"]
        assert data["data"]["description"] == todo_data["description"]
        assert data["data"]["priority"] == todo_data["priority"]

    def test_toggle_todo_from_true_to_false(self, authenticated_client, sample_todo_data):
        """TODO 상태를 True에서 False로 토글 테스트"""
        # 완료된 TODO 생성
        todo_data = {**sample_todo_data, "completed": True}
        create_response = authenticated_client.post("/todos/", json=todo_data)
        assert create_response.status_code == 201
        created_todo = create_response.json()["data"]

        # TODO 토글
        todo_id = created_todo["id"]
        response = authenticated_client.patch(f"/todos/{todo_id}/toggle")

        assert response.status_code == 200
        data = response.json()

        # 상태 변경 확인
        assert data["data"]["completed"] is False
        assert data["data"]["id"] == todo_id

        # 다른 필드들이 보존되었는지 확인
        assert data["data"]["title"] == todo_data["title"]
        assert data["data"]["description"] == todo_data["description"]
        assert data["data"]["priority"] == todo_data["priority"]

    def test_toggle_todo_multiple_times(self, authenticated_client, sample_todo_data):
        """TODO 상태를 여러 번 토글 테스트"""
        # TODO 생성
        todo_data = {**sample_todo_data, "completed": False}
        create_response = authenticated_client.post("/todos/", json=todo_data)
        created_todo = create_response.json()["data"]

        todo_id = created_todo["id"]
        current_state = False

        # 여러 번 토글하여 상태가 올바르게 변경되는지 확인
        for i in range(5):
            response = authenticated_client.patch(f"/todos/{todo_id}/toggle")
            assert response.status_code == 200
            data = response.json()

            # 상태가 반대로 변경되었는지 확인
            expected_state = not current_state
            assert data["data"]["completed"] == expected_state
            current_state = expected_state

    def test_toggle_nonexistent_todo(self, authenticated_client):
        """존재하지 않는 TODO 토글 테스트 (404)"""
        nonexistent_id = 99999
        response = authenticated_client.patch(f"/todos/{nonexistent_id}/toggle")

        assert response.status_code == 404
        data = response.json()
        assert "data" in data

    def test_toggle_todo_with_invalid_id_format(self, authenticated_client):
        """잘못된 ID 형식으로 TODO 토글 테스트 (422)"""
        invalid_id = "not_a_number"
        response = authenticated_client.patch(f"/todos/{invalid_id}/toggle")

        assert response.status_code == 422
        data = response.json()
        assert "validation_errors" in data["data"]

    def test_toggle_todo_with_negative_id(self, authenticated_client):
        """음수 ID로 TODO 토글 테스트 (404)"""
        negative_id = -1
        response = authenticated_client.patch(f"/todos/{negative_id}/toggle")

        assert response.status_code == 404
        data = response.json()
        assert "data" in data

    def test_toggle_todo_with_zero_id(self, authenticated_client):
        """0 ID로 TODO 토글 테스트 (404)"""
        zero_id = 0
        response = authenticated_client.patch(f"/todos/{zero_id}/toggle")

        assert response.status_code == 404
        data = response.json()
        assert "data" in data

    def test_toggle_todo_preserves_other_fields(self, authenticated_client):
        """TODO 토글 시 다른 필드들이 보존되는지 테스트"""
        # 상세한 TODO 생성
        todo_data = {
            "title": "상세한 TODO",
            "description": "모든 필드가 포함된 TODO",
            "priority": 4,
            "completed": False
        }

        create_response = authenticated_client.post("/todos/", json=todo_data)
        created_todo = create_response.json()["data"]

        # TODO 토글
        todo_id = created_todo["id"]
        response = authenticated_client.patch(f"/todos/{todo_id}/toggle")

        assert response.status_code == 200
        data = response.json()

        # completed만 변경되고 다른 필드들은 보존되었는지 확인
        assert data["data"]["completed"] != todo_data["completed"]
        assert data["data"]["title"] == todo_data["title"]
        assert data["data"]["description"] == todo_data["description"]
        assert data["data"]["priority"] == todo_data["priority"]

    def test_toggle_todo_updated_at_changes(self, authenticated_client, sample_todo_data):
        """TODO 토글 시 updated_at이 변경되는지 테스트"""
        # TODO 생성
        create_response = authenticated_client.post("/todos/", json=sample_todo_data)
        created_todo = create_response.json()["data"]

        # 토글 전 updated_at 저장
        original_updated_at = created_todo["updated_at"]

        # TODO 토글
        todo_id = created_todo["id"]
        response = authenticated_client.patch(f"/todos/{todo_id}/toggle")

        assert response.status_code == 200
        data = response.json()

        # updated_at이 존재하고 유효한 datetime인지 확인
        assert "updated_at" in data["data"]
        new_updated_at = data["data"]["updated_at"]
        assert new_updated_at is not None

    def test_toggle_multiple_different_todos(self, authenticated_client):
        """여러 개의 다른 TODO들을 각각 토글 테스트"""
        todo_list = [
            {"title": "TODO 1", "priority": 1, "completed": False},
            {"title": "TODO 2", "priority": 2, "completed": True},
            {"title": "TODO 3", "priority": 3, "completed": False}
        ]

        created_todos = []

        # 여러 TODO 생성
        for todo_data in todo_list:
            create_response = authenticated_client.post("/todos/", json=todo_data)
            created_todos.append(create_response.json()["data"])

        # 각 TODO를 토글
        for i, created_todo in enumerate(created_todos):
            todo_id = created_todo["id"]
            response = authenticated_client.patch(f"/todos/{todo_id}/toggle")

            assert response.status_code == 200
            data = response.json()

            # 상태가 반대로 변경되었는지 확인
            original_state = todo_list[i]["completed"]
            assert data["data"]["completed"] == (not original_state)

    def test_toggle_todo_response_consistency(self, authenticated_client, sample_todo_data):
        """TODO 토글 응답의 일관성 테스트"""
        # TODO 생성
        create_response = authenticated_client.post("/todos/", json=sample_todo_data)
        created_todo = create_response.json()["data"]

        # 같은 TODO를 여러 번 토글하여 응답 일관성 확인
        todo_id = created_todo["id"]
        responses = []

        for _ in range(3):
            response = authenticated_client.patch(f"/todos/{todo_id}/toggle")
            assert response.status_code == 200
            responses.append(response.json())

        # 모든 응답의 구조가 일관되는지 확인
        first_response = responses[0]
        for response in responses[1:]:
            assert "status" in response
            assert "msg" in response
            assert "data" in response
            assert "meta" in response
            assert response["data"]["id"] == first_response["data"]["id"]

    def test_toggle_todo_after_other_operations(self, authenticated_client, sample_todo_data):
        """다른 작업 후 TODO 토글 테스트"""
        # TODO 생성
        create_response = authenticated_client.post("/todos/", json=sample_todo_data)
        created_todo = create_response.json()["data"]

        # TODO 조회
        todo_id = created_todo["id"]
        get_response = authenticated_client.get(f"/todos/{todo_id}")
        assert get_response.status_code == 200

        # TODO 토글
        response = authenticated_client.patch(f"/todos/{todo_id}/toggle")

        assert response.status_code == 200
        data = response.json()

        # 상태가 변경되었는지 확인
        assert data["data"]["completed"] != sample_todo_data["completed"]
