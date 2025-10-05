"""
개발 서버 실행 스크립트

이 모듈은 개발 환경에서 FastAPI 애플리케이션을 실행하기 위한 스크립트입니다.
설정 파일에서 읽어온 값을 사용하여 uvicorn 서버를 시작합니다.

사용법:
    python run.py

특징:
- 환경변수 기반 설정
- 개발 모드에서 자동 재시작
- 디버그 모드에 따른 로그 레벨 조정
"""

import uvicorn
from config import settings

if __name__ == "__main__":
    """
    메인 실행 블록

    이 스크립트를 직접 실행할 때 uvicorn을 사용하여 FastAPI 애플리케이션을 시작합니다.
    """
    uvicorn.run(
        "app.main:app",                                    # FastAPI 앱 모듈 경로
        host=settings.HOST,                                # 서버 호스트 (기본: 0.0.0.0)
        port=settings.PORT,                                # 서버 포트 (기본: 8000)
        reload=settings.DEBUG,                             # 개발 모드에서 자동 재시작
        log_level="info" if not settings.DEBUG else "debug"  # 로그 레벨 조정
    )
