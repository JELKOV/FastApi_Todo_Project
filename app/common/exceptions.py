"""
커스텀 예외 클래스 정의

이 모듈은 애플리케이션에서 사용되는 커스텀 예외들을 정의합니다.
"""

from typing import Optional, Dict, Any
from fastapi import Request
from app.common.error_codes import TodoErrorCode


class BaseTodoException(Exception):
    """기본 TODO 예외 클래스"""

    def __init__(
        self,
        error_code: TodoErrorCode,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.request = request
        super().__init__(self.message)


class TodoNotFoundError(BaseTodoException):
    """TODO를 찾을 수 없을 때 발생하는 예외"""

    def __init__(self, todo_id: int, request: Optional[Request] = None):
        super().__init__(
            error_code=TodoErrorCode.TODO_NOT_FOUND,
            message=f"Todo with ID {todo_id} not found",
            status_code=404,
            details={"todo_id": todo_id},
            request=request
        )


class TodoValidationError(BaseTodoException):
    """TODO 데이터 검증 실패 시 발생하는 예외"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, request: Optional[Request] = None):
        super().__init__(
            error_code=TodoErrorCode.TODO_VALIDATION_ERROR,
            message=message,
            status_code=422,
            details=details,
            request=request
        )


class TodoInternalError(BaseTodoException):
    """TODO 내부 서버 오류 시 발생하는 예외"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, request: Optional[Request] = None):
        super().__init__(
            error_code=TodoErrorCode.TODO_INTERNAL_ERROR,
            message=message,
            status_code=500,
            details=details,
            request=request
        )


class TodoDatabaseError(BaseTodoException):
    """TODO 데이터베이스 오류 시 발생하는 예외"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, request: Optional[Request] = None):
        super().__init__(
            error_code=TodoErrorCode.TODO_DATABASE_ERROR,
            message=message,
            status_code=500,
            details=details,
            request=request
        )


# OTP 관련 예외 클래스
class OTPError(BaseTodoException):
    """OTP 관련 기본 예외"""
    
    def __init__(self, message: str, error_code: str = "OTP_ERROR", status_code: int = 400, request: Optional[Request] = None):
        super().__init__(
            error_code=error_code,
            message=message,
            status_code=status_code,
            request=request
        )


class InvalidOTPError(OTPError):
    """유효하지 않은 OTP 예외"""
    
    def __init__(self, message: str = "Invalid OTP provided", request: Optional[Request] = None):
        super().__init__(
            message=message,
            error_code="INVALID_OTP",
            status_code=400,
            request=request
        )


class OTPExpiredError(OTPError):
    """만료된 OTP 예외"""
    
    def __init__(self, message: str = "OTP has expired", request: Optional[Request] = None):
        super().__init__(
            message=message,
            error_code="OTP_EXPIRED",
            status_code=400,
            request=request
        )


class OTPNotFoundError(OTPError):
    """OTP를 찾을 수 없는 예외 (아직 요청되지 않았거나 이미 사용됨)"""
    
    def __init__(self, message: str = "OTP not found or already used", request: Optional[Request] = None):
        super().__init__(
            message=message,
            error_code="OTP_NOT_FOUND",
            status_code=404,
            request=request
        )
