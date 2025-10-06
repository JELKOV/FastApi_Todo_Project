"""
TODO API 컨트롤러

이 모듈은 TODO 관련 RESTful API 엔드포인트를 정의합니다.
Clean Architecture의 인터페이스 계층에 해당하며, HTTP 요청을 받아 비즈니스 로직을 호출합니다.

주요 기능:
- TODO CRUD 엔드포인트
- 요청 데이터 검증
- HTTP 상태 코드 및 에러 처리
- 의존성 주입을 통한 서비스 연결
- 구조화된 응답 시스템
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, Request, Response, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.background_tasks import log_user_activity_task  # 🆕 Background Tasks 임포트
from app.todos.application.services import TodoService
from app.todos.domain.entities import (
    TodoCreate,
    TodoUpdate,
    TodoResponse,
    TodoListResponse
)
from app.users.domain.models import User
from app.common.exceptions import TodoNotFoundError, TodoValidationError
from app.common.response_helpers import (
    success_response,
    created_response,
    no_content_response,
    list_response
)
from app.common.error_codes import MessageKey
from app.common.schemas import ErrorResponse

# API 라우터 인스턴스 생성
router = APIRouter()


def get_todo_service(db: Session = Depends(get_db)) -> TodoService:
    """
    TodoService 의존성 주입 함수

    FastAPI의 의존성 주입 시스템에서 사용되는 함수입니다.
    데이터베이스 세션을 주입받아 TodoService 인스턴스를 생성합니다.

    Args:
        db (Session): SQLAlchemy 데이터베이스 세션

    Returns:
        TodoService: TODO 비즈니스 로직 서비스 인스턴스
    """
    return TodoService(db)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "할 일 생성 성공"},
        422: {"model": ErrorResponse, "description": "검증 실패"},
    },
)
async def create_todo(
    request: Request,
    background_tasks: BackgroundTasks,  # 🆕 Background Tasks 주입
    todo_data: TodoCreate,
    todo_service: TodoService = Depends(get_todo_service),
    current_user: User = Depends(get_current_user)
):
    """
    새로운 TODO 생성

    POST /todos/

    새로운 TODO 항목을 생성합니다.
    사용자 활동은 백그라운드에서 로깅됩니다.

    Args:
        request (Request): FastAPI 요청 객체
        background_tasks (BackgroundTasks): 백그라운드 작업 처리
        todo_data (TodoCreate): 생성할 TODO 데이터
        todo_service (TodoService): TODO 서비스 (의존성 주입)
        current_user (User): 현재 인증된 사용자

    Returns:
        JSONResponse: 생성된 TODO 정보 (HTTP 201)

    Raises:
        TodoValidationError: 데이터 검증 실패 시 422 에러
        TodoInternalError: 서버 내부 오류 시 500 에러
    """
    try:
        todo = todo_service.create_todo(todo_data, current_user.id)

        # 🆕 백그라운드에서 사용자 활동 로깅
        background_tasks.add_task(
            log_user_activity_task,
            current_user.id,
            "todo_created",
            {
                "todo_id": todo.id,
                "title": todo.title,
                "priority": todo.priority,
                "completed": todo.completed
            }
        )

        return created_response(
            request=request,
            data=todo.model_dump(mode='json'),
            message_key=MessageKey.TODO_CREATED,
            location=f"/todos/{todo.id}"
        )
    except Exception as e:
        raise TodoValidationError(f"TODO 생성 중 오류가 발생했습니다: {str(e)}", request=request)


@router.get(
    "/",
    responses={
        200: {"description": "할 일 목록 조회 성공"},
        422: {"model": ErrorResponse, "description": "검증 실패"},
    },
)
async def get_todos(
    request: Request,
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
    completed: Optional[bool] = Query(None, description="완료 상태 필터"),
    priority: Optional[int] = Query(None, ge=1, le=5, description="우선순위 필터"),
    sort_by: str = Query("created_at", description="정렬 기준 필드"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="정렬 순서"),
    todo_service: TodoService = Depends(get_todo_service)
):
    """
    TODO 목록 조회 (필터링, 페이징, 정렬)

    GET /todos/

    TODO 목록을 조회합니다. 다양한 필터와 정렬 옵션을 지원합니다.

    Args:
        request (Request): FastAPI 요청 객체
        page (int): 페이지 번호 (1부터 시작)
        size (int): 페이지당 항목 수 (1-100)
        completed (Optional[bool]): 완료 상태로 필터링
        priority (Optional[int]): 우선순위로 필터링 (1-5)
        sort_by (str): 정렬 기준 필드명
        sort_order (str): 정렬 순서 ("asc" 또는 "desc")
        todo_service (TodoService): TODO 서비스 (의존성 주입)

    Returns:
        JSONResponse: 페이징 정보와 함께 TODO 목록

    Query Parameters:
        - page: 페이지 번호 (기본값: 1)
        - size: 페이지 크기 (기본값: 10, 최대: 100)
        - completed: 완료 상태 필터 (true/false)
        - priority: 우선순위 필터 (1-5)
        - sort_by: 정렬 필드 (created_at, updated_at, priority, title)
        - sort_order: 정렬 순서 (asc/desc)
    """
    try:
        # 페이지 번호를 offset으로 변환
        skip = (page - 1) * size

        todo_list = todo_service.get_todos(
            skip=skip,
            limit=size,
            completed=completed,
            priority=priority,
            sort_by=sort_by,
            sort_order=sort_order
        )

        # 응답 데이터 변환
        todos_data = [todo.model_dump(mode='json') for todo in todo_list.todos]

        return list_response(
            request=request,
            items=todos_data,
            total=todo_list.total,
            page=todo_list.page,
            size=todo_list.size,
            message_key=MessageKey.TODO_LIST_RETRIEVED
        )
    except Exception as e:
        raise TodoValidationError(f"TODO 목록 조회 중 오류가 발생했습니다: {str(e)}", request=request)


@router.get(
    "/{todo_id}",
    responses={
        200: {"description": "할 일 조회 성공"},
        404: {"model": ErrorResponse, "description": "할 일을 찾을 수 없음"},
    },
)
async def get_todo(
    request: Request,
    todo_id: int = Path(..., description="TODO ID"),
    todo_service: TodoService = Depends(get_todo_service)
):
    """
    특정 TODO 조회

    GET /todos/{todo_id}

    ID로 특정 TODO를 조회합니다.

    Args:
        request (Request): FastAPI 요청 객체
        todo_id (int): 조회할 TODO의 ID
        todo_service (TodoService): TODO 서비스 (의존성 주입)

    Returns:
        JSONResponse: TODO 정보

    Raises:
        TodoNotFoundError: TODO가 존재하지 않을 때 404 에러
    """
    todo = todo_service.get_todo(todo_id)
    if not todo:
        raise TodoNotFoundError(todo_id, request)

    return success_response(
        request=request,
        data=todo.model_dump(mode='json'),
        message_key=MessageKey.TODO_RETRIEVED
    )


@router.put(
    "/{todo_id}",
    responses={
        200: {"description": "할 일 수정 성공"},
        404: {"model": ErrorResponse, "description": "할 일을 찾을 수 없음"},
        422: {"model": ErrorResponse, "description": "검증 실패"},
    },
)
async def update_todo(
    request: Request,
    todo_data: TodoUpdate,
    todo_id: int = Path(..., description="TODO ID"),
    todo_service: TodoService = Depends(get_todo_service)
):
    """
    TODO 수정

    PUT /todos/{todo_id}

    기존 TODO를 수정합니다. 부분 업데이트를 지원합니다.

    Args:
        request (Request): FastAPI 요청 객체
        todo_data (TodoUpdate): 수정할 데이터
        todo_id (int): 수정할 TODO의 ID
        todo_service (TodoService): TODO 서비스 (의존성 주입)

    Returns:
        JSONResponse: 수정된 TODO 정보

    Raises:
        TodoNotFoundError: TODO가 존재하지 않을 때 404 에러
        TodoValidationError: 데이터 검증 실패 시 422 에러
    """
    try:
        todo = todo_service.update_todo(todo_id, todo_data)
        if not todo:
            raise TodoNotFoundError(todo_id, request)

        return success_response(
            request=request,
            data=todo.model_dump(mode='json'),
            message_key=MessageKey.TODO_UPDATED
        )
    except TodoNotFoundError:
        raise
    except Exception as e:
        raise TodoValidationError(f"TODO 수정 중 오류가 발생했습니다: {str(e)}", request=request)


@router.patch(
    "/{todo_id}/toggle",
    responses={
        200: {"description": "할 일 상태 토글 성공"},
        404: {"model": ErrorResponse, "description": "할 일을 찾을 수 없음"},
    },
)
async def toggle_todo(
    request: Request,
    background_tasks: BackgroundTasks,  # 🆕 Background Tasks 주입
    todo_id: int = Path(..., description="TODO ID"),
    todo_service: TodoService = Depends(get_todo_service),
    current_user: User = Depends(get_current_user)  # 🆕 사용자 인증 추가
):
    """
    TODO 완료 상태 토글

    PATCH /todos/{todo_id}/toggle

    TODO의 완료 상태를 반전시킵니다 (완료 ↔ 미완료).
    사용자 활동은 백그라운드에서 로깅됩니다.

    Args:
        request (Request): FastAPI 요청 객체
        background_tasks (BackgroundTasks): 백그라운드 작업 처리
        todo_id (int): 토글할 TODO의 ID
        todo_service (TodoService): TODO 서비스 (의존성 주입)
        current_user (User): 현재 인증된 사용자

    Returns:
        JSONResponse: 토글된 TODO 정보

    Raises:
        TodoNotFoundError: TODO가 존재하지 않을 때 404 에러
    """
    todo = todo_service.toggle_todo(todo_id, current_user.id)
    if not todo:
        raise TodoNotFoundError(todo_id, request)

    # 🆕 백그라운드에서 사용자 활동 로깅
    background_tasks.add_task(
        log_user_activity_task,
        current_user.id,
        "todo_toggled",
        {
            "todo_id": todo.id,
            "title": todo.title,
            "completed": todo.completed,
            "priority": todo.priority
        }
    )

    return success_response(
        request=request,
        data=todo.model_dump(mode='json'),
        message_key=MessageKey.TODO_TOGGLED
    )


@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "할 일 삭제 성공 (본문 없음)"},
        404: {"model": ErrorResponse, "description": "할 일을 찾을 수 없음"},
    },
)
async def delete_todo(
    request: Request,
    todo_id: int = Path(..., description="TODO ID"),
    todo_service: TodoService = Depends(get_todo_service)
):
    """
    TODO 삭제

    DELETE /todos/{todo_id}

    TODO를 삭제합니다.

    Args:
        request (Request): FastAPI 요청 객체
        todo_id (int): 삭제할 TODO의 ID
        todo_service (TodoService): TODO 서비스 (의존성 주입)

    Returns:
        Response: 성공 시 204 No Content

    Raises:
        TodoNotFoundError: TODO가 존재하지 않을 때 404 에러
    """
    success = todo_service.delete_todo(todo_id)
    if not success:
        raise TodoNotFoundError(todo_id, request)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
