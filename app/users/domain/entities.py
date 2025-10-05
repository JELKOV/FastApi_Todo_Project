"""
사용자 도메인 엔티티 정의

사용자 관련 Pydantic 모델들을 정의합니다.
API 요청/응답 스키마와 데이터 검증을 담당합니다.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
from app.common.schemas import BaseCreateRequest, BaseUpdateRequest


class UserBase(BaseModel):
    """
    사용자 기본 모델

    사용자의 공통 속성을 정의합니다.
    """
    username: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="사용자명 (2-50자)"
    )
    email: Optional[EmailStr] = Field(
        default=None,
        description="이메일 주소 (선택사항)"
    )

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """사용자명 검증"""
        if not v.strip():
            raise ValueError('사용자명은 공백일 수 없습니다')
        return v.strip()


class UserCreate(UserBase, BaseCreateRequest):
    """
    사용자 생성 요청 모델

    회원가입 시 사용되는 스키마입니다.
    """
    password: str = Field(
        ...,
        min_length=4,
        max_length=255,
        description="비밀번호 (4-255자)"
    )

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """비밀번호 검증"""
        if not v.strip():
            raise ValueError('비밀번호는 공백일 수 없습니다')
        if len(v.strip()) < 4:
            raise ValueError('비밀번호는 최소 4자 이상이어야 합니다')
        return v.strip()


class UserUpdate(BaseUpdateRequest):
    """
    사용자 정보 수정 요청 모델

    사용자 정보 업데이트 시 사용되는 스키마입니다.
    """
    username: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=50,
        description="사용자명 (2-50자)"
    )
    email: Optional[EmailStr] = Field(
        default=None,
        description="이메일 주소"
    )
    password: Optional[str] = Field(
        default=None,
        min_length=4,
        max_length=255,
        description="새 비밀번호 (4-255자)"
    )

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """사용자명 검증"""
        if v is not None and not v.strip():
            raise ValueError('사용자명은 공백일 수 없습니다')
        return v.strip() if v else v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """비밀번호 검증"""
        if v is not None and not v.strip():
            raise ValueError('비밀번호는 공백일 수 없습니다')
        if v is not None and len(v.strip()) < 4:
            raise ValueError('비밀번호는 최소 4자 이상이어야 합니다')
        return v.strip() if v else v


class UserResponse(UserBase):
    """
    사용자 정보 응답 모델

    API 응답에서 사용되는 스키마입니다.
    비밀번호는 포함되지 않습니다.
    """
    id: int = Field(
        ...,
        description="사용자 고유 식별자"
    )
    created_at: datetime = Field(
        ...,
        description="계정 생성 시간"
    )
    updated_at: datetime = Field(
        ...,
        description="마지막 수정 시간"
    )

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True
    )


class UserLogin(BaseModel):
    """
    사용자 로그인 요청 모델
    """
    username: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="사용자명"
    )
    password: str = Field(
        ...,
        min_length=4,
        max_length=255,
        description="비밀번호"
    )


class Token(BaseModel):
    """
    JWT 토큰 응답 모델
    """
    access_token: str = Field(
        ...,
        description="액세스 토큰"
    )
    token_type: str = Field(
        default="bearer",
        description="토큰 타입"
    )
    expires_in: int = Field(
        ...,
        description="토큰 만료 시간 (초)"
    )


class TokenData(BaseModel):
    """
    JWT 토큰 데이터 모델
    """
    username: Optional[str] = None


class UserWithTodos(UserResponse):
    """
    TODO 목록을 포함한 사용자 정보 응답 모델
    """
    todos: list = Field(
        default=[],
        description="사용자의 TODO 목록"
    )

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True
    )
