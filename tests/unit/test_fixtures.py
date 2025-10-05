"""
PyTest Fixture 테스트

pytest fixture의 다양한 활용법을 학습합니다.
- 기본 fixture 사용법
- fixture scope (function, class, module, session)
- fixture 의존성
- fixture 파라미터화
- fixture 공유
"""

import pytest
from unittest.mock import Mock
from datetime import datetime, timezone


class TestFixtureBasics:
    """Fixture 기본 사용법 테스트"""

    def test_simple_fixture(self, sample_todo_data):
        """간단한 fixture 사용 테스트"""
        assert sample_todo_data["title"] == "테스트 할 일"
        assert sample_todo_data["priority"] == 3
        assert sample_todo_data["completed"] == False

    def test_multiple_fixtures(self, sample_todo_data, sample_todo_list):
        """여러 fixture 사용 테스트"""
        # sample_todo_data 검증
        assert sample_todo_data["title"] == "테스트 할 일"

        # sample_todo_list 검증
        assert len(sample_todo_list) == 3
        assert all("title" in todo for todo in sample_todo_list)

    def test_fixture_with_client(self, client, sample_todo_data):
        """클라이언트 fixture 사용 테스트"""
        # POST 요청으로 TODO 생성
        response = client.post("/todos/", json=sample_todo_data)

        assert response.status_code == 201
        data = response.json()
        assert data["data"]["title"] == sample_todo_data["title"]


class TestFixtureScope:
    """Fixture Scope 테스트"""

    @pytest.fixture(scope="function")
    def function_scope_fixture(self):
        """Function scope fixture (기본값)"""
        print("Function scope fixture 생성")
        return datetime.now()

    @pytest.fixture(scope="class")
    def class_scope_fixture(self):
        """Class scope fixture"""
        print("Class scope fixture 생성")
        return datetime.now()

    def test_function_scope_1(self, function_scope_fixture):
        """Function scope 테스트 1"""
        print(f"Function scope 1: {function_scope_fixture}")
        assert isinstance(function_scope_fixture, datetime)

    def test_function_scope_2(self, function_scope_fixture):
        """Function scope 테스트 2"""
        print(f"Function scope 2: {function_scope_fixture}")
        assert isinstance(function_scope_fixture, datetime)

    def test_class_scope_1(self, class_scope_fixture):
        """Class scope 테스트 1"""
        print(f"Class scope 1: {class_scope_fixture}")
        assert isinstance(class_scope_fixture, datetime)

    def test_class_scope_2(self, class_scope_fixture):
        """Class scope 테스트 2"""
        print(f"Class scope 2: {class_scope_fixture}")
        assert isinstance(class_scope_fixture, datetime)


class TestFixtureDependency:
    """Fixture 의존성 테스트"""

    @pytest.fixture
    def base_data(self):
        """기본 데이터 fixture"""
        return {"base": "data"}

    @pytest.fixture
    def enhanced_data(self, base_data):
        """base_data에 의존하는 fixture"""
        enhanced = base_data.copy()
        enhanced["enhanced"] = "value"
        return enhanced

    @pytest.fixture
    def final_data(self, enhanced_data, sample_todo_data):
        """여러 fixture에 의존하는 fixture"""
        final = enhanced_data.copy()
        final["todo"] = sample_todo_data
        return final

    def test_fixture_dependency_chain(self, final_data):
        """Fixture 의존성 체인 테스트"""
        assert "base" in final_data
        assert "enhanced" in final_data
        assert "todo" in final_data
        assert final_data["todo"]["title"] == "테스트 할 일"


class TestFixtureParameterization:
    """Fixture 파라미터화 테스트"""

    @pytest.fixture(params=[1, 2, 3])
    def priority_level(self, request):
        """우선순위 레벨 fixture"""
        return request.param

    @pytest.fixture(params=["low", "medium", "high"])
    def priority_name(self, request):
        """우선순위 이름 fixture"""
        return request.param

    def test_priority_levels(self, priority_level):
        """우선순위 레벨 테스트"""
        assert 1 <= priority_level <= 3

    def test_priority_names(self, priority_name):
        """우선순위 이름 테스트"""
        assert priority_name in ["low", "medium", "high"]

    def test_priority_combination(self, priority_level, priority_name):
        """우선순위 조합 테스트"""
        assert isinstance(priority_level, int)
        assert isinstance(priority_name, str)


class TestCustomFixtures:
    """커스텀 Fixture 테스트"""

    @pytest.fixture
    def mock_todo_service(self):
        """Mock TodoService fixture"""
        mock_service = Mock()
        mock_service.create_todo.return_value = Mock(
            id=1,
            title="Mocked Todo",
            description="Mocked Description",
            priority=3,
            completed=False
        )
        return mock_service

    @pytest.fixture
    def todo_with_high_priority(self):
        """높은 우선순위 TODO fixture"""
        return {
            "title": "높은 우선순위 할 일",
            "description": "중요한 작업",
            "priority": 5,
            "completed": False
        }

    @pytest.fixture
    def completed_todo(self):
        """완료된 TODO fixture"""
        return {
            "title": "완료된 할 일",
            "description": "이미 끝난 작업",
            "priority": 2,
            "completed": True
        }

    def test_mock_service(self, mock_todo_service, sample_todo_data):
        """Mock 서비스 fixture 테스트"""
        result = mock_todo_service.create_todo(sample_todo_data)

        assert result.id == 1
        assert result.title == "Mocked Todo"
        mock_todo_service.create_todo.assert_called_once_with(sample_todo_data)

    def test_high_priority_todo(self, client, todo_with_high_priority):
        """높은 우선순위 TODO 테스트"""
        response = client.post("/todos/", json=todo_with_high_priority)

        assert response.status_code == 201
        data = response.json()
        assert data["data"]["priority"] == 5

    def test_completed_todo(self, client, completed_todo):
        """완료된 TODO 테스트"""
        response = client.post("/todos/", json=completed_todo)

        assert response.status_code == 201
        data = response.json()
        assert data["data"]["completed"] == True


class TestFixtureTeardown:
    """Fixture Teardown 테스트"""

    @pytest.fixture
    def resource_with_cleanup(self):
        """리소스 정리가 필요한 fixture"""
        resource = {"data": "important"}
        print("리소스 생성")
        yield resource
        print("리소스 정리")

    @pytest.fixture
    def multiple_resources(self):
        """여러 리소스 관리 fixture"""
        resources = []
        try:
            for i in range(3):
                resource = {"id": i, "data": f"resource_{i}"}
                resources.append(resource)
                print(f"리소스 {i} 생성")
            yield resources
        finally:
            print("모든 리소스 정리")

    def test_resource_cleanup(self, resource_with_cleanup):
        """리소스 정리 테스트"""
        assert resource_with_cleanup["data"] == "important"

    def test_multiple_resource_cleanup(self, multiple_resources):
        """여러 리소스 정리 테스트"""
        assert len(multiple_resources) == 3
        assert multiple_resources[0]["id"] == 0
        assert multiple_resources[2]["data"] == "resource_2"


class TestFixtureSharing:
    """Fixture 공유 테스트"""

    @pytest.fixture
    def shared_data(self):
        """공유 데이터 fixture"""
        return {"shared": "data", "count": 0}

    def test_shared_data_1(self, shared_data):
        """공유 데이터 테스트 1"""
        shared_data["count"] += 1
        assert shared_data["count"] == 1

    def test_shared_data_2(self, shared_data):
        """공유 데이터 테스트 2"""
        shared_data["count"] += 1
        assert shared_data["count"] == 1  # 새로운 인스턴스


class TestFixtureAutouse:
    """Autouse Fixture 테스트"""

    @pytest.fixture(autouse=True)
    def auto_setup(self):
        """자동으로 실행되는 fixture"""
        print("자동 설정 시작")
        yield
        print("자동 정리 완료")

    def test_with_autouse(self):
        """Autouse fixture 테스트"""
        assert True  # autouse fixture가 자동으로 실행됨
