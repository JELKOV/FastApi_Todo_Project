"""
GET TODO 목록 API 테스트

TODO 목록 조회 API의 다양한 시나리오를 테스트합니다.
- 빈 목록 조회
- 데이터가 있는 목록 조회
- 페이징 테스트
- 필터링 테스트 (완료 상태, 우선순위)
- 정렬 테스트
- 복합 필터링 테스트
"""

import pytest
from fastapi.testclient import TestClient


class TestGetTodosAPI:
    """TODO 목록 조회 API 테스트 클래스"""

    def test_get_todos_empty_list(self, authenticated_client):
        """빈 목록 조회 테스트"""
        response = authenticated_client.get("/todos/")

        assert response.status_code == 200
        data = response.json()

        # 응답 구조 검증
        assert "status" in data
        assert "msg" in data
        assert "data" in data
        assert "meta" in data

        # 빈 목록 확인
        assert data["data"]["todos"] == []
        assert data["data"]["total"] == 0
        assert data["data"]["page"] == 1
        assert data["data"]["size"] == 10

    def test_get_todos_with_data(self, authenticated_client, sample_todo_list):
        """데이터가 있는 목록 조회 테스트"""
        # 테스트 데이터 생성
        created_todos = []
        for todo_data in sample_todo_list:
            response = authenticated_client.post("/todos/", json=todo_data)
            assert response.status_code == 201
            created_todos.append(response.json()["data"])

        # 목록 조회
        response = authenticated_client.get("/todos/")
        assert response.status_code == 200
        data = response.json()

        # 응답 검증
        assert len(data["data"]["todos"]) == len(sample_todo_list)
        assert data["data"]["total"] == len(sample_todo_list)

        # 생성된 TODO들이 모두 포함되어 있는지 확인
        returned_ids = [todo["id"] for todo in data["data"]["todos"]]
        created_ids = [todo["id"] for todo in created_todos]
        assert set(returned_ids) == set(created_ids)

    def test_get_todos_pagination(self, authenticated_client, sample_todo_list):
        """페이징 테스트"""
        # 테스트 데이터 생성
        for todo_data in sample_todo_list:
            response = authenticated_client.post("/todos/", json=todo_data)
            assert response.status_code == 201

        # 첫 번째 페이지 조회 (크기 2)
        response = authenticated_client.get("/todos/?size=2&page=1")
        assert response.status_code == 200
        data = response.json()

        assert len(data["data"]["todos"]) == 2
        assert data["data"]["page"] == 1
        assert data["data"]["size"] == 2
        assert data["data"]["total"] == len(sample_todo_list)

        # 두 번째 페이지 조회
        response = authenticated_client.get("/todos/?size=2&page=2")
        assert response.status_code == 200
        data = response.json()

        assert len(data["data"]["todos"]) == 1  # 마지막 TODO
        assert data["data"]["page"] == 2
        assert data["data"]["size"] == 2

    def test_get_todos_filter_by_completed(self, authenticated_client, sample_todo_list):
        """완료 상태별 필터링 테스트"""
        # 테스트 데이터 생성
        for todo_data in sample_todo_list:
            response = authenticated_client.post("/todos/", json=todo_data)
            assert response.status_code == 201

        # 완료된 TODO만 조회
        response = authenticated_client.get("/todos/?completed=true")
        assert response.status_code == 200
        data = response.json()

        # 모든 반환된 TODO가 완료된 상태인지 확인
        for todo in data["data"]["todos"]:
            assert todo["completed"] is True

        # 미완료 TODO만 조회
        response = authenticated_client.get("/todos/?completed=false")
        assert response.status_code == 200
        data = response.json()

        # 모든 반환된 TODO가 미완료 상태인지 확인
        for todo in data["data"]["todos"]:
            assert todo["completed"] is False

    def test_get_todos_filter_by_priority(self, authenticated_client, sample_todo_list):
        """우선순위별 필터링 테스트"""
        # 테스트 데이터 생성
        for todo_data in sample_todo_list:
            response = authenticated_client.post("/todos/", json=todo_data)
            assert response.status_code == 201

        # 우선순위 2인 TODO만 조회
        response = authenticated_client.get("/todos/?priority=2")
        assert response.status_code == 200
        data = response.json()

        # 모든 반환된 TODO의 우선순위가 2인지 확인
        for todo in data["data"]["todos"]:
            assert todo["priority"] == 2

    def test_get_todos_sort_by_priority_asc(self, authenticated_client, sample_todo_list):
        """우선순위 오름차순 정렬 테스트"""
        # 테스트 데이터 생성
        for todo_data in sample_todo_list:
            response = authenticated_client.post("/todos/", json=todo_data)
            assert response.status_code == 201

        # 우선순위 오름차순 정렬
        response = authenticated_client.get("/todos/?sort_by=priority&sort_order=asc")
        assert response.status_code == 200
        data = response.json()

        # 정렬 순서 확인
        priorities = [todo["priority"] for todo in data["data"]["todos"]]
        assert priorities == sorted(priorities)

    def test_get_todos_sort_by_priority_desc(self, authenticated_client, sample_todo_list):
        """우선순위 내림차순 정렬 테스트"""
        # 테스트 데이터 생성
        for todo_data in sample_todo_list:
            response = authenticated_client.post("/todos/", json=todo_data)
            assert response.status_code == 201

        # 우선순위 내림차순 정렬
        response = authenticated_client.get("/todos/?sort_by=priority&sort_order=desc")
        assert response.status_code == 200
        data = response.json()

        # 정렬 순서 확인
        priorities = [todo["priority"] for todo in data["data"]["todos"]]
        assert priorities == sorted(priorities, reverse=True)

    def test_get_todos_combined_filters(self, authenticated_client, sample_todo_list):
        """복합 필터링 테스트"""
        # 테스트 데이터 생성
        for todo_data in sample_todo_list:
            response = authenticated_client.post("/todos/", json=todo_data)
            assert response.status_code == 201

        # 완료되지 않고 우선순위가 2 이상인 TODO 조회
        response = authenticated_client.get("/todos/?completed=false&priority=2")
        assert response.status_code == 200
        data = response.json()

        # 모든 반환된 TODO가 조건을 만족하는지 확인
        for todo in data["data"]["todos"]:
            assert todo["completed"] is False
            assert todo["priority"] >= 2

    def test_get_todos_invalid_parameters(self, authenticated_client):
        """잘못된 파라미터 테스트"""
        # 잘못된 정렬 순서
        response = authenticated_client.get("/todos/?sort_order=invalid")
        assert response.status_code == 422

        # 잘못된 페이지 번호
        response = authenticated_client.get("/todos/?page=0")
        assert response.status_code == 422

        # 잘못된 페이지 크기
        response = authenticated_client.get("/todos/?size=0")
        assert response.status_code == 422
