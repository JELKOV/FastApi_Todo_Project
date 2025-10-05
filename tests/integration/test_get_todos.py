"""
GET 전체 조회 API 테스트

TODO 목록 조회 API의 다양한 시나리오를 테스트합니다.
- 기본 목록 조회
- 페이징 테스트
- 필터링 테스트
- 정렬 테스트
"""

import pytest
from fastapi.testclient import TestClient


class TestGetTodosAPI:
    """TODO 목록 조회 API 테스트 클래스"""

    def test_get_todos_empty_list(self, client: TestClient):
        """빈 목록 조회 테스트"""
        response = client.get("/todos/")

        assert response.status_code == 200
        data = response.json()

        # 응답 구조 검증
        assert "status" in data
        assert "msg" in data
        assert "data" in data
        assert "meta" in data

        # 데이터 내용 검증
        assert data["status"] == 200
        assert data["msg"] == "Todo list retrieved successfully"
        assert data["data"]["todos"] == []
        assert data["data"]["total"] == 0
        assert data["data"]["page"] == 1
        assert data["data"]["size"] == 10

    def test_get_todos_with_data(self, client: TestClient, sample_todo_list):
        """데이터가 있는 목록 조회 테스트"""
        # 테스트 데이터 생성
        created_todos = []
        for todo_data in sample_todo_list:
            response = client.post("/todos/", json=todo_data)
            assert response.status_code == 201
            created_todos.append(response.json()["data"])

        # 목록 조회
        response = client.get("/todos/")

        assert response.status_code == 200
        data = response.json()

        # 응답 구조 검증
        assert data["status"] == 200
        assert data["data"]["total"] == 3
        assert len(data["data"]["todos"]) == 3

        # 생성된 TODO들이 응답에 포함되는지 확인
        response_titles = [todo["title"] for todo in data["data"]["todos"]]
        for created_todo in created_todos:
            assert created_todo["title"] in response_titles

    def test_get_todos_pagination(self, client: TestClient, sample_todo_list):
        """페이징 테스트"""
        # 테스트 데이터 생성
        for todo_data in sample_todo_list:
            response = client.post("/todos/", json=todo_data)
            assert response.status_code == 201

        # 첫 번째 페이지 조회 (크기 2)
        response = client.get("/todos/?page=1&size=2")
        assert response.status_code == 200
        data = response.json()

        assert data["data"]["total"] == 3
        assert data["data"]["page"] == 1
        assert data["data"]["size"] == 2
        assert len(data["data"]["todos"]) == 2

        # 두 번째 페이지 조회
        response = client.get("/todos/?page=2&size=2")
        assert response.status_code == 200
        data = response.json()

        assert data["data"]["total"] == 3
        assert data["data"]["page"] == 2
        assert data["data"]["size"] == 2
        assert len(data["data"]["todos"]) == 1

    def test_get_todos_filter_by_completed(self, client: TestClient, sample_todo_list):
        """완료 상태별 필터링 테스트"""
        # 테스트 데이터 생성
        for todo_data in sample_todo_list:
            response = client.post("/todos/", json=todo_data)
            assert response.status_code == 201

        # 완료된 TODO만 조회
        response = client.get("/todos/?completed=true")
        assert response.status_code == 200
        data = response.json()

        assert data["data"]["total"] == 1
        assert all(todo["completed"] == True for todo in data["data"]["todos"])

        # 미완료 TODO만 조회
        response = client.get("/todos/?completed=false")
        assert response.status_code == 200
        data = response.json()

        assert data["data"]["total"] == 2
        assert all(todo["completed"] == False for todo in data["data"]["todos"])

    def test_get_todos_filter_by_priority(self, client: TestClient, sample_todo_list):
        """우선순위별 필터링 테스트"""
        # 테스트 데이터 생성
        for todo_data in sample_todo_list:
            response = client.post("/todos/", json=todo_data)
            assert response.status_code == 201

        # 우선순위 1인 TODO만 조회
        response = client.get("/todos/?priority=1")
        assert response.status_code == 200
        data = response.json()

        assert data["data"]["total"] == 1
        assert all(todo["priority"] == 1 for todo in data["data"]["todos"])

        # 우선순위 3인 TODO만 조회
        response = client.get("/todos/?priority=3")
        assert response.status_code == 200
        data = response.json()

        assert data["data"]["total"] == 1
        assert all(todo["priority"] == 3 for todo in data["data"]["todos"])

    def test_get_todos_sort_by_priority_asc(self, client: TestClient, sample_todo_list):
        """우선순위 오름차순 정렬 테스트"""
        # 테스트 데이터 생성
        for todo_data in sample_todo_list:
            response = client.post("/todos/", json=todo_data)
            assert response.status_code == 201

        # 우선순위 오름차순 정렬
        response = client.get("/todos/?sort_by=priority&sort_order=asc")
        assert response.status_code == 200
        data = response.json()

        # 정렬 검증
        priorities = [todo["priority"] for todo in data["data"]["todos"]]
        assert priorities == sorted(priorities)

    def test_get_todos_sort_by_priority_desc(self, client: TestClient, sample_todo_list):
        """우선순위 내림차순 정렬 테스트"""
        # 테스트 데이터 생성
        for todo_data in sample_todo_list:
            response = client.post("/todos/", json=todo_data)
            assert response.status_code == 201

        # 우선순위 내림차순 정렬
        response = client.get("/todos/?sort_by=priority&sort_order=desc")
        assert response.status_code == 200
        data = response.json()

        # 정렬 검증
        priorities = [todo["priority"] for todo in data["data"]["todos"]]
        assert priorities == sorted(priorities, reverse=True)

    def test_get_todos_combined_filters(self, client: TestClient, sample_todo_list):
        """복합 필터링 테스트"""
        # 테스트 데이터 생성
        for todo_data in sample_todo_list:
            response = client.post("/todos/", json=todo_data)
            assert response.status_code == 201

        # 완료되지 않았고 우선순위가 1인 TODO 조회
        response = client.get("/todos/?completed=false&priority=1&page=1&size=10")
        assert response.status_code == 200
        data = response.json()

        # 필터링 결과 검증
        for todo in data["data"]["todos"]:
            assert todo["completed"] == False
            assert todo["priority"] == 1

    def test_get_todos_invalid_parameters(self, client: TestClient):
        """잘못된 파라미터 테스트"""
        # 잘못된 정렬 순서
        response = client.get("/todos/?sort_order=invalid")
        assert response.status_code == 422

        # 잘못된 페이지 번호
        response = client.get("/todos/?page=0")
        assert response.status_code == 422

        # 잘못된 페이지 크기
        response = client.get("/todos/?size=1000")
        assert response.status_code == 422

        # 잘못된 우선순위
        response = client.get("/todos/?priority=10")
        assert response.status_code == 422
