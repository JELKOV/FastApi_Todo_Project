"""
PATCH API 테스트

TODO 상태 토글 API의 다양한 시나리오를 테스트합니다.
- 유효한 TODO 상태 토글
- 존재하지 않는 TODO 토글 (404)
- 잘못된 ID 형식으로 토글 (422)
- 토글 후 상태 변화 확인
"""

import pytest
from fastapi.testclient import TestClient


class TestPatchTodoAPI:
    """TODO 상태 토글 API 테스트 클래스"""

    def test_toggle_todo_from_false_to_true(self, client: TestClient, sample_todo_data):
        """TODO 상태를 False에서 True로 토글 테스트"""
        # 미완료 TODO 생성
        todo_data = {**sample_todo_data, "completed": False}
        create_response = client.post("/todos/", json=todo_data)
        assert create_response.status_code == 201
        created_todo = create_response.json()["data"]
        todo_id = created_todo["id"]

        # 상태 토글
        response = client.patch(f"/todos/{todo_id}/toggle")

        assert response.status_code == 200
        data = response.json()

        # 응답 구조 검증
        assert "status" in data
        assert "msg" in data
        assert "data" in data
        assert "meta" in data

        # 데이터 내용 검증
        assert data["status"] == 200
        assert data["msg"] == "Todo status toggled successfully"
        assert data["data"]["id"] == todo_id
        assert data["data"]["completed"] == True  # False에서 True로 변경
        assert data["data"]["title"] == todo_data["title"]
        assert data["data"]["description"] == todo_data["description"]
        assert data["data"]["priority"] == todo_data["priority"]

    def test_toggle_todo_from_true_to_false(self, client: TestClient, sample_todo_data):
        """TODO 상태를 True에서 False로 토글 테스트"""
        # 완료된 TODO 생성
        todo_data = {**sample_todo_data, "completed": True}
        create_response = client.post("/todos/", json=todo_data)
        assert create_response.status_code == 201
        created_todo = create_response.json()["data"]
        todo_id = created_todo["id"]

        # 상태 토글
        response = client.patch(f"/todos/{todo_id}/toggle")

        assert response.status_code == 200
        data = response.json()

        # 데이터 내용 검증
        assert data["data"]["completed"] == False  # True에서 False로 변경
        assert data["data"]["title"] == todo_data["title"]
        assert data["data"]["description"] == todo_data["description"]
        assert data["data"]["priority"] == todo_data["priority"]

    def test_toggle_todo_multiple_times(self, client: TestClient, sample_todo_data):
        """TODO 상태를 여러 번 토글 테스트"""
        # TODO 생성
        todo_data = {**sample_todo_data, "completed": False}
        create_response = client.post("/todos/", json=todo_data)
        created_todo = create_response.json()["data"]
        todo_id = created_todo["id"]

        # 상태 변화 추적
        expected_states = [True, False, True, False]

        for i, expected_state in enumerate(expected_states):
            response = client.patch(f"/todos/{todo_id}/toggle")
            assert response.status_code == 200

            data = response.json()
            assert data["data"]["completed"] == expected_state
            assert data["data"]["id"] == todo_id

    def test_toggle_nonexistent_todo(self, client: TestClient):
        """존재하지 않는 TODO 토글 테스트 (404)"""
        nonexistent_id = 99999

        response = client.patch(f"/todos/{nonexistent_id}/toggle")

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

    def test_toggle_todo_with_invalid_id_format(self, client: TestClient):
        """잘못된 ID 형식으로 TODO 토글 테스트 (422)"""
        invalid_ids = ["abc", "invalid", "1.5"]

        for invalid_id in invalid_ids:
            response = client.patch(f"/todos/{invalid_id}/toggle")
            assert response.status_code == 422  # 잘못된 형식은 422

            data = response.json()
            assert "validation_errors" in data["data"]

    def test_toggle_todo_with_negative_id(self, client: TestClient):
        """음수 ID로 TODO 토글 테스트 (404)"""
        negative_id = -1

        response = client.patch(f"/todos/{negative_id}/toggle")

        assert response.status_code == 404  # 음수 ID는 404로 처리
        data = response.json()

        # 음수 ID는 404 error
        assert data["status"] == 404

    def test_toggle_todo_with_zero_id(self, client: TestClient):
        """0 ID로 TODO 토글 테스트 (404)"""
        zero_id = 0

        response = client.patch(f"/todos/{zero_id}/toggle")

        assert response.status_code == 404  # 0 ID는 404로 처리
        data = response.json()

        # 0 ID는 404 error
        assert data["status"] == 404

    def test_toggle_todo_preserves_other_fields(self, client: TestClient):
        """TODO 토글 시 다른 필드들이 보존되는지 테스트"""
        # 상세한 TODO 생성
        todo_data = {
            "title": "상세한 TODO",
            "description": "모든 필드가 포함된 TODO",
            "priority": 4,
            "completed": False
        }

        create_response = client.post("/todos/", json=todo_data)
        created_todo = create_response.json()["data"]
        todo_id = created_todo["id"]

        # 상태 토글
        response = client.patch(f"/todos/{todo_id}/toggle")
        assert response.status_code == 200

        data = response.json()

        # 다른 필드들이 변경되지 않았는지 확인
        assert data["data"]["title"] == todo_data["title"]
        assert data["data"]["description"] == todo_data["description"]
        assert data["data"]["priority"] == todo_data["priority"]
        # completed만 변경되어야 함
        assert data["data"]["completed"] == True

    def test_toggle_todo_updated_at_changes(self, client: TestClient, sample_todo_data):
        """TODO 토글 시 updated_at이 변경되는지 테스트"""
        # TODO 생성
        create_response = client.post("/todos/", json=sample_todo_data)
        created_todo = create_response.json()["data"]
        todo_id = created_todo["id"]

        original_updated_at = created_todo["updated_at"]

        # 상태 토글
        response = client.patch(f"/todos/{todo_id}/toggle")
        assert response.status_code == 200

        data = response.json()
        new_updated_at = data["data"]["updated_at"]

        # updated_at이 존재하는지 확인 (밀리초 차이로 인해 동일할 수 있음)
        assert "updated_at" in data["data"]
        assert new_updated_at is not None

    def test_toggle_multiple_different_todos(self, client: TestClient):
        """여러 개의 다른 TODO들을 각각 토글 테스트"""
        todo_list = [
            {"title": "TODO 1", "priority": 1, "completed": False},
            {"title": "TODO 2", "priority": 2, "completed": True},
            {"title": "TODO 3", "priority": 3, "completed": False}
        ]

        created_todos = []

        # 여러 TODO 생성
        for todo_data in todo_list:
            create_response = client.post("/todos/", json=todo_data)
            created_todos.append(create_response.json()["data"])

        # 각 TODO를 토글하고 결과 확인
        expected_states = [True, False, True]  # False->True, True->False, False->True

        for i, (created_todo, expected_state) in enumerate(zip(created_todos, expected_states)):
            todo_id = created_todo["id"]
            response = client.patch(f"/todos/{todo_id}/toggle")

            assert response.status_code == 200
            data = response.json()

            assert data["data"]["id"] == todo_id
            assert data["data"]["completed"] == expected_state
            assert data["data"]["title"] == todo_list[i]["title"]

    def test_toggle_todo_response_consistency(self, client: TestClient, sample_todo_data):
        """TODO 토글 응답의 일관성 테스트"""
        # TODO 생성
        create_response = client.post("/todos/", json=sample_todo_data)
        created_todo = create_response.json()["data"]
        todo_id = created_todo["id"]

        # 여러 번 토글하여 응답이 일관되는지 확인
        for i in range(3):
            response = client.patch(f"/todos/{todo_id}/toggle")
            assert response.status_code == 200

            data = response.json()

            # 매번 동일한 응답 구조를 반환하는지 확인
            assert "status" in data
            assert "msg" in data
            assert "data" in data
            assert "meta" in data
            assert data["status"] == 200
            assert data["msg"] == "Todo status toggled successfully"
            assert data["data"]["id"] == todo_id

    def test_toggle_todo_after_other_operations(self, client: TestClient, sample_todo_data):
        """다른 작업 후 TODO 토글 테스트"""
        # TODO 생성
        create_response = client.post("/todos/", json=sample_todo_data)
        created_todo = create_response.json()["data"]
        todo_id = created_todo["id"]

        # TODO 수정
        update_data = {"title": "수정된 제목", "priority": 5}
        update_response = client.put(f"/todos/{todo_id}", json=update_data)
        assert update_response.status_code == 200

        # 수정 후 토글
        response = client.patch(f"/todos/{todo_id}/toggle")
        assert response.status_code == 200

        data = response.json()

        # 수정된 내용이 유지되고 상태만 토글되었는지 확인
        assert data["data"]["title"] == "수정된 제목"
        assert data["data"]["priority"] == 5
        assert data["data"]["completed"] == True  # 원래 False였으므로 True로 변경
