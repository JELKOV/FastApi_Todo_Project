"""
에러 코드 및 메시지 관리 시스템

이 모듈은 애플리케이션의 모든 에러 코드와 메시지를 중앙에서 관리합니다.
다국어 지원과 체계적인 에러 코드 분류를 제공합니다.
"""

from enum import Enum
from typing import Dict


class TodoErrorCode(Enum):
    """TODO 관련 에러 코드"""
    
    # 400 Bad Request
    TODO_INVALID_DATA = "E400T001"
    TODO_INVALID_TITLE = "E400T002"
    TODO_INVALID_PRIORITY = "E400T003"
    TODO_INVALID_STATUS = "E400T004"
    
    # 401 Unauthorized
    TODO_UNAUTHORIZED = "E401T001"
    
    # 403 Forbidden
    TODO_FORBIDDEN = "E403T001"
    
    # 404 Not Found
    TODO_NOT_FOUND = "E404T001"
    
    # 409 Conflict
    TODO_ALREADY_EXISTS = "E409T001"
    
    # 422 Validation Error
    TODO_VALIDATION_ERROR = "E422T001"
    TODO_INVALID_FORMAT = "E422T002"
    
    # 500 Internal Server Error
    TODO_INTERNAL_ERROR = "E500T001"
    TODO_DATABASE_ERROR = "E500T002"


class MessageKey(Enum):
    """메시지 키"""
    
    # 성공 메시지
    SUCCESS = "SUCCESS"
    TODO_CREATED = "TODO_CREATED"
    TODO_UPDATED = "TODO_UPDATED"
    TODO_DELETED = "TODO_DELETED"
    TODO_RETRIEVED = "TODO_RETRIEVED"
    TODO_LIST_RETRIEVED = "TODO_LIST_RETRIEVED"
    TODO_TOGGLED = "TODO_TOGGLED"
    
    # 에러 메시지
    TODO_NOT_FOUND = "TODO_NOT_FOUND"
    TODO_VALIDATION_ERROR = "TODO_VALIDATION_ERROR"
    TODO_INTERNAL_ERROR = "TODO_INTERNAL_ERROR"
    TODO_DATABASE_ERROR = "TODO_DATABASE_ERROR"
    TODO_INVALID_DATA = "TODO_INVALID_DATA"


class MessageType(str, Enum):
    """메시지 타입"""
    
    SUCCESS = "success"
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"


# 다국어 메시지 정의
MESSAGES: Dict[str, Dict[MessageType, Dict[str, str]]] = {
    "ko": {
        MessageType.SUCCESS: {
            MessageKey.SUCCESS.value: "성공",
            MessageKey.TODO_CREATED.value: "할 일이 생성되었습니다",
            MessageKey.TODO_UPDATED.value: "할 일이 수정되었습니다",
            MessageKey.TODO_DELETED.value: "할 일이 삭제되었습니다",
            MessageKey.TODO_RETRIEVED.value: "할 일을 조회했습니다",
            MessageKey.TODO_LIST_RETRIEVED.value: "할 일 목록을 조회했습니다",
            MessageKey.TODO_TOGGLED.value: "할 일 상태가 변경되었습니다",
        },
        MessageType.ERROR: {
            TodoErrorCode.TODO_NOT_FOUND.value: "할 일을 찾을 수 없습니다",
            TodoErrorCode.TODO_VALIDATION_ERROR.value: "입력 데이터가 올바르지 않습니다",
            TodoErrorCode.TODO_INTERNAL_ERROR.value: "서버 내부 오류가 발생했습니다",
            TodoErrorCode.TODO_DATABASE_ERROR.value: "데이터베이스 오류가 발생했습니다",
            TodoErrorCode.TODO_INVALID_DATA.value: "유효하지 않은 데이터입니다",
            TodoErrorCode.TODO_INVALID_TITLE.value: "제목이 올바르지 않습니다",
            TodoErrorCode.TODO_INVALID_PRIORITY.value: "우선순위가 올바르지 않습니다",
        }
    },
    "en": {
        MessageType.SUCCESS: {
            MessageKey.SUCCESS.value: "Success",
            MessageKey.TODO_CREATED.value: "Todo created successfully",
            MessageKey.TODO_UPDATED.value: "Todo updated successfully",
            MessageKey.TODO_DELETED.value: "Todo deleted successfully",
            MessageKey.TODO_RETRIEVED.value: "Todo retrieved successfully",
            MessageKey.TODO_LIST_RETRIEVED.value: "Todo list retrieved successfully",
            MessageKey.TODO_TOGGLED.value: "Todo status toggled successfully",
        },
        MessageType.ERROR: {
            TodoErrorCode.TODO_NOT_FOUND.value: "Todo not found",
            TodoErrorCode.TODO_VALIDATION_ERROR.value: "Invalid input data",
            TodoErrorCode.TODO_INTERNAL_ERROR.value: "Internal server error",
            TodoErrorCode.TODO_DATABASE_ERROR.value: "Database error",
            TodoErrorCode.TODO_INVALID_DATA.value: "Invalid data",
            TodoErrorCode.TODO_INVALID_TITLE.value: "Invalid title",
            TodoErrorCode.TODO_INVALID_PRIORITY.value: "Invalid priority",
        }
    }
}
