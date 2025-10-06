"""
백그라운드 작업 함수 테스트

Background Tasks 함수들의 기능을 테스트합니다.
"""

import pytest
from unittest.mock import patch, AsyncMock
from app.core.background_tasks import (
    send_otp_email_task,
    log_user_activity_task,
    send_notification_task,
    cleanup_expired_data_task,
    generate_analytics_task
)


class TestBackgroundTasksFunctions:
    """백그라운드 작업 함수 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_send_otp_email_task_success(self):
        """OTP 이메일 전송 작업 성공 테스트"""
        with patch('app.core.email_service.email_service.send_otp_email', new_callable=AsyncMock) as mock_send:
            with patch('app.core.background_tasks.logger') as mock_logger:
                await send_otp_email_task("test@example.com", "1234")

                # 이메일 서비스가 호출되었는지 확인
                mock_send.assert_called_once_with("test@example.com", "1234")

                # 성공 로그가 기록되었는지 확인
                mock_logger.info.assert_called_once()
                call_args = mock_logger.info.call_args[0][0]
                assert "Background task completed" in call_args
                assert "test@example.com" in call_args

    @pytest.mark.asyncio
    async def test_send_otp_email_task_error(self):
        """OTP 이메일 전송 작업 에러 처리 테스트"""
        with patch('app.core.email_service.email_service.send_otp_email', side_effect=Exception("Email Error")):
            with patch('app.core.background_tasks.logger') as mock_logger:
                await send_otp_email_task("test@example.com", "1234")

                # 에러 로그가 기록되었는지 확인
                mock_logger.error.assert_called_once()
                call_args = mock_logger.error.call_args[0][0]
                assert "Background task failed" in call_args
                assert "test@example.com" in call_args
                assert "Email Error" in call_args

    @pytest.mark.asyncio
    async def test_log_user_activity_task_success(self):
        """사용자 활동 로깅 작업 성공 테스트"""
        with patch('app.core.background_tasks.logger') as mock_logger:
            await log_user_activity_task(
                user_id=123,
                action="todo_created",
                details={"todo_id": 456, "title": "Test Todo", "priority": 3}
            )

            # 활동 로그가 기록되었는지 확인
            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]
            assert "User 123 performed todo_created" in call_args
            assert "todo_id" in call_args
            assert "Test Todo" in call_args

    @pytest.mark.asyncio
    async def test_log_user_activity_task_error(self):
        """사용자 활동 로깅 작업 에러 처리 테스트"""
        with patch('app.core.background_tasks.logger') as mock_logger:
            # 로깅 중 에러 발생 시뮬레이션
            mock_logger.info.side_effect = Exception("Logging Error")

            await log_user_activity_task(
                user_id=123,
                action="todo_created",
                details={"todo_id": 456}
            )

            # 에러 로그가 기록되었는지 확인
            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args[0][0]
            assert "Failed to log user activity" in call_args
            assert "Logging Error" in call_args

    @pytest.mark.asyncio
    async def test_send_notification_task_success(self):
        """알림 전송 작업 성공 테스트"""
        with patch('app.core.background_tasks.logger') as mock_logger:
            await send_notification_task(
                user_id=789,
                notification_type="todo_completed",
                data={"todo_id": 101, "title": "Completed Todo"}
            )

            # 알림 로그가 기록되었는지 확인
            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]
            assert "Notification sent to user 789" in call_args
            assert "todo_completed" in call_args
            assert "Completed Todo" in call_args

    @pytest.mark.asyncio
    async def test_send_notification_task_error(self):
        """알림 전송 작업 에러 처리 테스트"""
        with patch('app.core.background_tasks.logger') as mock_logger:
            # 알림 전송 중 에러 발생 시뮬레이션
            mock_logger.info.side_effect = Exception("Notification Error")

            await send_notification_task(
                user_id=789,
                notification_type="todo_completed",
                data={"todo_id": 101}
            )

            # 에러 로그가 기록되었는지 확인
            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args[0][0]
            assert "Failed to send notification" in call_args
            assert "Notification Error" in call_args

    @pytest.mark.asyncio
    async def test_cleanup_expired_data_task_success(self):
        """만료된 데이터 정리 작업 성공 테스트"""
        with patch('app.core.background_tasks.logger') as mock_logger:
            await cleanup_expired_data_task()

            # 정리 시작 로그 확인
            start_log_calls = [call for call in mock_logger.info.call_args_list
                             if "Starting cleanup" in call[0][0]]
            assert len(start_log_calls) == 1

            # 정리 완료 로그 확인
            complete_log_calls = [call for call in mock_logger.info.call_args_list
                                if "Cleanup completed" in call[0][0]]
            assert len(complete_log_calls) == 1

    @pytest.mark.asyncio
    async def test_cleanup_expired_data_task_error(self):
        """만료된 데이터 정리 작업 에러 처리 테스트"""
        with patch('app.core.background_tasks.logger') as mock_logger:
            # 정리 작업 중 에러 발생 시뮬레이션
            mock_logger.info.side_effect = Exception("Cleanup Error")

            await cleanup_expired_data_task()

            # 에러 로그가 기록되었는지 확인
            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args[0][0]
            assert "Cleanup task failed" in call_args
            assert "Cleanup Error" in call_args

    @pytest.mark.asyncio
    async def test_generate_analytics_task_success(self):
        """분석 데이터 생성 작업 성공 테스트"""
        with patch('app.core.background_tasks.logger') as mock_logger:
            await generate_analytics_task()

            # 분석 시작 로그 확인
            start_log_calls = [call for call in mock_logger.info.call_args_list
                             if "Generating analytics" in call[0][0]]
            assert len(start_log_calls) == 1

            # 분석 완료 로그 확인
            complete_log_calls = [call for call in mock_logger.info.call_args_list
                                if "Analytics generation completed" in call[0][0]]
            assert len(complete_log_calls) == 1

    @pytest.mark.asyncio
    async def test_generate_analytics_task_error(self):
        """분석 데이터 생성 작업 에러 처리 테스트"""
        with patch('app.core.background_tasks.logger') as mock_logger:
            # 분석 작업 중 에러 발생 시뮬레이션
            mock_logger.info.side_effect = Exception("Analytics Error")

            await generate_analytics_task()

            # 에러 로그가 기록되었는지 확인
            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args[0][0]
            assert "Analytics generation failed" in call_args
            assert "Analytics Error" in call_args


class TestBackgroundTasksIntegration:
    """백그라운드 작업 통합 테스트"""

    @pytest.mark.asyncio
    async def test_multiple_background_tasks_concurrent(self):
        """여러 백그라운드 작업 동시 실행 테스트"""
        with patch('app.core.background_tasks.logger') as mock_logger:
            import asyncio

            # 여러 작업을 동시에 실행
            tasks = [
                log_user_activity_task(1, "todo_created", {"todo_id": 1}),
                log_user_activity_task(2, "todo_updated", {"todo_id": 2}),
                send_notification_task(1, "todo_completed", {"todo_id": 1}),
                send_notification_task(2, "todo_completed", {"todo_id": 2}),
            ]

            await asyncio.gather(*tasks)

            # 모든 작업이 완료되었는지 확인
            assert mock_logger.info.call_count == 4

    @pytest.mark.asyncio
    async def test_background_tasks_with_different_data_types(self):
        """다양한 데이터 타입으로 백그라운드 작업 테스트"""
        with patch('app.core.background_tasks.logger') as mock_logger:
            # 다양한 데이터 타입 테스트
            await log_user_activity_task(
                user_id=1,
                action="complex_action",
                details={
                    "string": "test",
                    "number": 123,
                    "boolean": True,
                    "list": [1, 2, 3],
                    "dict": {"nested": "value"},
                    "none": None
                }
            )

            # 로그가 기록되었는지 확인
            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]
            assert "User 1 performed complex_action" in call_args
            assert "string" in call_args
            assert "test" in call_args

    @pytest.mark.asyncio
    async def test_background_tasks_error_recovery(self):
        """백그라운드 작업 에러 복구 테스트"""
        with patch('app.core.background_tasks.logger') as mock_logger:
            # 첫 번째 작업은 실패, 두 번째 작업은 성공
            mock_logger.info.side_effect = [Exception("First Error"), None]

            # 첫 번째 작업 (실패)
            await log_user_activity_task(1, "failed_action", {"data": "test"})

            # 두 번째 작업 (성공)
            await log_user_activity_task(2, "success_action", {"data": "test"})

            # 에러 로그와 성공 로그가 모두 기록되었는지 확인
            error_calls = [call for call in mock_logger.error.call_args_list
                          if "Failed to log user activity" in call[0][0]]
            success_calls = [call for call in mock_logger.info.call_args_list
                           if "User 2 performed success_action" in call[0][0]]

            assert len(error_calls) == 1
            assert len(success_calls) == 1
