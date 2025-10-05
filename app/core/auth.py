"""
JWT 인증 유틸리티 모듈

JWT 토큰 생성, 검증 및 사용자 인증을 위한 유틸리티 함수들을 제공합니다.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from config import settings
from app.core.database import get_db
from app.users.domain.models import User
from app.users.application.services import UserService

# 비밀번호 해시화 컨텍스트
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer 토큰 스키마
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT 액세스 토큰 생성

    Args:
        data: 토큰에 포함할 데이터 (예: {"sub": "username"})
        expires_delta: 토큰 만료 시간 (기본값: 30분)

    Returns:
        str: 생성된 JWT 토큰
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    JWT 토큰 검증

    Args:
        token: 검증할 JWT 토큰

    Returns:
        Optional[str]: 토큰에서 추출한 사용자명 (검증 실패 시 None)
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    현재 인증된 사용자 정보 반환

    Args:
        credentials: HTTP Bearer 토큰
        db: 데이터베이스 세션

    Returns:
        User: 인증된 사용자 정보

    Raises:
        HTTPException: 인증 실패 시 401 에러
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Bearer 토큰에서 JWT 추출
        token = credentials.credentials
        username = verify_token(token)
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    # 사용자 정보 조회
    user_service = UserService(db)
    user = user_service.get_user_by_username_orm(username)  # ORM 객체 반환
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    현재 활성 사용자 정보 반환

    Args:
        current_user: 현재 인증된 사용자

    Returns:
        User: 활성 사용자 정보

    Raises:
        HTTPException: 비활성 사용자일 경우 400 에러
    """
    # 현재는 모든 사용자가 활성 상태로 간주
    # 필요시 User 모델에 is_active 필드 추가
    return current_user


def authenticate_user(db: Session, username: str, password: str) -> Union[User, bool]:
    """
    사용자 인증

    Args:
        db: 데이터베이스 세션
        username: 사용자명
        password: 비밀번호

    Returns:
        Union[User, bool]: 인증 성공 시 User 객체, 실패 시 False
    """
    user_service = UserService(db)
    user = user_service.get_user_by_username_orm(username)  # ORM 객체 반환
    if not user:
        return False

    # bcrypt를 사용한 비밀번호 검증
    if not user_service.verify_password(password, user.password):
        return False

    return user
