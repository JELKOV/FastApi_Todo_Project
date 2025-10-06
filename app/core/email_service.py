"""
이메일 전송 서비스

실제 이메일 전송을 처리하는 서비스입니다.
개발 환경에서는 콘솔 출력, 프로덕션 환경에서는 실제 이메일 전송을 수행합니다.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """이메일 전송 서비스"""

    def __init__(self):
        self.smtp_server = getattr(settings, 'SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_username = getattr(settings, 'SMTP_USERNAME', '')
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', '')
        self.from_email = getattr(settings, 'FROM_EMAIL', 'noreply@example.com')

    async def send_otp_email(self, email: str, otp_code: str):
        """
        OTP 이메일 전송

        Args:
            email: 수신자 이메일 주소
            otp_code: OTP 코드
        """
        try:
            # 이메일 내용 생성
            subject = "🔐 Your OTP Code - Todo API"
            body = self._create_otp_email_body(otp_code)

            # 이메일 전송
            await self._send_email(email, subject, body)
            logger.info(f"✅ OTP email sent successfully to {email}")

        except Exception as e:
            logger.error(f"❌ Failed to send OTP email to {email}: {str(e)}")
            raise

    def _create_otp_email_body(self, otp_code: str) -> str:
        """OTP 이메일 본문 생성"""
        return f"""
안녕하세요! 👋

Todo API에서 요청하신 OTP 코드입니다.

🔐 **OTP 코드: {otp_code}**

⚠️ **중요 사항:**
- 이 코드는 5분 후에 만료됩니다
- 보안을 위해 다른 사람과 공유하지 마세요
- 이 코드는 한 번만 사용할 수 있습니다

문의사항이 있으시면 언제든지 연락주세요.

감사합니다! 🙏
Todo API Team
        """.strip()

    async def _send_email(self, to_email: str, subject: str, body: str):
        """
        실제 이메일 전송

        Args:
            to_email: 수신자 이메일
            subject: 이메일 제목
            body: 이메일 본문
        """
        # 개발 환경에서는 콘솔 출력
        if settings.DEBUG:
            print("\n" + "="*50)
            print("📧 EMAIL SENT (Development Mode)")
            print("="*50)
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"Body:\n{body}")
            print("="*50 + "\n")
            return

        # 프로덕션 환경에서는 실제 이메일 전송
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

        except Exception as e:
            logger.error(f"SMTP error: {str(e)}")
            raise


# 전역 이메일 서비스 인스턴스
email_service = EmailService()
