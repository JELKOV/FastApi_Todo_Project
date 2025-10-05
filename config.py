"""
애플리케이션 설정 관리

이 모듈은 애플리케이션의 모든 설정값을 중앙에서 관리합니다.
환경변수를 통해 설정값을 오버라이드할 수 있으며, 기본값을 제공합니다.

설정 항목:
- 애플리케이션 정보 (이름, 버전, 디버그 모드)
- 데이터베이스 연결 정보
- 서버 설정 (호스트, 포트)
"""

import os
from dotenv import load_dotenv

# .env 파일을 UTF-8로 로드 (클래스 정의 전에 실행)
load_dotenv(encoding="utf-8")


class Settings:
    """
    애플리케이션 설정 클래스

    모든 애플리케이션 설정을 관리하는 클래스입니다.
    환경변수가 설정되어 있으면 해당 값을 사용하고, 없으면 기본값을 사용합니다.
    """

    # 애플리케이션 기본 정보
    APP_NAME: str = os.getenv("APP_NAME", "Todo RESTful API")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # 데이터베이스 설정
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./todos.db")

    # 서버 설정
    HOST: str = os.getenv("HOST", "0.0.0.0")  # 모든 인터페이스에서 접근 가능
    PORT: int = int(os.getenv("PORT", "8000"))  # 기본 포트 8000


# 전역 설정 인스턴스
# 애플리케이션 전반에서 이 인스턴스를 사용하여 설정값에 접근합니다.
settings = Settings()
