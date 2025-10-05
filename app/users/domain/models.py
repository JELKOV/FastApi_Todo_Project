"""
사용자 도메인 SQLAlchemy 모델 정의

이 모듈은 User 엔티티의 데이터베이스 모델을 정의합니다.
SQLAlchemy ORM을 사용하여 데이터베이스 테이블과 매핑되는 모델입니다.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """
    사용자 SQLAlchemy 모델

    데이터베이스의 'users' 테이블과 매핑되는 모델입니다.
    사용자 인증 및 기본 정보를 관리합니다.
    """
    __tablename__ = "users"  # 데이터베이스 테이블 이름

    # 기본 키: 자동 증가하는 정수형 ID
    id = Column(
        Integer,
        primary_key=True,     # 기본 키로 설정
        index=True            # 인덱스 생성으로 조회 성능 향상
    )

    # 사용자명: 최대 50자, 필수 입력, 유니크 제약
    username = Column(
        String(50),
        nullable=False,       # NULL 값 허용하지 않음
        unique=True           # 중복 사용자명 방지
    )

    # 이메일: 최대 100자, 선택 입력, 유니크 제약
    email = Column(
        String(100),
        nullable=True,        # NULL 값 허용 (선택적 필드)
        unique=True           # 중복 이메일 방지
    )

    # 비밀번호: 최대 255자, 필수 입력 (해시된 값)
    password = Column(
        String(255),
        nullable=False        # NULL 값 허용하지 않음
    )

    # 생성 시간: 서버에서 자동 설정
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()  # 데이터베이스에서 현재 시간 자동 설정
    )

    # 수정 시간: 서버에서 자동 업데이트
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),           # 초기 생성 시 현재 시간
        onupdate=func.now()                  # 업데이트 시마다 현재 시간으로 갱신
    )

    # 관계 설정: User가 가진 모든 Todo들 (임시로 주석 처리)
    # todos = relationship(
    #     "app.todos.domain.models.Todo",      # 전체 모듈 경로로 명시
    #     back_populates="user",               # 양방향 관계 설정
    #     cascade="save-update",               # 저장/업데이트 시 연관 객체도 처리
    #     passive_deletes=True                 # 삭제 시 연관 객체는 별도 처리
    # )

    def __repr__(self):
        """
        객체의 문자열 표현

        개발 및 디버깅 시 User 객체의 주요 정보를 보여주는 문자열을 반환합니다.

        Returns:
            str: User 객체의 문자열 표현
                예: "<User(id=1, username='gram', email='gram@example.com')>"
        """
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
