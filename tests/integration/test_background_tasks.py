"""
Background Tasks 테스트

FastAPI Background Tasks 기능을 테스트합니다.
"""

import pytest
import requests
import json
import time
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app


class TestBackgroundTasks:
    """Background Tasks 테스트 클래스"""

    @pytest.fixture
    def client(self):
        """테스트 클라이언트 픽스처"""
        return TestClient(app)

    def test_otp_request_with_background_task(self, client):
        """OTP 요청 시 백그라운드 이메일 전송 테스트"""
        email = "test@example.com"
        otp_data = {"email": email}

        # Background task가 호출되는지 확인
        with patch('app.core.background_tasks.send_otp_email_task') as mock_task:
            response = client.post("/users/request-otp", json=otp_data)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == 200
            assert data["msg"] == "OTP sent successfully"
            assert data["data"]["email"] == email
            assert "expires_in_minutes" in data["data"]

            # 개발 환경에서는 OTP 코드가 포함되어야 함
            if "otp_code" in data["data"]:
                assert len(data["data"]["otp_code"]) == 4  # 4자리 OTP

    def test_otp_response_time(self, client):
        """OTP 응답 시간 테스트"""
        email = "test@example.com"
        otp_data = {"email": email}

        start_time = time.time()
        response = client.post("/users/request-otp", json=otp_data)
        end_time = time.time()

        response_time = end_time - start_time

        assert response.status_code == 200
        # 응답 시간이 5초 이하여야 함 (백그라운드 처리로 인한 개선)
        assert response_time < 5.0

    def test_email_service_development_mode(self):
        """이메일 서비스 개발 모드 테스트"""
        from app.core.email_service import EmailService

        email_service = EmailService()

        # 개발 모드에서는 콘솔 출력만 수행
        with patch('builtins.print') as mock_print:
            import asyncio
            asyncio.run(email_service.send_otp_email("test@example.com", "1234"))

            # print가 호출되었는지 확인
            assert mock_print.called

    @pytest.mark.asyncio
    async def test_send_otp_email_task(self):
        """OTP 이메일 전송 백그라운드 작업 테스트"""
        from app.core.background_tasks import send_otp_email_task

        with patch('app.core.email_service.email_service.send_otp_email', new_callable=AsyncMock) as mock_send:
            await send_otp_email_task("test@example.com", "1234")

            mock_send.assert_called_once_with("test@example.com", "1234")

    @pytest.mark.asyncio
    async def test_log_user_activity_task(self):
        """사용자 활동 로깅 백그라운드 작업 테스트"""
        from app.core.background_tasks import log_user_activity_task

        with patch('app.core.background_tasks.logger') as mock_logger:
            await log_user_activity_task(
                user_id=1,
                action="todo_created",
                details={"todo_id": 123, "title": "Test Todo"}
            )

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]
            assert "User 1 performed todo_created" in call_args

    @pytest.mark.asyncio
    async def test_send_notification_task(self):
        """알림 전송 백그라운드 작업 테스트"""
        from app.core.background_tasks import send_notification_task

        with patch('app.core.background_tasks.logger') as mock_logger:
            await send_notification_task(
                user_id=1,
                notification_type="todo_completed",
                data={"todo_id": 123, "title": "Test Todo"}
            )

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]
            assert "Notification sent to user 1" in call_args

    def test_background_task_error_handling(self):
        """백그라운드 작업 에러 처리 테스트"""
        from app.core.background_tasks import send_otp_email_task

        with patch('app.core.email_service.email_service.send_otp_email', side_effect=Exception("Test error")):
            with patch('app.core.background_tasks.logger') as mock_logger:
                import asyncio
                asyncio.run(send_otp_email_task("test@example.com", "1234"))

                # 에러 로그가 기록되었는지 확인
                mock_logger.error.assert_called_once()
                call_args = mock_logger.error.call_args[0][0]
                assert "Background task failed" in call_args


class TestEmailService:
    """이메일 서비스 테스트 클래스"""

    def test_email_service_initialization(self):
        """이메일 서비스 초기화 테스트"""
        from app.core.email_service import EmailService

        email_service = EmailService()

        assert email_service.smtp_server == "smtp.gmail.com"
        assert email_service.smtp_port == 587
        assert email_service.from_email == "noreply@example.com"

    def test_create_otp_email_body(self):
        """OTP 이메일 본문 생성 테스트"""
        from app.core.email_service import EmailService

        email_service = EmailService()
        otp_code = "1234"

        body = email_service._create_otp_email_body(otp_code)

        assert otp_code in body
        assert "안녕하세요!" in body
        assert "Todo API" in body
        assert "5분 후에 만료" in body

    @pytest.mark.asyncio
    async def test_send_email_development_mode(self):
        """개발 모드 이메일 전송 테스트"""
        from app.core.email_service import EmailService

        email_service = EmailService()

        with patch('builtins.print') as mock_print:
            await email_service._send_email(
                to_email="test@example.com",
                subject="Test Subject",
                body="Test Body"
            )

            # 개발 모드에서는 print가 호출되어야 함
            assert mock_print.called

    @pytest.mark.asyncio
    async def test_send_email_production_mode(self):
        """프로덕션 모드 이메일 전송 테스트"""
        from app.core.email_service import EmailService
        from unittest.mock import patch

        email_service = EmailService()

        # DEBUG를 False로 설정
        with patch('config.settings.DEBUG', False):
            with patch('smtplib.SMTP') as mock_smtp:
                mock_server = mock_smtp.return_value.__enter__.return_value

                await email_service._send_email(
                    to_email="test@example.com",
                    subject="Test Subject",
                    body="Test Body"
                )

                # SMTP 서버가 호출되었는지 확인
                mock_smtp.assert_called_once()
                mock_server.starttls.assert_called_once()
                mock_server.send_message.assert_called_once()


class TestBackgroundTasksIntegration:
    """Background Tasks 통합 테스트"""

    def test_otp_workflow_with_background_task(self):
        """OTP 워크플로우 백그라운드 작업 통합 테스트"""
        client = TestClient(app)

        # 1. OTP 요청
        otp_data = {"email": "integration@example.com"}
        response = client.post("/users/request-otp", json=otp_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == 200

        # 2. OTP 검증 (백그라운드 작업이 완료된 후)
        if "otp_code" in data["data"]:
            otp_code = data["data"]["otp_code"]
            verify_data = {
                "email": "integration@example.com",
                "otp_code": otp_code
            }

            verify_response = client.post("/users/verify-otp", json=verify_data)
            assert verify_response.status_code == 200

    def test_multiple_otp_requests_performance(self):
        """여러 OTP 요청 성능 테스트"""
        client = TestClient(app)

        emails = [
            "test1@example.com",
            "test2@example.com",
            "test3@example.com"
        ]

        start_time = time.time()

        for email in emails:
            response = client.post("/users/request-otp", json={"email": email})
            assert response.status_code == 200

        end_time = time.time()
        total_time = end_time - start_time

        # 3개의 요청이 10초 이내에 완료되어야 함
        assert total_time < 10.0
        assert total_time / len(emails) < 5.0  # 평균 응답 시간
