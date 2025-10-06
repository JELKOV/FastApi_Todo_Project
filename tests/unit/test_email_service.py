"""
이메일 서비스 테스트

EmailService 클래스의 기능을 테스트합니다.
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from app.core.email_service import EmailService


class TestEmailService:
    """이메일 서비스 테스트 클래스"""

    @pytest.fixture
    def email_service(self):
        """이메일 서비스 픽스처"""
        return EmailService()

    def test_email_service_initialization(self, email_service):
        """이메일 서비스 초기화 테스트"""
        assert email_service.smtp_server == "smtp.gmail.com"
        assert email_service.smtp_port == 587
        assert email_service.from_email == "noreply@example.com"
        assert email_service.smtp_username == ""
        assert email_service.smtp_password == ""

    def test_create_otp_email_body(self, email_service):
        """OTP 이메일 본문 생성 테스트"""
        otp_code = "1234"
        body = email_service._create_otp_email_body(otp_code)

        # OTP 코드가 포함되어야 함
        assert otp_code in body

        # 한국어 텍스트가 포함되어야 함
        assert "안녕하세요!" in body
        assert "Todo API" in body
        assert "5분 후에 만료" in body
        assert "보안을 위해" in body
        assert "감사합니다!" in body

        # 이모지가 포함되어야 함
        assert "👋" in body
        assert "🔐" in body
        assert "⚠️" in body
        assert "🙏" in body

    def test_create_otp_email_body_format(self, email_service):
        """OTP 이메일 본문 형식 테스트"""
        otp_code = "5678"
        body = email_service._create_otp_email_body(otp_code)

        # 본문이 문자열이어야 함
        assert isinstance(body, str)

        # 본문이 비어있지 않아야 함
        assert len(body) > 0

        # 줄바꿈이 포함되어야 함
        assert "\n" in body

        # OTP 코드가 강조 표시되어야 함
        assert f"**OTP 코드: {otp_code}**" in body

    @pytest.mark.asyncio
    async def test_send_otp_email_success(self, email_service):
        """OTP 이메일 전송 성공 테스트"""
        with patch.object(email_service, '_send_email', new_callable=AsyncMock) as mock_send:
            await email_service.send_otp_email("test@example.com", "1234")

            mock_send.assert_called_once()
            call_args = mock_send.call_args[0]
            assert call_args[0] == "test@example.com"  # to_email
            assert "OTP Code" in call_args[1]  # subject
            assert "1234" in call_args[2]  # body

    @pytest.mark.asyncio
    async def test_send_otp_email_error_handling(self, email_service):
        """OTP 이메일 전송 에러 처리 테스트"""
        with patch.object(email_service, '_send_email', side_effect=Exception("SMTP Error")):
            with patch('app.core.email_service.logger') as mock_logger:
                with pytest.raises(Exception):
                    await email_service.send_otp_email("test@example.com", "1234")

                # 에러 로그가 기록되었는지 확인
                mock_logger.error.assert_called_once()
                call_args = mock_logger.error.call_args[0][0]
                assert "Failed to send OTP email" in call_args
                assert "SMTP Error" in call_args

    @pytest.mark.asyncio
    async def test_send_email_development_mode(self, email_service):
        """개발 모드 이메일 전송 테스트"""
        with patch('config.settings.DEBUG', True):
            with patch('builtins.print') as mock_print:
                await email_service._send_email(
                    to_email="test@example.com",
                    subject="Test Subject",
                    body="Test Body"
                )

                # 개발 모드에서는 print가 호출되어야 함
                assert mock_print.called

                # 콘솔 출력 형식 확인
                print_calls = mock_print.call_args_list
                assert len(print_calls) > 0

    @pytest.mark.asyncio
    async def test_send_email_production_mode(self, email_service):
        """프로덕션 모드 이메일 전송 테스트"""
        with patch('config.settings.DEBUG', False):
            with patch('smtplib.SMTP') as mock_smtp:
                # SMTP 컨텍스트 매니저 모킹
                mock_server = MagicMock()
                mock_smtp.return_value.__enter__.return_value = mock_server

                await email_service._send_email(
                    to_email="test@example.com",
                    subject="Test Subject",
                    body="Test Body"
                )

                # SMTP 서버가 호출되었는지 확인
                mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
                mock_server.starttls.assert_called_once()
                mock_server.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_production_mode_with_credentials(self, email_service):
        """인증 정보가 있는 프로덕션 모드 이메일 전송 테스트"""
        # 인증 정보 설정
        email_service.smtp_username = "test@example.com"
        email_service.smtp_password = "testpassword"

        with patch('config.settings.DEBUG', False):
            with patch('smtplib.SMTP') as mock_smtp:
                mock_server = MagicMock()
                mock_smtp.return_value.__enter__.return_value = mock_server

                await email_service._send_email(
                    to_email="test@example.com",
                    subject="Test Subject",
                    body="Test Body"
                )

                # 로그인이 호출되었는지 확인
                mock_server.login.assert_called_once_with("test@example.com", "testpassword")

    @pytest.mark.asyncio
    async def test_send_email_production_mode_smtp_error(self, email_service):
        """프로덕션 모드 SMTP 에러 처리 테스트"""
        with patch('config.settings.DEBUG', False):
            with patch('smtplib.SMTP', side_effect=Exception("SMTP Connection Error")):
                with patch('app.core.email_service.logger') as mock_logger:
                    with pytest.raises(Exception):
                        await email_service._send_email(
                            to_email="test@example.com",
                            subject="Test Subject",
                            body="Test Body"
                        )

                    # SMTP 에러 로그가 기록되었는지 확인
                    mock_logger.error.assert_called_once()
                    call_args = mock_logger.error.call_args[0][0]
                    assert "SMTP error" in call_args
                    assert "SMTP Connection Error" in call_args

    def test_email_service_with_custom_settings(self):
        """사용자 정의 설정으로 이메일 서비스 테스트"""
        with patch('app.core.email_service.settings') as mock_settings:
            mock_settings.SMTP_SERVER = "custom.smtp.com"
            mock_settings.SMTP_PORT = 465
            mock_settings.SMTP_USERNAME = "custom@example.com"
            mock_settings.SMTP_PASSWORD = "custompassword"
            mock_settings.FROM_EMAIL = "noreply@custom.com"

            email_service = EmailService()

            assert email_service.smtp_server == "custom.smtp.com"
            assert email_service.smtp_port == 465
            assert email_service.smtp_username == "custom@example.com"
            assert email_service.smtp_password == "custompassword"
            assert email_service.from_email == "noreply@custom.com"

    def test_email_service_with_missing_settings(self):
        """설정이 누락된 경우 기본값 사용 테스트"""
        # 실제 EmailService의 getattr 동작을 테스트
        from app.core.email_service import EmailService

        # 설정이 None인 경우를 시뮬레이션
        with patch('app.core.email_service.settings') as mock_settings:
            # 설정 속성이 없는 경우를 시뮬레이션
            mock_settings.SMTP_SERVER = None
            mock_settings.SMTP_PORT = None
            mock_settings.SMTP_USERNAME = None
            mock_settings.SMTP_PASSWORD = None
            mock_settings.FROM_EMAIL = None

            email_service = EmailService()

            # None 값이 설정되어야 함 (getattr의 기본값은 None이므로)
            assert email_service.smtp_server is None
            assert email_service.smtp_port is None
            assert email_service.smtp_username is None
            assert email_service.smtp_password is None
            assert email_service.from_email is None


class TestEmailServiceIntegration:
    """이메일 서비스 통합 테스트"""

    @pytest.mark.asyncio
    async def test_complete_otp_email_workflow(self):
        """완전한 OTP 이메일 워크플로우 테스트"""
        email_service = EmailService()

        with patch('config.settings.DEBUG', True):
            with patch('builtins.print') as mock_print:
                await email_service.send_otp_email("integration@example.com", "9999")

                # 이메일이 전송되었는지 확인
                assert mock_print.called

                # 콘솔 출력 내용 확인
                print_calls = [call[0][0] for call in mock_print.call_args_list]
                output_text = " ".join(print_calls)

                assert "integration@example.com" in output_text
                assert "OTP Code" in output_text
                assert "9999" in output_text
                assert "안녕하세요!" in output_text

    @pytest.mark.asyncio
    async def test_email_service_performance(self):
        """이메일 서비스 성능 테스트"""
        email_service = EmailService()

        with patch('config.settings.DEBUG', True):
            with patch('builtins.print'):
                import time

                start_time = time.time()

                # 여러 이메일 전송
                tasks = []
                for i in range(5):
                    task = email_service.send_otp_email(f"test{i}@example.com", f"{i:04d}")
                    tasks.append(task)

                await asyncio.gather(*tasks)

                end_time = time.time()
                total_time = end_time - start_time

                # 5개의 이메일이 2초 이내에 전송되어야 함
                assert total_time < 2.0
