"""
PyTest Mocking 테스트

Mock 객체를 사용하여 외부 의존성을 격리하고 테스트하는 방법을 학습합니다.
- 데이터베이스 의존성 모킹
- 외부 API 호출 모킹
- 파일 시스템 모킹
- 시간 관련 모킹
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.todos.domain.models import Todo
from app.todos.domain.entities import TodoCreate, TodoResponse
from app.todos.application.services import TodoService


class TestMockingBasics:
    """Mock 기본 사용법 테스트"""

    def test_basic_mock(self):
        """기본 Mock 사용법"""
        # Mock 객체 생성
        mock_obj = Mock()

        # Mock 메서드 호출
        mock_obj.some_method.return_value = "mocked result"

        # 메서드 호출 및 검증
        result = mock_obj.some_method()
        assert result == "mocked result"

        # 메서드가 호출되었는지 확인
        mock_obj.some_method.assert_called_once()

    def test_mock_with_side_effect(self):
        """Side effect를 사용한 Mock"""
        mock_obj = Mock()

        # 예외 발생 시뮬레이션
        mock_obj.error_method.side_effect = ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            mock_obj.error_method()

        # 여러 값을 순차적으로 반환
        mock_obj.sequence_method.side_effect = [1, 2, 3]

        assert mock_obj.sequence_method() == 1
        assert mock_obj.sequence_method() == 2
        assert mock_obj.sequence_method() == 3

    def test_mock_call_args(self):
        """Mock 호출 인자 검증"""
        mock_obj = Mock()

        # 메서드 호출
        mock_obj.process_data("test", count=5)

        # 호출 인자 검증
        mock_obj.process_data.assert_called_once_with("test", count=5)

        # 호출 횟수 검증
        assert mock_obj.process_data.call_count == 1


class TestDatabaseMocking:
    """데이터베이스 관련 Mock 테스트"""

    def test_simple_mock_database_operation(self):
        """간단한 Mock 데이터베이스 작업 테스트"""
        # Mock 데이터베이스 객체
        mock_db = Mock()
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.query.return_value = Mock()

        # 데이터베이스 작업 시뮬레이션
        mock_db.add("some_object")
        mock_db.commit()

        # Mock 호출 검증
        mock_db.add.assert_called_once_with("some_object")
        mock_db.commit.assert_called_once()

    def test_mock_query_chain(self):
        """Mock 쿼리 체인 테스트"""
        # Mock 쿼리 객체
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = ["result1", "result2"]

        # 쿼리 체인 실행
        result = mock_query.filter("condition").order_by("field").limit(10).all()

        # 결과 검증
        assert result == ["result1", "result2"]

        # Mock 호출 검증
        mock_query.filter.assert_called_once_with("condition")
        mock_query.order_by.assert_called_once_with("field")
        mock_query.limit.assert_called_once_with(10)
        mock_query.all.assert_called_once()


class TestExternalDependencyMocking:
    """외부 의존성 Mock 테스트"""

    def test_external_api_call_mock(self):
        """외부 API 호출 Mock 테스트 (requests 없이)"""
        # httpx를 사용한 Mock 테스트
        from unittest.mock import patch
        import httpx

        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "mocked data"}

        with patch('httpx.get') as mock_get:
            mock_get.return_value = mock_response

            # 실제 함수에서 httpx.get을 사용한다고 가정
            response = httpx.get("https://api.example.com/data")

            # 검증
            assert response.status_code == 200
            assert response.json() == {"data": "mocked data"}
            mock_get.assert_called_once_with("https://api.example.com/data")

    @patch('builtins.open', new_callable=MagicMock)
    def test_file_operations_mock(self, mock_open):
        """파일 작업 Mock 테스트"""
        # Mock 파일 객체
        mock_file = MagicMock()
        mock_file.read.return_value = "file content"
        mock_file.__enter__.return_value = mock_file
        mock_file.__exit__.return_value = None
        mock_open.return_value = mock_file

        # 파일 읽기 테스트
        with open("test.txt", "r") as f:
            content = f.read()

        # 검증
        assert content == "file content"
        mock_open.assert_called_once_with("test.txt", "r")

    def test_time_mocking(self):
        """시간 관련 Mock 테스트"""
        # 현재 시간을 Mock으로 대체
        current_time = datetime.now(timezone.utc)

        # Mock 객체로 시간 생성
        mock_time = Mock()
        mock_time.year = 2024
        mock_time.month = 1
        mock_time.day = 1
        mock_time.hour = 12
        mock_time.minute = 0
        mock_time.second = 0

        # Mock 시간 검증
        assert mock_time.year == 2024
        assert mock_time.month == 1
        assert mock_time.day == 1


class TestContextManagerMocking:
    """Context Manager Mock 테스트"""

    @patch('app.core.database.get_db')
    def test_database_context_manager_mock(self, mock_get_db):
        """데이터베이스 컨텍스트 매니저 Mock 테스트"""
        # Mock 세션 설정
        mock_session = Mock(spec=Session)
        mock_get_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_get_db.return_value.__exit__ = Mock(return_value=None)

        # 컨텍스트 매니저 사용
        with mock_get_db() as db:
            # 세션이 반환되는지 확인
            assert db == mock_session

        # 컨텍스트 매니저가 올바르게 호출되었는지 확인
        mock_get_db.assert_called_once()


class TestAsyncMocking:
    """비동기 Mock 테스트"""

    @pytest.mark.asyncio
    async def test_async_function_mock(self):
        """비동기 함수 Mock 테스트"""
        # Mock 비동기 함수
        async def mock_async_function():
            return "async result"

        # 비동기 함수 호출
        result = await mock_async_function()

        # 검증
        assert result == "async result"

    @pytest.mark.asyncio
    @patch('asyncio.sleep')
    async def test_async_with_patch(self, mock_sleep):
        """asyncio.sleep Mock 테스트"""
        mock_sleep.return_value = None

        # 비동기 함수에서 sleep 사용
        import asyncio
        await asyncio.sleep(1)

        # 검증
        mock_sleep.assert_called_once_with(1)
