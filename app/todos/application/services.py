"""
TODO 애플리케이션 서비스

이 모듈은 TODO 도메인의 비즈니스 로직을 처리하는 서비스 클래스를 정의합니다.
Clean Architecture의 애플리케이션 계층에 해당하며, 도메인 로직과 데이터베이스 접근을 분리합니다.

주요 기능:
- TODO CRUD 작업 (생성, 조회, 수정, 삭제)
- 완료 상태 토글
- 필터링 및 페이징
- 정렬 기능
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from app.todos.domain.models import Todo
from app.todos.domain.entities import TodoCreate, TodoUpdate, TodoResponse, TodoListResponse


class TodoService:
    """
    TODO 비즈니스 로직 서비스

    TODO 도메인의 모든 비즈니스 로직을 처리하는 서비스 클래스입니다.
    데이터베이스 세션을 주입받아 사용하며, 도메인 모델과 Pydantic 엔티티 간의 변환을 담당합니다.
    """

    def __init__(self, db: Session):
        """
        서비스 초기화

        Args:
            db (Session): SQLAlchemy 데이터베이스 세션
        """
        self.db = db

    def create_todo(self, todo_data: TodoCreate, user_id: int = None) -> TodoResponse:
        """
        새로운 TODO 생성

        Args:
            todo_data (TodoCreate): 생성할 TODO 데이터
            user_id (int, optional): 사용자 ID (인증된 사용자)

        Returns:
            TodoResponse: 생성된 TODO 정보 (ID와 타임스탬프 포함)
        """
        # SQLAlchemy 모델 인스턴스 생성
        db_todo = Todo(
            title=todo_data.title,
            description=todo_data.description,
            completed=todo_data.completed,
            priority=todo_data.priority,
            user_id=user_id
        )

        # 데이터베이스에 추가 및 커밋
        self.db.add(db_todo)
        self.db.commit()
        self.db.refresh(db_todo)  # 데이터베이스에서 최신 데이터로 새로고침

        # Pydantic 응답 모델로 변환하여 반환
        return TodoResponse.model_validate(db_todo)

    def get_todo(self, todo_id: int) -> Optional[TodoResponse]:
        """
        ID로 TODO 조회

        Args:
            todo_id (int): 조회할 TODO의 ID

        Returns:
            Optional[TodoResponse]: TODO 정보 (존재하지 않으면 None)
        """
        db_todo = self.db.query(Todo).filter(Todo.id == todo_id).first()
        if db_todo:
            return TodoResponse.model_validate(db_todo)
        return None

    def get_todos(
        self,
        skip: int = 0,
        limit: int = 100,
        completed: Optional[bool] = None,
        priority: Optional[int] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> TodoListResponse:
        """
        TODO 목록 조회 (필터링, 페이징, 정렬 포함)

        Args:
            skip (int): 건너뛸 레코드 수 (페이징용)
            limit (int): 조회할 최대 레코드 수
            completed (Optional[bool]): 완료 상태 필터
            priority (Optional[int]): 우선순위 필터
            sort_by (str): 정렬 기준 필드명
            sort_order (str): 정렬 순서 ("asc" 또는 "desc")

        Returns:
            TodoListResponse: 페이징 정보와 함께 TODO 목록
        """
        # 기본 쿼리 생성
        query = self.db.query(Todo)

        # 필터 적용
        if completed is not None:
            query = query.filter(Todo.completed == completed)
        if priority is not None:
            query = query.filter(Todo.priority == priority)

        # 정렬 적용
        if hasattr(Todo, sort_by):
            if sort_order == "desc":
                query = query.order_by(desc(getattr(Todo, sort_by)))
            else:
                query = query.order_by(asc(getattr(Todo, sort_by)))

        # 전체 개수 조회
        total = query.count()

        # 페이징 적용하여 데이터 조회
        todos = query.offset(skip).limit(limit).all()

        # 응답 모델 생성
        return TodoListResponse(
            todos=[TodoResponse.model_validate(todo) for todo in todos],
            total=total,
            page=skip // limit + 1 if limit > 0 else 1,
            size=limit
        )

    def update_todo(self, todo_id: int, todo_data: TodoUpdate) -> Optional[TodoResponse]:
        """
        TODO 수정

        Args:
            todo_id (int): 수정할 TODO의 ID
            todo_data (TodoUpdate): 수정할 데이터 (부분 업데이트 지원)

        Returns:
            Optional[TodoResponse]: 수정된 TODO 정보 (존재하지 않으면 None)
        """
        # 수정할 TODO 조회
        db_todo = self.db.query(Todo).filter(Todo.id == todo_id).first()
        if not db_todo:
            return None

        # 제공된 필드만 업데이트 (부분 업데이트)
        update_data = todo_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_todo, field, value)

        # 변경사항 커밋
        self.db.commit()
        self.db.refresh(db_todo)

        return TodoResponse.model_validate(db_todo)

    def delete_todo(self, todo_id: int) -> bool:
        """
        TODO 삭제

        Args:
            todo_id (int): 삭제할 TODO의 ID

        Returns:
            bool: 삭제 성공 여부 (존재하지 않는 TODO면 False)
        """
        # 삭제할 TODO 조회
        db_todo = self.db.query(Todo).filter(Todo.id == todo_id).first()
        if not db_todo:
            return False

        # TODO 삭제 및 커밋
        self.db.delete(db_todo)
        self.db.commit()
        return True

    def toggle_todo(self, todo_id: int) -> Optional[TodoResponse]:
        """
        TODO 완료 상태 토글

        Args:
            todo_id (int): 토글할 TODO의 ID

        Returns:
            Optional[TodoResponse]: 토글된 TODO 정보 (존재하지 않으면 None)
        """
        # 토글할 TODO 조회
        db_todo = self.db.query(Todo).filter(Todo.id == todo_id).first()
        if not db_todo:
            return None

        # 완료 상태 반전
        db_todo.completed = not db_todo.completed

        # 변경사항 커밋
        self.db.commit()
        self.db.refresh(db_todo)

        return TodoResponse.model_validate(db_todo)
