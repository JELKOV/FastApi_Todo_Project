"""
전역 예외 핸들러

이 모듈은 애플리케이션의 모든 예외를 일관된 형식으로 처리합니다.
"""

import logging
from typing import Optional
from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.common.error_codes import TodoErrorCode, MessageType, MESSAGES
from app.common.exceptions import BaseTodoException
from app.common.schemas import ErrorResponse

logger = logging.getLogger(__name__)


def get_language_from_request(request: Request) -> str:
    """요청에서 언어 정보를 추출합니다."""
    # Accept-Language 헤더에서 언어 추출
    accept_language = request.headers.get("accept-language", "en")
    if accept_language:
        lang = accept_language.split(",")[0].split("-")[0].lower()
        return lang if lang in MESSAGES else "en"
    return "en"


def get_error_message(error_code: TodoErrorCode, request: Optional[Request] = None, lang: Optional[str] = None) -> str:
    """에러 코드에 해당하는 다국어 메시지를 반환합니다."""
    if not request and not lang:
        lang = "en"
    elif request:
        lang = get_language_from_request(request)

    try:
        return MESSAGES[lang][MessageType.ERROR][error_code.value]
    except KeyError:
        # 폴백으로 영어 메시지 반환
        try:
            return MESSAGES["en"][MessageType.ERROR][error_code.value]
        except KeyError:
            return f"Error: {error_code.value}"


def get_success_message(message_key: str, request: Optional[Request] = None, lang: Optional[str] = None) -> str:
    """성공 메시지 키에 해당하는 다국어 메시지를 반환합니다."""
    if not request and not lang:
        lang = "en"
    elif request:
        lang = get_language_from_request(request)

    try:
        return MESSAGES[lang][MessageType.SUCCESS][message_key]
    except KeyError:
        # 폴백으로 영어 메시지 반환
        try:
            return MESSAGES["en"][MessageType.SUCCESS][message_key]
        except KeyError:
            return "Success"


def create_error_response(
    request: Request,
    status_code: int,
    error_code: TodoErrorCode,
    message: Optional[str] = None,
    details: Optional[dict] = None
) -> JSONResponse:
    """에러 응답을 생성합니다."""
    if not message:
        message = get_error_message(error_code, request)

    response_data = {
        "status": status_code,
        "msg": message,
        "data": details or {},
        "meta": {
            "timestamp": "2024-01-01T00:00:00Z",  # 실제로는 datetime.now().isoformat()
            "request_id": getattr(request.state, 'request_id', 'unknown'),
            "error_code": error_code.value
        },
        "error_code": error_code.value
    }

    return JSONResponse(status_code=status_code, content=response_data)


async def todo_exception_handler(request: Request, exc: BaseTodoException) -> JSONResponse:
    """TODO 커스텀 예외 핸들러"""
    logger.error(
        f"Todo Exception: {exc.error_code.value} - {exc.message}",
        extra={
            "error_code": exc.error_code.value,
            "status_code": exc.status_code,
            "details": exc.details,
            "request_id": getattr(request.state, 'request_id', None),
            "url": str(request.url),
            "method": request.method,
        }
    )

    return create_error_response(
        request=request,
        status_code=exc.status_code,
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP 예외 핸들러"""
    logger.warning(
        f"HTTP Exception: {exc.status_code} - {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "request_id": getattr(request.state, 'request_id', None),
            "url": str(request.url),
            "method": request.method,
        }
    )

    # 상태 코드에 따른 에러 코드 매핑
    error_code_map = {
        400: TodoErrorCode.TODO_INVALID_DATA,
        401: TodoErrorCode.TODO_UNAUTHORIZED,
        403: TodoErrorCode.TODO_FORBIDDEN,
        404: TodoErrorCode.TODO_NOT_FOUND,
        409: TodoErrorCode.TODO_ALREADY_EXISTS,
        422: TodoErrorCode.TODO_VALIDATION_ERROR,
        500: TodoErrorCode.TODO_INTERNAL_ERROR,
    }

    error_code = error_code_map.get(exc.status_code, TodoErrorCode.TODO_INTERNAL_ERROR)

    return create_error_response(
        request=request,
        status_code=exc.status_code,
        error_code=error_code,
        message=str(exc.detail),
        details={"detail": str(exc.detail)}
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """요청 검증 예외 핸들러"""
    logger.warning(
        f"Validation Error: {exc.errors()}",
        extra={
            "validation_errors": exc.errors(),
            "request_id": getattr(request.state, 'request_id', None),
            "url": str(request.url),
            "method": request.method,
        }
    )

    return create_error_response(
        request=request,
        status_code=422,
        error_code=TodoErrorCode.TODO_VALIDATION_ERROR,
        message=get_error_message(TodoErrorCode.TODO_VALIDATION_ERROR, request),
        details={"validation_errors": exc.errors()}
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """SQLAlchemy 예외 핸들러"""
    logger.error(
        f"Database Error: {exc!s}",
        extra={
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "request_id": getattr(request.state, 'request_id', None),
            "url": str(request.url),
            "method": request.method,
        },
        exc_info=True
    )

    return create_error_response(
        request=request,
        status_code=500,
        error_code=TodoErrorCode.TODO_DATABASE_ERROR,
        message=get_error_message(TodoErrorCode.TODO_DATABASE_ERROR, request),
        details={"database_error": str(exc)}
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """일반 예외 핸들러"""
    logger.error(
        f"Unexpected Error: {exc!s}",
        extra={
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "request_id": getattr(request.state, 'request_id', None),
            "url": str(request.url),
            "method": request.method,
        },
        exc_info=True
    )

    return create_error_response(
        request=request,
        status_code=500,
        error_code=TodoErrorCode.TODO_INTERNAL_ERROR,
        message=get_error_message(TodoErrorCode.TODO_INTERNAL_ERROR, request),
        details={"unexpected_error": str(exc)}
    )
