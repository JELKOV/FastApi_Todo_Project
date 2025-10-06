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

# DEBUG 모드를 True로 설정 (개발 모드 - 이메일 콘솔 출력)
settings.DEBUG = True
# 포트를 8000으로 설정 (기본 포트)
settings.PORT = 8000

if __name__ == "__main__":
    """
    메인 실행 블록

    FastAPI 애플리케이션을 시작합니다.
    """
    print("🚀 FastAPI 서버 시작 중...")
    print("=" * 50)
    print(f"📍 호스트: {settings.HOST}")
    print(f"🔌 포트: {settings.PORT}")
    print(f"🔄 자동 재시작: {'활성화' if settings.DEBUG else '비활성화'}")
    print(f"📊 로그 레벨: {'debug' if settings.DEBUG else 'info'}")
    print("=" * 50)

    try:
        uvicorn.run(
            "app.main:app",                                    # FastAPI 앱 모듈 경로
            host=settings.HOST,                                # 서버 호스트 (기본: 0.0.0.0)
            port=settings.PORT,                                # 서버 포트 (기본: 8000)
            reload=False,                                      # reload 모드 비활성화 (가상환경 문제 해결)
            log_level="info" if not settings.DEBUG else "debug"  # 로그 레벨 조정
        )
    except KeyboardInterrupt:
        print("\n\n🛑 서버가 사용자에 의해 중지되었습니다.")
    except Exception as e:
        print(f"\n❌ 서버 시작 중 오류가 발생했습니다: {e}")
        print("💡 가상환경이 활성화되어 있는지 확인하세요:")
        print("   .venv\\Scripts\\activate  (Windows)")
        print("   source .venv/bin/activate  (Linux/Mac)")
        print("💡 필요한 패키지가 설치되어 있는지 확인하세요:")
        print("   pip install -r requirements.txt")
