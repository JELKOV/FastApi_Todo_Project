"""
공통 응답 및 요청 스키마 정의

이 모듈은 모든 API 응답과 요청을 일관된 형식으로 관리하는
공통 스키마들을 정의합니다.
"""

from datetime import datetime
from typing import Optional, Any, Generic, TypeVar, Union, List
from pydantic import BaseModel, Field, ConfigDict

T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """기본 응답 모델"""

    status: int = Field(..., description="HTTP 상태 코드")
    msg: str = Field(..., description="응답 메시지")
    data: Optional[T] = Field(None, description="응답 데이터")
    meta: dict = Field(default_factory=dict, description="메타데이터")


class ErrorResponse(BaseModel):
    """에러 응답 모델"""

    status: int = Field(..., description="HTTP 상태 코드")
    msg: str = Field(..., description="에러 메시지")
    data: Optional[dict] = Field(None, description="에러 상세 정보")
    meta: dict = Field(default_factory=dict, description="메타데이터")
    error_code: Optional[str] = Field(None, description="에러 코드")


class SuccessResponse(BaseModel, Generic[T]):
    """성공 응답 모델"""

    status: int = Field(default=200, description="HTTP 상태 코드")
    msg: str = Field(default="Success", description="성공 메시지")
    data: Optional[T] = Field(None, description="응답 데이터")
    meta: dict = Field(default_factory=dict, description="메타데이터")


# ================================
# 공통 요청 모델들
# ================================

class BaseRequest(BaseModel):
    """기본 요청 모델"""

    model_config = ConfigDict(
        str_strip_whitespace=True,  # 문자열 공백 제거
        validate_assignment=True,   # 할당 시 검증
        extra='forbid'             # 추가 필드 금지
    )


class PaginationRequest(BaseRequest):
    """페이징 요청 모델"""

    page: int = Field(
        default=1,
        ge=1,
        description="페이지 번호 (1부터 시작)"
    )
    size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="페이지당 항목 수 (최대 100)"
    )


class SortRequest(BaseRequest):
    """정렬 요청 모델"""

    sort_by: str = Field(
        default="created_at",
        description="정렬 기준 필드"
    )
    sort_order: str = Field(
        default="desc",
        pattern="^(asc|desc)$",
        description="정렬 순서 (asc: 오름차순, desc: 내림차순)"
    )


class SearchRequest(BaseRequest):
    """검색 요청 모델"""

    query: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="검색어"
    )
    filters: Optional[dict] = Field(
        default=None,
        description="추가 필터 조건"
    )


class BaseCreateRequest(BaseRequest):
    """기본 생성 요청 모델"""

    def model_validate_extra(self) -> dict:
        """추가 검증 로직을 위한 메서드"""
        return {}


class BaseUpdateRequest(BaseRequest):
    """기본 수정 요청 모델"""

    def get_update_fields(self) -> dict:
        """실제로 업데이트할 필드만 반환"""
        return self.model_dump(exclude_unset=True, exclude_none=True)


class BulkOperationRequest(BaseRequest):
    """대량 작업 요청 모델"""

    ids: List[int] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="작업할 항목들의 ID 목록"
    )
    operation: str = Field(
        ...,
        pattern="^(delete|update|toggle)$",
        description="수행할 작업 (delete, update, toggle)"
    )
    data: Optional[dict] = Field(
        default=None,
        description="작업에 필요한 추가 데이터"
    )


class FileUploadRequest(BaseRequest):
    """파일 업로드 요청 모델"""

    filename: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="업로드할 파일명"
    )
    content_type: str = Field(
        ...,
        description="파일 MIME 타입"
    )
    size: int = Field(
        ...,
        ge=1,
        le=10*1024*1024,  # 10MB 제한
        description="파일 크기 (바이트)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="파일 설명"
    )


class ValidationRequest(BaseRequest):
    """검증 요청 모델"""

    field_name: str = Field(
        ...,
        min_length=1,
        description="검증할 필드명"
    )
    value: Any = Field(
        ...,
        description="검증할 값"
    )
    rules: Optional[dict] = Field(
        default=None,
        description="검증 규칙"
    )
