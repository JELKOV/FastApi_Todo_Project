"""
TODO 도메인 엔티티 정의

이 모듈은 TODO 도메인의 Pydantic 모델들을 정의합니다.
이 모델들은 API 요청/응답의 데이터 검증과 직렬화에 사용됩니다.

모델 구조:
- TodoBase: 기본 TODO 속성들
- TodoCreate: TODO 생성 시 사용되는 모델
- TodoUpdate: TODO 수정 시 사용되는 모델 (모든 필드가 선택적)
- TodoResponse: API 응답 시 사용되는 모델 (ID와 타임스탬프 포함)
- TodoListResponse: TODO 목록 조회 시 사용되는 페이징 모델
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.common.schemas import BaseCreateRequest, BaseUpdateRequest, PaginationRequest, SortRequest, SearchRequest


class TodoBase(BaseModel):
    """
    기본 TODO 모델

    모든 TODO 엔티티가 공통으로 가지는 기본 속성들을 정의합니다.
    이 클래스는 다른 TODO 모델들의 베이스 클래스로 사용됩니다.
    """
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="할 일 제목"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="할 일 상세 설명"
    )
    completed: bool = Field(
        False,
        description="완료 상태 (true: 완료, false: 미완료)"
    )
    priority: int = Field(
        1,
        ge=1,
        le=5,
        description="우선순위 (1: 낮음, 5: 높음)"
    )


class TodoCreate(TodoBase, BaseCreateRequest):
    """
    TODO 생성 모델

    새로운 TODO를 생성할 때 사용되는 모델입니다.
    TodoBase의 모든 필드를 상속받으며, BaseCreateRequest의 공통 기능도 사용합니다.
    """

    def model_validate_extra(self) -> dict:
        """TODO 생성 시 추가 검증 로직"""
        # 예: 제목에 특수문자 체크, 우선순위별 제한 등
        return {}


class TodoUpdate(BaseUpdateRequest):
    """
    TODO 수정 모델

    기존 TODO를 수정할 때 사용되는 모델입니다.
    모든 필드가 선택적(Optional)이며, BaseUpdateRequest를 상속받아 공통 업데이트 기능을 사용합니다.
    """
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="할 일 제목 (수정 시에만 필요)"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="할 일 상세 설명 (수정 시에만 필요)"
    )
    completed: Optional[bool] = Field(
        None,
        description="완료 상태 (수정 시에만 필요)"
    )
    priority: Optional[int] = Field(
        None,
        ge=1,
        le=5,
        description="우선순위 (수정 시에만 필요)"
    )


class TodoResponse(TodoBase):
    """
    TODO 응답 모델

    API 응답에서 TODO 정보를 반환할 때 사용되는 모델입니다.
    TodoBase의 모든 필드와 함께 데이터베이스에서 생성되는 필드들을 포함합니다.
    """
    id: int = Field(
        ...,
        description="고유 식별자"
    )
    created_at: datetime = Field(
        ...,
        description="생성 시간"
    )
    updated_at: datetime = Field(
        ...,
        description="마지막 수정 시간"
    )
    user_id: Optional[int] = Field(
        None,
        description="생성자 사용자 ID"
    )

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True
    )


class TodoListRequest(PaginationRequest, SortRequest, SearchRequest):
    """
    TODO 목록 조회 요청 모델

    페이징, 정렬, 검색 기능을 모두 포함한 고급 목록 조회 모델입니다.
    """
    completed: Optional[bool] = Field(
        default=None,
        description="완료 상태 필터 (true: 완료, false: 미완료)"
    )
    priority: Optional[int] = Field(
        default=None,
        ge=1,
        le=5,
        description="우선순위 필터 (1-5)"
    )

    def get_filters(self) -> dict:
        """필터 조건을 딕셔너리로 반환"""
        filters = {}
        if self.completed is not None:
            filters['completed'] = self.completed
        if self.priority is not None:
            filters['priority'] = self.priority
        if self.query:
            filters['search'] = self.query
        if self.filters:
            filters.update(self.filters)
        return filters


class TodoBulkRequest(BaseModel):
    """
    TODO 대량 작업 요청 모델

    여러 TODO를 한 번에 처리할 때 사용합니다.
    """
    ids: list[int] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="작업할 TODO ID 목록"
    )
    operation: str = Field(
        ...,
        pattern="^(delete|complete|incomplete|toggle)$",
        description="수행할 작업"
    )
    data: Optional[dict] = Field(
        default=None,
        description="작업에 필요한 추가 데이터"
    )


class TodoListResponse(BaseModel):
    """
    TODO 목록 응답 모델

    TODO 목록을 페이징과 함께 조회할 때 사용되는 모델입니다.
    페이징 정보와 함께 TODO 목록을 포함합니다.
    """
    todos: list[TodoResponse] = Field(
        ...,
        description="TODO 목록"
    )
    total: int = Field(
        ...,
        description="전체 TODO 개수"
    )
    page: int = Field(
        ...,
        description="현재 페이지 번호"
    )
    size: int = Field(
        ...,
        description="페이지당 아이템 개수"
    )
