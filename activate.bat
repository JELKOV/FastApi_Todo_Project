@echo off
echo 🚀 Todo FastAPI Backend 환경 활성화 중...
call .venv\Scripts\activate.bat
echo ✅ 가상환경이 활성화되었습니다!
echo 📍 현재 Python 경로: %VIRTUAL_ENV%\Scripts\python.exe
echo.
echo 🛠️  사용 가능한 명령어:
echo   python run.py          - 서버 실행
echo   pytest                 - 테스트 실행
echo   pytest --cov=app       - 커버리지 포함 테스트
echo   black .                - 코드 포맷팅
echo   flake8 .               - 린팅 검사
echo.
cmd /k
