"""
Todo RESTful API with FastAPI

이 모듈은 FastAPI를 사용한 TODO 관리 RESTful API의 메인 애플리케이션입니다.
Clean Architecture 패턴을 적용하여 도메인, 애플리케이션, 인프라, 인터페이스 계층으로 구성되었습니다.

주요 기능:
- TODO CRUD 작업 (생성, 조회, 수정, 삭제)
- 완료 상태 토글
- 필터링 및 페이징
- 자동 API 문서 생성 (Swagger UI, ReDoc)
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import os

from app.core.database import engine, Base
from app.todos.interfaces.api.controller import router as todos_router
from app.users.interfaces.api.controller import router as users_router
from app.common.exceptions import BaseTodoException
from app.common.exception_handlers import (
    todo_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler
)

# SQLite 데이터베이스 사용

# 데이터베이스 테이블 생성
# SQLAlchemy Base 클래스의 메타데이터를 사용하여 모든 모델의 테이블을 생성합니다.
Base.metadata.create_all(bind=engine)

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(
    title=os.getenv("APP_NAME", "Todo RESTful API"),
    description="A complete RESTful API for Todo management built with FastAPI and SQLite",
    version=os.getenv("APP_VERSION", "1.0.0"),
    docs_url="/docs",      # Swagger UI 문서 경로
    redoc_url="/redoc",    # ReDoc 문서 경로
    default_response_class=ORJSONResponse,  # 빠른 JSON 응답
)

# CORS 미들웨어 추가
# 모든 오리진에서의 요청을 허용하여 프론트엔드와의 통신을 가능하게 합니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # 모든 도메인 허용 (프로덕션에서는 특정 도메인으로 제한)
    allow_credentials=True,     # 쿠키 및 인증 헤더 허용
    allow_methods=["*"],        # 모든 HTTP 메서드 허용
    allow_headers=["*"],        # 모든 헤더 허용
)

# 전역 예외 핸들러 등록
# 커스텀 예외부터 일반 예외까지 체계적으로 처리합니다.
app.add_exception_handler(BaseTodoException, todo_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


@app.get("/")
async def root(request: Request):
    """
    루트 엔드포인트

    API의 기본 정보를 반환합니다.
    - API 이름 및 버전
    - 문서 링크
    - 헬스 체크 링크

    Args:
        request (Request): FastAPI 요청 객체

    Returns:
        JSONResponse: API 기본 정보
    """
    from app.common.response_helpers import success_response
    from app.common.error_codes import MessageKey

    data = {
        "name": "Todo RESTful API",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "docs": "/docs",
        "health": "/health"
    }

    return success_response(
        request=request,
        data=data,
        message_key=MessageKey.SUCCESS
    )


@app.get("/health")
async def health_check(request: Request):
    """
    헬스 체크 엔드포인트

    애플리케이션의 상태를 확인합니다.
    - 서버 상태
    - 데이터베이스 연결 상태
    - 버전 정보

    Args:
        request (Request): FastAPI 요청 객체

    Returns:
        JSONResponse: 헬스 체크 결과
    """
    from app.common.response_helpers import success_response
    from app.common.error_codes import MessageKey

    data = {
        "status": "healthy",
        "database": "connected",
        "version": os.getenv("APP_VERSION", "1.0.0")
    }

    return success_response(
        request=request,
        data=data,
        message_key=MessageKey.SUCCESS
    )


# TODO 라우터 등록
# /todos 경로에 TODO 관련 엔드포인트들을 등록합니다.
app.include_router(todos_router, prefix="/todos", tags=["todos"])

# User 라우터 등록
# /users 경로에 User 관련 엔드포인트들을 등록합니다.
app.include_router(users_router, tags=["users"])


if __name__ == "__main__":
    """
    개발 서버 실행

    이 모듈을 직접 실행할 때 uvicorn을 사용하여 개발 서버를 시작합니다.
    DEBUG 환경변수가 'true'로 설정되어 있으면 자동 재시작 기능이 활성화됩니다.
    """
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",                                    # 모든 인터페이스에서 접근 가능
        port=8000,                                         # 포트 8000에서 실행
        reload=os.getenv("DEBUG", "False").lower() == "true"  # 개발 모드에서 자동 재시작
    )
