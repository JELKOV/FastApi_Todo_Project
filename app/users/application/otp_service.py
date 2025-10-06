"""
OTP 서비스 레이어

Redis를 활용한 OTP 생성, 저장, 검증 로직을 처리합니다.
"""

import random
from typing import Optional
import redis

from config import settings
from app.common.exceptions import InvalidOTPError, OTPExpiredError, OTPNotFoundError


class OTPService:
    """
    OTP 서비스 클래스
    
    Redis를 사용하여 OTP 생성, 저장, 검증을 처리합니다.
    """

    def __init__(self, redis_client):
        """
        OTPService 초기화
        
        Args:
            redis_client: Redis 클라이언트 인스턴스
        """
        self.redis_client = redis_client
        self.otp_expiration_seconds = settings.OTP_EXPIRATION_MINUTES * 60

    def generate_and_store_otp(self, email: str) -> str:
        """
        4자리 OTP를 생성하고 Redis에 저장합니다.
        이메일을 키로, OTP 코드를 값으로 사용하며, 설정된 시간 동안만 유효합니다.
        
        Args:
            email: 사용자 이메일 (Redis 키로 사용)
            
        Returns:
            str: 생성된 4자리 OTP 코드
        """
        # 4자리 숫자 OTP 생성
        otp_code = str(random.randint(1000, 9999))
        
        # Redis에 OTP 저장 (SETEX: SET with EXPIRE)
        # key: email, value: otp_code, ex: expiration_seconds
        self.redis_client.setex(email, self.otp_expiration_seconds, otp_code)
        
        print(f"🔐 Generated OTP for {email}: {otp_code} (expires in {settings.OTP_EXPIRATION_MINUTES} minutes)")
        return otp_code

    def verify_otp(self, email: str, otp_code: str) -> bool:
        """
        제공된 OTP 코드를 Redis에 저장된 코드와 비교하여 검증합니다.
        검증 성공 시 Redis에서 OTP를 삭제하여 재사용을 방지합니다.
        
        Args:
            email: 사용자 이메일
            otp_code: 검증할 OTP 코드
            
        Returns:
            bool: 검증 성공 여부
            
        Raises:
            OTPNotFoundError: OTP가 없거나 만료된 경우
            InvalidOTPError: OTP가 일치하지 않는 경우
        """
        stored_otp = self.redis_client.get(email)

        if not stored_otp:
            # OTP가 없거나 이미 만료되었거나 사용된 경우
            raise OTPNotFoundError(f"OTP for {email} not found or has expired.")

        if stored_otp != otp_code:
            # OTP가 일치하지 않는 경우
            raise InvalidOTPError("The provided OTP is incorrect.")
        
        # OTP 검증 성공 시, Redis에서 해당 OTP를 삭제하여 재사용 방지
        self.redis_client.delete(email)
        print(f"✅ OTP verified successfully for {email}")
        return True

    def get_remaining_otp_time(self, email: str) -> Optional[int]:
        """
        주어진 이메일에 대한 OTP의 남은 유효 시간을 초 단위로 반환합니다.
        OTP가 없으면 None을 반환합니다.
        
        Args:
            email: 사용자 이메일
            
        Returns:
            Optional[int]: 남은 유효 시간(초) 또는 None
        """
        return self.redis_client.ttl(email)

    def resend_otp(self, email: str) -> str:
        """
        기존 OTP를 무효화하고 새로운 OTP를 생성합니다.
        
        Args:
            email: 사용자 이메일
            
        Returns:
            str: 새로 생성된 OTP 코드
        """
        # 기존 OTP 삭제 (있다면)
        self.redis_client.delete(email)
        
        # 새로운 OTP 생성 및 저장
        return self.generate_and_store_otp(email)

    def is_otp_exists(self, email: str) -> bool:
        """
        해당 이메일에 대한 OTP가 존재하는지 확인합니다.
        
        Args:
            email: 사용자 이메일
            
        Returns:
            bool: OTP 존재 여부
        """
        return self.redis_client.exists(email) == 1
