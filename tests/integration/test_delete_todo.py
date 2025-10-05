"""
DELETE API 테스트

TODO 삭제 API의 다양한 시나리오를 테스트합니다.
- 유효한 TODO 삭제 (204)
- 존재하지 않는 TODO 삭제 (404)
- 잘못된 ID 형식으로 삭제 (422)
- 삭제 후 조회 불가 확인
"""

import pytest
from fastapi.testclient import TestClient


class TestDeleteTodoAPI:
    """TODO 삭제 API 테스트 클래스"""

    def test_delete_existing_todo(self, client: TestClient, sample_todo_data):
        """존재하는 TODO 삭제 테스트 (204)"""
        # TODO 생성
        create_response = client.post("/todos/", json=sample_todo_data)
        assert create_response.status_code == 201
        created_todo = create_response.json()["data"]
        todo_id = created_todo["id"]

        # TODO 삭제
        response = client.delete(f"/todos/{todo_id}")

        # 204 No Content 응답 확인
        assert response.status_code == 204
        # 204 응답은 본문이 없어야 함
        assert response.content == b""

    def test_delete_nonexistent_todo(self, client: TestClient):
        """존재하지 않는 TODO 삭제 테스트 (404)"""
        nonexistent_id = 99999

        response = client.delete(f"/todos/{nonexistent_id}")

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

    def test_delete_todo_with_invalid_id_format(self, client: TestClient):
        """잘못된 ID 형식으로 TODO 삭제 테스트 (422)"""
        invalid_ids = ["abc", "invalid", "1.5"]

        for invalid_id in invalid_ids:
            response = client.delete(f"/todos/{invalid_id}")
            assert response.status_code == 422  # 잘못된 형식은 422

            data = response.json()
            assert "validation_errors" in data["data"]

    def test_delete_todo_with_negative_id(self, client: TestClient):
        """음수 ID로 TODO 삭제 테스트 (404)"""
        negative_id = -1

        response = client.delete(f"/todos/{negative_id}")

        assert response.status_code == 404  # 음수 ID는 404로 처리
        data = response.json()

        # 음수 ID는 404 error
        assert data["status"] == 404

    def test_delete_todo_with_zero_id(self, client: TestClient):
        """0 ID로 TODO 삭제 테스트 (404)"""
        zero_id = 0

        response = client.delete(f"/todos/{zero_id}")

        assert response.status_code == 404  # 0 ID는 404로 처리
        data = response.json()

        # 0 ID는 404 error
        assert data["status"] == 404

    def test_delete_todo_and_verify_deletion(self, client: TestClient, sample_todo_data):
        """TODO 삭제 후 삭제 확인 테스트"""
        # TODO 생성
        create_response = client.post("/todos/", json=sample_todo_data)
        created_todo = create_response.json()["data"]
        todo_id = created_todo["id"]

        # TODO 조회 (삭제 전)
        get_response = client.get(f"/todos/{todo_id}")
        assert get_response.status_code == 200

        # TODO 삭제
        delete_response = client.delete(f"/todos/{todo_id}")
        assert delete_response.status_code == 204

        # TODO 조회 (삭제 후)
        get_response_after = client.get(f"/todos/{todo_id}")
        assert get_response_after.status_code == 404

        # 삭제된 TODO는 목록에서도 제거되었는지 확인
        list_response = client.get("/todos/")
        assert list_response.status_code == 200
        list_data = list_response.json()

        # 삭제된 TODO ID가 목록에 없는지 확인
        todo_ids = [todo["id"] for todo in list_data["data"]["todos"]]
        assert todo_id not in todo_ids

    def test_delete_multiple_todos(self, client: TestClient):
        """여러 TODO 삭제 테스트"""
        # 여러 TODO 생성
        todo_list = [
            {"title": "TODO 1", "priority": 1},
            {"title": "TODO 2", "priority": 2},
            {"title": "TODO 3", "priority": 3}
        ]

        created_todos = []
        for todo_data in todo_list:
            create_response = client.post("/todos/", json=todo_data)
            created_todos.append(create_response.json()["data"])

        # 각 TODO 삭제
        for created_todo in created_todos:
            todo_id = created_todo["id"]
            delete_response = client.delete(f"/todos/{todo_id}")
            assert delete_response.status_code == 204

        # 모든 TODO가 삭제되었는지 확인
        list_response = client.get("/todos/")
        assert list_response.status_code == 200
        list_data = list_response.json()

        assert list_data["data"]["total"] == 0
        assert len(list_data["data"]["todos"]) == 0

    def test_delete_todo_that_was_modified(self, client: TestClient, sample_todo_data):
        """수정된 TODO 삭제 테스트"""
        # TODO 생성
        create_response = client.post("/todos/", json=sample_todo_data)
        created_todo = create_response.json()["data"]
        todo_id = created_todo["id"]

        # TODO 수정
        update_data = {"title": "수정된 제목", "priority": 5, "completed": True}
        update_response = client.put(f"/todos/{todo_id}", json=update_data)
        assert update_response.status_code == 200

        # TODO 토글
        toggle_response = client.patch(f"/todos/{todo_id}/toggle")
        assert toggle_response.status_code == 200

        # 수정 및 토글된 TODO 삭제
        delete_response = client.delete(f"/todos/{todo_id}")
        assert delete_response.status_code == 204

        # 삭제 확인
        get_response = client.get(f"/todos/{todo_id}")
        assert get_response.status_code == 404

    def test_delete_already_deleted_todo(self, client: TestClient, sample_todo_data):
        """이미 삭제된 TODO 재삭제 테스트 (404)"""
        # TODO 생성
        create_response = client.post("/todos/", json=sample_todo_data)
        created_todo = create_response.json()["data"]
        todo_id = created_todo["id"]

        # 첫 번째 삭제
        delete_response = client.delete(f"/todos/{todo_id}")
        assert delete_response.status_code == 204

        # 두 번째 삭제 (이미 삭제된 TODO)
        delete_response_2 = client.delete(f"/todos/{todo_id}")
        assert delete_response_2.status_code == 404

        # 에러 응답 확인
        data = delete_response_2.json()
        assert data["status"] == 404
        assert data["error_code"] == "E404T001"

    def test_delete_todo_preserves_other_todos(self, client: TestClient):
        """특정 TODO 삭제 시 다른 TODO들이 보존되는지 테스트"""
        # 여러 TODO 생성
        todo_list = [
            {"title": "보존될 TODO 1", "priority": 1},
            {"title": "삭제될 TODO", "priority": 2},
            {"title": "보존될 TODO 2", "priority": 3}
        ]

        created_todos = []
        for todo_data in todo_list:
            create_response = client.post("/todos/", json=todo_data)
            created_todos.append(create_response.json()["data"])

        # 가운데 TODO 삭제
        todo_to_delete = created_todos[1]  # "삭제될 TODO"
        delete_response = client.delete(f"/todos/{todo_to_delete['id']}")
        assert delete_response.status_code == 204

        # 남은 TODO들 확인
        list_response = client.get("/todos/")
        assert list_response.status_code == 200
        list_data = list_response.json()

        # 2개의 TODO가 남아있어야 함
        assert list_data["data"]["total"] == 2
        assert len(list_data["data"]["todos"]) == 2

        # 삭제되지 않은 TODO들이 남아있는지 확인
        remaining_ids = [todo["id"] for todo in list_data["data"]["todos"]]
        assert created_todos[0]["id"] in remaining_ids
        assert created_todos[2]["id"] in remaining_ids
        assert todo_to_delete["id"] not in remaining_ids

    def test_delete_todo_with_special_characters_in_title(self, client: TestClient):
        """특수 문자가 포함된 제목의 TODO 삭제 테스트"""
        # 특수 문자 포함 TODO 생성
        special_todo_data = {
            "title": "🚀 특수문자 TODO! @#$%^&*()",
            "description": "한글과 English mixed 설명",
            "priority": 4,
            "completed": False
        }

        create_response = client.post("/todos/", json=special_todo_data)
        assert create_response.status_code == 201
        created_todo = create_response.json()["data"]
        todo_id = created_todo["id"]

        # TODO 삭제
        delete_response = client.delete(f"/todos/{todo_id}")
        assert delete_response.status_code == 204

        # 삭제 확인
        get_response = client.get(f"/todos/{todo_id}")
        assert get_response.status_code == 404

    def test_delete_todo_response_consistency(self, client: TestClient, sample_todo_data):
        """TODO 삭제 응답의 일관성 테스트"""
        # TODO 생성
        create_response = client.post("/todos/", json=sample_todo_data)
        created_todo = create_response.json()["data"]
        todo_id = created_todo["id"]

        # TODO 삭제
        response = client.delete(f"/todos/{todo_id}")

        # 응답이 일관되는지 확인
        assert response.status_code == 204
        assert response.content == b""
        # 204 응답은 헤더만 있고 본문은 없음

    def test_delete_todo_after_complete_workflow(self, client: TestClient, sample_todo_data):
        """완전한 워크플로우 후 TODO 삭제 테스트"""
        # TODO 생성
        create_response = client.post("/todos/", json=sample_todo_data)
        created_todo = create_response.json()["data"]
        todo_id = created_todo["id"]

        # TODO 수정
        update_data = {"title": "워크플로우 TODO", "priority": 5}
        update_response = client.put(f"/todos/{todo_id}", json=update_data)
        assert update_response.status_code == 200

        # TODO 토글 (완료)
        toggle_response = client.patch(f"/todos/{todo_id}/toggle")
        assert toggle_response.status_code == 200

        # TODO 조회 (완료 상태 확인)
        get_response = client.get(f"/todos/{todo_id}")
        assert get_response.status_code == 200
        assert get_response.json()["data"]["completed"] == True

        # TODO 삭제
        delete_response = client.delete(f"/todos/{todo_id}")
        assert delete_response.status_code == 204

        # 최종 확인 - TODO가 완전히 삭제되었는지
        final_get_response = client.get(f"/todos/{todo_id}")
        assert final_get_response.status_code == 404
