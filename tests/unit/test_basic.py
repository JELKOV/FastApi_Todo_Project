"""
기본 PyTest 테스트

PyTest가 제대로 동작하는지 확인하는 기본 테스트들입니다.
"""

import pytest
from app.todos.domain.entities import TodoCreate, TodoUpdate


class TestBasicFunctionality:
    """기본 기능 테스트 클래스"""

    def test_pytest_is_working(self):
        """PyTest가 정상 동작하는지 확인"""
        assert True

    def test_simple_math(self):
        """간단한 수학 연산 테스트"""
        assert 2 + 2 == 4
        assert 10 - 5 == 5
        assert 3 * 4 == 12
        assert 8 / 2 == 4

    def test_string_operations(self):
        """문자열 연산 테스트"""
        text = "Hello PyTest"
        assert len(text) == 12
        assert "PyTest" in text
        assert text.upper() == "HELLO PYTEST"

    def test_list_operations(self):
        """리스트 연산 테스트"""
        numbers = [1, 2, 3, 4, 5]
        assert len(numbers) == 5
        assert max(numbers) == 5
        assert min(numbers) == 1
        assert sum(numbers) == 15


class TestPydanticModels:
    """Pydantic 모델 기본 테스트"""

    def test_todo_create_valid(self):
        """유효한 TODO 생성 테스트"""
        todo_data = {
            "title": "테스트 할 일",
            "description": "테스트 설명",
            "priority": 3,
            "completed": False
        }
        todo = TodoCreate(**todo_data)

        assert todo.title == "테스트 할 일"
        assert todo.description == "테스트 설명"
        assert todo.priority == 3
        assert todo.completed == False

    def test_todo_create_default_values(self):
        """기본값이 적용되는지 테스트"""
        todo_data = {"title": "기본값 테스트"}
        todo = TodoCreate(**todo_data)

        assert todo.title == "기본값 테스트"
        assert todo.description is None
        assert todo.priority == 1  # 기본값
        assert todo.completed == False  # 기본값

    def test_todo_update_partial(self):
        """부분 업데이트 테스트"""
        update_data = {"title": "수정된 제목"}
        todo_update = TodoUpdate(**update_data)

        assert todo_update.title == "수정된 제목"
        assert todo_update.description is None
        assert todo_update.priority is None
        assert todo_update.completed is None
