"""
DELETE API 테스트

TODO 삭제 API의 다양한 시나리오를 테스트합니다.
- 존재하는 TODO 삭제 (204)
- 존재하지 않는 TODO 삭제 (404)
- 잘못된 ID 형식으로 삭제 (422)
- 삭제 후 재삭제 시도 (404)
- 여러 TODO 삭제 테스트
"""

import pytest
from fastapi.testclient import TestClient


class TestDeleteTodoAPI:
    """TODO 삭제 API 테스트 클래스"""

    def test_delete_existing_todo(self, authenticated_client, sample_todo_data):
        """존재하는 TODO 삭제 테스트 (204)"""
        # TODO 생성
        create_response = authenticated_client.post("/todos/", json=sample_todo_data)
        assert create_response.status_code == 201
        created_todo = create_response.json()["data"]

        # TODO 삭제
        todo_id = created_todo["id"]
        response = authenticated_client.delete(f"/todos/{todo_id}")

        assert response.status_code == 204

        # 삭제 후 조회 시 404 반환 확인
        get_response = authenticated_client.get(f"/todos/{todo_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_todo(self, authenticated_client):
        """존재하지 않는 TODO 삭제 테스트 (404)"""
        nonexistent_id = 99999
        response = authenticated_client.delete(f"/todos/{nonexistent_id}")

        assert response.status_code == 404
        data = response.json()
        assert "data" in data

    def test_delete_todo_with_invalid_id_format(self, authenticated_client):
        """잘못된 ID 형식으로 TODO 삭제 테스트 (422)"""
        invalid_id = "not_a_number"
        response = authenticated_client.delete(f"/todos/{invalid_id}")

        assert response.status_code == 422
        data = response.json()
        assert "validation_errors" in data["data"]

    def test_delete_todo_with_negative_id(self, authenticated_client):
        """음수 ID로 TODO 삭제 테스트 (404)"""
        negative_id = -1
        response = authenticated_client.delete(f"/todos/{negative_id}")

        assert response.status_code == 404
        data = response.json()
        assert "data" in data

    def test_delete_todo_with_zero_id(self, authenticated_client):
        """0 ID로 TODO 삭제 테스트 (404)"""
        zero_id = 0
        response = authenticated_client.delete(f"/todos/{zero_id}")

        assert response.status_code == 404
        data = response.json()
        assert "data" in data

    def test_delete_todo_and_verify_deletion(self, authenticated_client, sample_todo_data):
        """TODO 삭제 후 삭제 확인 테스트"""
        # TODO 생성
        create_response = authenticated_client.post("/todos/", json=sample_todo_data)
        created_todo = create_response.json()["data"]
        todo_id = created_todo["id"]

        # TODO 삭제
        delete_response = authenticated_client.delete(f"/todos/{todo_id}")
        assert delete_response.status_code == 204

        # 삭제 확인: 조회 시 404
        get_response = authenticated_client.get(f"/todos/{todo_id}")
        assert get_response.status_code == 404

        # 삭제 확인: 목록에서 제외
        list_response = authenticated_client.get("/todos/")
        assert list_response.status_code == 200
        list_data = list_response.json()
        deleted_ids = [todo["id"] for todo in list_data["data"]["todos"]]
        assert todo_id not in deleted_ids

    def test_delete_multiple_todos(self, authenticated_client):
        """여러 TODO 삭제 테스트"""
        # 여러 TODO 생성
        todo_list = [
            {"title": "TODO 1", "priority": 1},
            {"title": "TODO 2", "priority": 2},
            {"title": "TODO 3", "priority": 3}
        ]

        created_todos = []
        for todo_data in todo_list:
            create_response = authenticated_client.post("/todos/", json=todo_data)
            assert create_response.status_code == 201
            created_todos.append(create_response.json()["data"])

        # 각 TODO 삭제
        for created_todo in created_todos:
            todo_id = created_todo["id"]
            response = authenticated_client.delete(f"/todos/{todo_id}")
            assert response.status_code == 204

            # 삭제 확인
            get_response = authenticated_client.get(f"/todos/{todo_id}")
            assert get_response.status_code == 404

    def test_delete_todo_that_was_modified(self, authenticated_client, sample_todo_data):
        """수정된 TODO 삭제 테스트"""
        # TODO 생성
        create_response = authenticated_client.post("/todos/", json=sample_todo_data)
        created_todo = create_response.json()["data"]
        todo_id = created_todo["id"]

        # TODO 수정 (토글)
        toggle_response = authenticated_client.patch(f"/todos/{todo_id}/toggle")
        assert toggle_response.status_code == 200

        # 수정된 TODO 삭제
        delete_response = authenticated_client.delete(f"/todos/{todo_id}")
        assert delete_response.status_code == 204

        # 삭제 확인
        get_response = authenticated_client.get(f"/todos/{todo_id}")
        assert get_response.status_code == 404

    def test_delete_already_deleted_todo(self, authenticated_client, sample_todo_data):
        """이미 삭제된 TODO 재삭제 테스트 (404)"""
        # TODO 생성
        create_response = authenticated_client.post("/todos/", json=sample_todo_data)
        created_todo = create_response.json()["data"]
        todo_id = created_todo["id"]

        # 첫 번째 삭제
        first_delete = authenticated_client.delete(f"/todos/{todo_id}")
        assert first_delete.status_code == 204

        # 두 번째 삭제 (이미 삭제된 TODO)
        second_delete = authenticated_client.delete(f"/todos/{todo_id}")
        assert second_delete.status_code == 404

    def test_delete_todo_preserves_other_todos(self, authenticated_client):
        """특정 TODO 삭제 시 다른 TODO들이 보존되는지 테스트"""
        # 여러 TODO 생성
        todo_list = [
            {"title": "보존될 TODO 1", "priority": 1},
            {"title": "삭제될 TODO", "priority": 2},
            {"title": "보존될 TODO 2", "priority": 3}
        ]

        created_todos = []
        for todo_data in todo_list:
            create_response = authenticated_client.post("/todos/", json=todo_data)
            assert create_response.status_code == 201
            created_todos.append(create_response.json()["data"])

        # 중간 TODO 삭제
        todo_to_delete = created_todos[1]
        delete_response = authenticated_client.delete(f"/todos/{todo_to_delete['id']}")
        assert delete_response.status_code == 204

        # 다른 TODO들이 보존되었는지 확인
        for i, preserved_todo in enumerate([created_todos[0], created_todos[2]]):
            get_response = authenticated_client.get(f"/todos/{preserved_todo['id']}")
            assert get_response.status_code == 200
            data = get_response.json()
            assert data["data"]["title"] == todo_list[i * 2]["title"]  # 0, 2 인덱스

    def test_delete_todo_with_special_characters_in_title(self, authenticated_client):
        """특수 문자가 포함된 제목의 TODO 삭제 테스트"""
        # 특수 문자 포함 TODO 생성
        special_todo_data = {
            "title": "🚀 특수문자 TODO! @#$%^&*()",
            "description": "한글과 English mixed 설명",
            "priority": 4,
            "completed": False
        }

        create_response = authenticated_client.post("/todos/", json=special_todo_data)
        assert create_response.status_code == 201
        created_todo = create_response.json()["data"]

        # TODO 삭제
        todo_id = created_todo["id"]
        response = authenticated_client.delete(f"/todos/{todo_id}")

        assert response.status_code == 204

        # 삭제 확인
        get_response = authenticated_client.get(f"/todos/{todo_id}")
        assert get_response.status_code == 404

    def test_delete_todo_response_consistency(self, authenticated_client, sample_todo_data):
        """TODO 삭제 응답의 일관성 테스트"""
        # TODO 생성
        create_response = authenticated_client.post("/todos/", json=sample_todo_data)
        created_todo = create_response.json()["data"]
        todo_id = created_todo["id"]

        # TODO 삭제
        response = authenticated_client.delete(f"/todos/{todo_id}")

        # 삭제 응답은 항상 204 No Content여야 함
        assert response.status_code == 204

        # 응답 본문이 비어있는지 확인 (204 응답)
        assert response.content == b""

    def test_delete_todo_after_complete_workflow(self, authenticated_client, sample_todo_data):
        """완전한 워크플로우 후 TODO 삭제 테스트"""
        # TODO 생성
        create_response = authenticated_client.post("/todos/", json=sample_todo_data)
        created_todo = create_response.json()["data"]
        todo_id = created_todo["id"]

        # TODO 조회
        get_response = authenticated_client.get(f"/todos/{todo_id}")
        assert get_response.status_code == 200

        # TODO 수정 (토글)
        toggle_response = authenticated_client.patch(f"/todos/{todo_id}/toggle")
        assert toggle_response.status_code == 200

        # TODO 삭제
        delete_response = authenticated_client.delete(f"/todos/{todo_id}")
        assert delete_response.status_code == 204

        # 삭제 확인
        final_get_response = authenticated_client.get(f"/todos/{todo_id}")
        assert final_get_response.status_code == 404
