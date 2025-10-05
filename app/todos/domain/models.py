"""
TODO 도메인 SQLAlchemy 모델 정의

이 모듈은 TODO와 User 엔티티의 데이터베이스 모델을 정의합니다.
SQLAlchemy ORM을 사용하여 데이터베이스 테이블과 매핑되는 모델입니다.

주요 특징:
- User 모델: 사용자 인증 및 관리
- Todo 모델: 할 일 관리 (User와 FK 관계)
- 자동 생성되는 ID (Primary Key)
- 자동 타임스탬프 (생성/수정 시간)
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Todo(Base):
    """
    TODO SQLAlchemy 모델

    데이터베이스의 'todos' 테이블과 매핑되는 모델입니다.
    각 TODO 항목의 모든 속성과 메타데이터를 정의합니다.
    User와의 외래키 관계를 통해 사용자별 TODO 관리를 지원합니다.
    """
    __tablename__ = "todos"  # 데이터베이스 테이블 이름

    # 기본 키: 자동 증가하는 정수형 ID
    id = Column(
        Integer,
        primary_key=True,     # 기본 키로 설정
        index=True            # 인덱스 생성으로 조회 성능 향상
    )

    # 할 일 제목: 최대 200자, 필수 입력, 인덱스 생성
    title = Column(
        String(200),
        nullable=False,       # NULL 값 허용하지 않음
        index=True            # 제목으로 검색 시 성능 향상을 위한 인덱스
    )

    # 할 일 상세 설명: 텍스트 타입, 선택 입력
    description = Column(
        Text,
        nullable=True         # NULL 값 허용 (선택적 필드)
    )

    # 완료 상태: 불린 타입, 기본값 False
    completed = Column(
        Boolean,
        default=False,        # 기본값: 미완료
        nullable=False        # NULL 값 허용하지 않음
    )

    # 우선순위: 1-5 범위의 정수, 기본값 1
    priority = Column(
        Integer,
        default=1,            # 기본값: 낮은 우선순위
        nullable=False        # NULL 값 허용하지 않음
    )

    # 사용자 외래키: User 테이블의 id 참조
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),  # 사용자 삭제 시 NULL로 설정
        nullable=True,        # NULL 값 허용 (익명 TODO 지원)
        index=True            # 사용자별 조회 성능 향상
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

    # 관계 설정: 이 TODO를 소유한 User (임시로 주석 처리)
    # user = relationship(
    #     "app.users.domain.models.User",      # 전체 모듈 경로로 명시
    #     back_populates="todos"               # 양방향 관계 설정
    # )

    def __repr__(self):
        """
        객체의 문자열 표현

        개발 및 디버깅 시 TODO 객체의 주요 정보를 보여주는 문자열을 반환합니다.

        Returns:
            str: TODO 객체의 문자열 표현
                예: "<Todo(id=1, title='할 일 제목', completed=False)>"
        """
        return f"<Todo(id={self.id}, title='{self.title}', completed={self.completed})>"
