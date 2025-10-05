"""
사용자 API 컨트롤러

사용자 관련 REST API 엔드포인트를 정의합니다.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import authenticate_user, create_access_token, get_current_user
from app.users.application.services import UserService
from app.users.domain.entities import UserCreate, UserUpdate, UserResponse, UserLogin, Token
from app.users.domain.models import User
from app.common.response_helpers import success_response, created_response, list_response
from app.common.error_codes import MessageKey
from config import settings
from datetime import timedelta

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """
    UserService 의존성 주입

    Args:
        db: 데이터베이스 세션

    Returns:
        UserService: 사용자 서비스 인스턴스
    """
    return UserService(db)


@router.post("/login", response_model=Token, response_description="사용자 로그인")
async def login(
    request: Request,
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    사용자 로그인 및 JWT 토큰 발급

    Args:
        request: FastAPI 요청 객체
        login_data: 로그인 데이터 (사용자명, 비밀번호)
        db: 데이터베이스 세션

    Returns:
        Token: JWT 액세스 토큰

    Raises:
        HTTPException: 인증 실패 시 401 에러
    """
    # 사용자 인증
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # JWT 토큰 생성
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/", response_description="사용자 생성")
async def create_user(
    request: Request,
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """
    새 사용자 생성

    Args:
        request: FastAPI 요청 객체
        user_data: 사용자 생성 데이터
        user_service: 사용자 서비스

    Returns:
        dict: 생성된 사용자 정보
    """
    user = user_service.create_user(user_data)
    return created_response(
        request=request,
        data=user.model_dump(mode='json'),
        message_key=MessageKey.USER_CREATED
    )


@router.get("/me", response_description="현재 사용자 정보")
async def get_current_user_info(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    현재 인증된 사용자 정보 조회

    Args:
        request: FastAPI 요청 객체
        current_user: 현재 인증된 사용자 (JWT 토큰에서 추출)

    Returns:
        dict: 현재 사용자 정보
    """
    # User ORM 객체를 UserResponse Pydantic 모델로 변환
    user_response = UserResponse.model_validate(current_user)
    return success_response(
        request=request,
        data=user_response.model_dump(mode='json'),
        message_key=MessageKey.USER_RETRIEVED
    )


@router.get("/{user_id}", response_description="사용자 조회")
async def get_user(
    request: Request,
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """
    ID로 사용자 조회

    Args:
        request: FastAPI 요청 객체
        user_id: 사용자 ID
        user_service: 사용자 서비스

    Returns:
        dict: 사용자 정보
    """
    user = user_service.get_user_by_id(user_id)
    return success_response(
        request=request,
        data=user.model_dump(mode='json'),
        message_key=MessageKey.USER_RETRIEVED
    )


@router.get("/", response_description="사용자 목록 조회")
async def list_users(
    request: Request,
    skip: int = Query(0, ge=0, description="건너뛸 레코드 수"),
    limit: int = Query(100, ge=1, le=1000, description="최대 반환 레코드 수"),
    user_service: UserService = Depends(get_user_service)
):
    """
    사용자 목록 조회

    Args:
        request: FastAPI 요청 객체
        skip: 건너뛸 레코드 수
        limit: 최대 반환 레코드 수
        user_service: 사용자 서비스

    Returns:
        dict: 사용자 목록
    """
    users = user_service.list_users(skip=skip, limit=limit)
    user_data = [user.model_dump(mode='json') for user in users]

    return list_response(
        request=request,
        items=user_data,
        total=len(user_data),
        page=skip // limit + 1 if limit > 0 else 1,
        size=limit,
        message_key=MessageKey.USER_LIST_RETRIEVED,
        items_key="users"
    )


@router.put("/{user_id}", response_description="사용자 정보 수정")
async def update_user(
    request: Request,
    user_id: int,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service)
):
    """
    사용자 정보 수정

    Args:
        request: FastAPI 요청 객체
        user_id: 사용자 ID
        user_data: 수정할 사용자 데이터
        user_service: 사용자 서비스

    Returns:
        dict: 수정된 사용자 정보
    """
    user = user_service.update_user(user_id, user_data)
    return success_response(
        request=request,
        data=user.model_dump(mode='json'),
        message_key=MessageKey.USER_UPDATED
    )


@router.delete("/{user_id}", response_description="사용자 삭제")
async def delete_user(
    request: Request,
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """
    사용자 삭제

    Args:
        request: FastAPI 요청 객체
        user_id: 사용자 ID
        user_service: 사용자 서비스

    Returns:
        dict: 삭제 성공 메시지
    """
    user_service.delete_user(user_id)
    return success_response(
        request=request,
        message_key=MessageKey.USER_DELETED
    )


@router.get("/username/{username}", response_description="사용자명으로 사용자 조회")
async def get_user_by_username(
    request: Request,
    username: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    사용자명으로 사용자 조회

    Args:
        request: FastAPI 요청 객체
        username: 사용자명
        user_service: 사용자 서비스

    Returns:
        dict: 사용자 정보
    """
    user = user_service.get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )

    return success_response(
        request=request,
        data=user.model_dump(mode='json'),
        message_key=MessageKey.USER_RETRIEVED
    )


@router.get("/email/{email}", response_description="이메일로 사용자 조회")
async def get_user_by_email(
    request: Request,
    email: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    이메일로 사용자 조회

    Args:
        request: FastAPI 요청 객체
        email: 이메일 주소
        user_service: 사용자 서비스

    Returns:
        dict: 사용자 정보
    """
    user = user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )

    return success_response(
        request=request,
        data=user.model_dump(mode='json'),
        message_key=MessageKey.USER_RETRIEVED
    )
