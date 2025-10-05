# 🚀 FastAPI 프로젝트 개발 환경 설정 가이드

## 📋 현재 프로젝트 설정

이 프로젝트는 다음 설정들이 포함되어 있습니다:

### ✅ 자동 설정된 것들
- **가상환경**: `.venv/` (Python 3.13)
- **VS Code 설정**: `.vscode/settings.json` (자동 인터프리터 선택)
- **pytest 설정**: `pytest.ini` (테스트 환경)
- **개발 도구**: Makefile, 활성화 스크립트
- **Git 설정**: `.gitignore` (Python 프로젝트용)

### 🛠️ 개발 명령어
```bash
# 가상환경 활성화 (Windows)
activate.bat

# 가상환경 활성화 (Linux/Mac)
./activate.sh

# 서버 실행
python run.py

# 테스트 실행
pytest

# 커버리지 포함 테스트
pytest --cov=app

# 코드 포맷팅
black .

# 린팅 검사
flake8 .
```

## 🔄 다른 프로젝트에 적용하기

### 방법 1: 템플릿 스크립트 사용
```bash
# 현재 프로젝트에서 템플릿 생성
python project_template.py my_new_project

# 새 프로젝트로 이동
cd my_new_project

# 활성화
activate.bat  # Windows
./activate.sh  # Linux/Mac
```

### 방법 2: 수동 복사
```bash
# 새 프로젝트 생성
mkdir my_new_project
cd my_new_project

# 가상환경 생성
python -m venv .venv

# 설정 파일들 복사
cp ../todo_fastapi_be/.vscode/settings.json .vscode/
cp ../todo_fastapi_be/pytest.ini .
cp ../todo_fastapi_be/Makefile .
cp ../todo_fastapi_be/activate.bat .
cp ../todo_fastapi_be/.gitignore .

# 활성화
activate.bat
pip install -r requirements.txt
```

## 🎯 설정 범위

### 프로젝트별 설정 (권장)
- ✅ **독립적인 개발 환경**
- ✅ **팀원들과 설정 공유**
- ✅ **프로젝트별 다른 Python 버전**
- ✅ **Git으로 버전 관리**

### 글로벌 설정 (선택사항)
- ⚠️ **모든 프로젝트에 동일한 설정 적용**
- ⚠️ **프로젝트별 독립성 떨어짐**

## 📁 프로젝트 구조
```
my_project/
├── .venv/                 # 가상환경
├── .vscode/               # VS Code 설정
│   └── settings.json
├── app/                   # 애플리케이션 코드
├── tests/                 # 테스트 코드
├── pytest.ini            # pytest 설정
├── Makefile              # 개발 명령어
├── activate.bat/.sh      # 활성화 스크립트
├── requirements.txt      # 의존성
└── .gitignore           # Git 무시 파일
```

## 🔧 문제 해결

### VS Code가 가상환경을 인식하지 못할 때
1. `Ctrl + Shift + P` → "Python: Select Interpreter"
2. `.venv/Scripts/python.exe` 선택

### 패키지 import 오류가 날 때
1. 가상환경이 활성화되었는지 확인
2. `python -c "import sys; print(sys.executable)"`
3. `.venv` 경로가 나오는지 확인
