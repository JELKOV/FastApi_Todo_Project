"""
응답 헬퍼 함수들

이 모듈은 일관된 응답 형식을 생성하는 헬퍼 함수들을 제공합니다.
"""

from datetime import datetime, timezone
from typing import Any, Optional, Dict
from fastapi import Request
from fastapi.responses import JSONResponse

from app.common.error_codes import MessageKey, MessageType, MESSAGES
from app.common.exception_handlers import get_language_from_request, get_success_message


def create_meta_data(request: Request, extra_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """메타데이터를 생성합니다."""
    meta = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": getattr(request.state, 'request_id', 'unknown'),
    }
    
    # 추가 메타데이터가 있으면 병합
    if extra_data:
        meta.update(extra_data)
    
    return meta


def success_response(
    request: Request,
    data: Any = None,
    message_key: MessageKey = MessageKey.SUCCESS,
    status_code: int = 200,
    extra_meta: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """성공 응답을 생성합니다."""
    message = get_success_message(message_key.value, request)
    meta = create_meta_data(request, extra_meta)
    
    response_data = {
        "status": status_code,
        "msg": message,
        "data": data,
        "meta": meta
    }
    
    return JSONResponse(status_code=status_code, content=response_data)


def created_response(
    request: Request,
    data: Any = None,
    message_key: MessageKey = MessageKey.TODO_CREATED,
    location: Optional[str] = None
) -> JSONResponse:
    """생성 응답을 생성합니다."""
    response = success_response(
        request=request,
        data=data,
        message_key=message_key,
        status_code=201
    )
    
    # Location 헤더 추가
    if location:
        response.headers["Location"] = location
    
    return response


def no_content_response(request: Request) -> JSONResponse:
    """No Content 응답을 생성합니다."""
    return JSONResponse(status_code=204, content=None)


def list_response(
    request: Request,
    items: list,
    total: int,
    page: int,
    size: int,
    message_key: MessageKey = MessageKey.TODO_LIST_RETRIEVED
) -> JSONResponse:
    """목록 응답을 생성합니다."""
    data = {
        "todos": items,
        "total": total,
        "page": page,
        "size": size
    }
    
    return success_response(
        request=request,
        data=data,
        message_key=message_key
    )
