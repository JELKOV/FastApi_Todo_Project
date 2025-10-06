# 🐍 Python 가상환경 완벽 가이드

## 📚 목차
1. [가상환경 기본 개념](#1-가상환경-기본-개념)
2. [프로젝트 설정 단계별 가이드](#2-프로젝트-설정-단계별-가이드)
3. [VS Code 통합 설정](#3-vs-code-통합-설정)
4. [테스트 환경 구축](#4-테스트-환경-구축)
5. [다른 프로젝트 적용법](#5-다른-프로젝트-적용법)
6. [문제 해결](#6-문제-해결)

---

## 1. 가상환경 기본 개념

### 🤔 왜 가상환경이 필요한가?
- **패키지 충돌 방지**: 프로젝트별로 다른 버전의 패키지 사용
- **의존성 격리**: 한 프로젝트의 패키지가 다른 프로젝트에 영향 없음
- **배포 환경 일치**: 개발환경과 운영환경 동일하게 유지

### 📁 가상환경 구조
```
프로젝트/
├── .venv/                    # 가상환경 폴더
│   ├── Scripts/              # Windows 실행파일들
│   │   ├── python.exe        # 격리된 Python
│   │   ├── pip.exe           # 격리된 pip
│   │   └── activate.bat      # 활성화 스크립트
│   └── Lib/site-packages/    # 프로젝트별 패키지들
├── app/                      # 애플리케이션 코드
├── tests/                    # 테스트 코드
└── requirements.txt          # 의존성 목록
```

---

## 2. 프로젝트 설정 단계별 가이드

### 🚀 Step 1: 프로젝트 초기 설정

```bash
# 1. 프로젝트 디렉토리 생성
mkdir my_project
cd my_project

# 2. 가상환경 생성
python -m venv .venv

# 3. 가상환경 활성화 (Windows)
.venv\Scripts\activate

# 3. 가상환경 활성화 (Linux/Mac)
source .venv/bin/activate

# 4. pip 업그레이드
python -m pip install --upgrade pip
```

### 📦 Step 2: 필수 패키지 설치

```bash
# FastAPI 프로젝트 기본 패키지
pip install fastapi uvicorn[standard] python-multipart
pip install pydantic pydantic-settings
pip install sqlalchemy python-dotenv
pip install psycopg2-binary orjson

# 테스트 도구
pip install pytest pytest-asyncio pytest-cov httpx

# 개발 도구 (선택사항)
pip install black flake8 mypy

# 의존성 저장
pip freeze > requirements.txt
```

### ⚙️ Step 3: VS Code 설정

#### `.vscode/settings.json` 생성
```json
{
    "python.pythonPath": "./.venv/Scripts/python.exe",
    "python.defaultInterpreterPath": "./.venv/Scripts/python.exe",
    "python.terminal.activateEnvironment": true,
    "python.terminal.activateEnvInCurrentTerminal": true,
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true,
        ".coverage": true,
        "htmlcov": true
    }
}
```

### 🧪 Step 4: 테스트 환경 설정

#### `pytest.ini` 생성
```ini
[tool:pytest]
testpaths = tests
pythonpath = .
python_files = test_*.py *_test.py
python_functions = test_*
python_classes = Test*

markers =
    unit: 단위 테스트
    integration: 통합 테스트
    slow: 느린 테스트
    database: 데이터베이스 테스트

minversion = 6.0
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning

log_cli = true
log_cli_level = INFO
log_cli_format = %(asctime)s [%(levelname)8s] %(name)s: %(message)s
log_cli_date_format = %Y-%m-%d %H:%M:%S

addopts =
    --strict-markers
    --strict-config
    --verbose
    --tb=short
```

### 🛠️ Step 5: 개발 도구 설정

#### `Makefile` 생성
```makefile
.PHONY: help install test test-cov run dev clean format lint

help: ## 도움말 표시
	@echo "🚀 FastAPI 프로젝트 개발 명령어"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## 의존성 설치
	pip install -r requirements.txt

test: ## 테스트 실행
	pytest

test-cov: ## 커버리지 포함 테스트
	pytest --cov=app --cov-report=html --cov-report=term

run: ## 서버 실행
	python run.py

dev: ## 개발 서버 실행 (자동 재시작)
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

format: ## 코드 포맷팅
	black .
	isort .

lint: ## 린팅 검사
	flake8 .
	mypy app/

clean: ## 캐시 및 임시 파일 정리
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -f .coverage
```

#### `activate.bat` (Windows) 생성
```batch
@echo off
echo 🚀 프로젝트 환경 활성화 중...
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
```

#### `activate.sh` (Linux/Mac) 생성
```bash
#!/bin/bash
echo "🚀 프로젝트 환경 활성화 중..."
source .venv/bin/activate
echo "✅ 가상환경이 활성화되었습니다!"
echo "📍 현재 Python 경로: $VIRTUAL_ENV/bin/python"
echo ""
echo "🛠️  사용 가능한 명령어:"
echo "  python run.py          - 서버 실행"
echo "  pytest                 - 테스트 실행"
echo "  pytest --cov=app       - 커버리지 포함 테스트"
echo "  black .                - 코드 포맷팅"
echo "  flake8 .               - 린팅 검사"
echo ""
bash
```

### 📝 Step 6: Git 설정

#### `.gitignore` 생성
```gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
#Pipfile.lock

# PEP 582; used by e.g. github.com/David-OConnor/pyflow
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# IDE
.vscode/settings.json
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# 프로젝트별
*.db
*.sqlite
todos.db
logs/
temp/
```

---

## 3. VS Code 통합 설정

### 🎯 VS Code가 가상환경을 인식하도록 하는 방법

#### 방법 1: 자동 인식 (권장)
위의 `.vscode/settings.json` 설정으로 자동 인식됩니다.

#### 방법 2: 수동 선택
1. `Ctrl + Shift + P` → "Python: Select Interpreter"
2. `.venv/Scripts/python.exe` 선택

#### 방법 3: VS Code 재시작
1. VS Code 완전 종료
2. 가상환경 활성화된 터미널에서 `code .` 실행

### 🔍 가상환경 확인 방법
```bash
# 현재 Python 경로 확인
python -c "import sys; print(sys.executable)"

# 가상환경 활성화 상태 확인
echo $VIRTUAL_ENV  # Linux/Mac
echo %VIRTUAL_ENV%  # Windows
```

---

## 4. 테스트 환경 구축

### 📁 테스트 디렉토리 구조
```
tests/
├── __init__.py
├── conftest.py           # 공통 픽스처
├── unit/                 # 단위 테스트
│   ├── __init__.py
│   ├── test_domain/      # 도메인 테스트
│   └── test_services/    # 서비스 테스트
├── integration/          # 통합 테스트
│   ├── __init__.py
│   └── test_api/         # API 엔드포인트 테스트
└── fixtures/             # 테스트 데이터
    └── test_data.py
```

### 🧪 기본 테스트 예제

#### `tests/conftest.py`
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base

# 테스트용 인메모리 SQLite 데이터베이스
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
```

#### `tests/unit/test_domain.py`
```python
import pytest
from pydantic import ValidationError
from app.todos.domain.entities import TodoCreate, TodoUpdate

def test_todo_create_valid():
    """유효한 TODO 생성 테스트"""
    todo_data = {
        "title": "테스트 할 일",
        "description": "테스트 설명",
        "priority": 3,
        "completed": False
    }
    todo = TodoCreate(**todo_data)
    assert todo.title == "테스트 할 일"
    assert todo.priority == 3
    assert todo.completed == False

def test_todo_create_invalid_title():
    """잘못된 제목으로 TODO 생성 시 오류"""
    with pytest.raises(ValidationError):
        TodoCreate(title="", description="설명", priority=1)

def test_todo_create_invalid_priority():
    """잘못된 우선순위로 TODO 생성 시 오류"""
    with pytest.raises(ValidationError):
        TodoCreate(title="제목", description="설명", priority=10)
```

#### `tests/integration/test_api.py`
```python
import pytest
from fastapi.testclient import TestClient

def test_create_todo(client: TestClient):
    """TODO 생성 API 테스트"""
    todo_data = {
        "title": "API 테스트 할 일",
        "description": "API 테스트 설명",
        "priority": 3,
        "completed": False
    }

    response = client.post("/todos/", json=todo_data)
    assert response.status_code == 201

    data = response.json()
    assert data["status"] == 201
    assert data["data"]["title"] == "API 테스트 할 일"
    assert data["data"]["priority"] == 3

def test_get_todos(client: TestClient):
    """TODO 목록 조회 API 테스트"""
    response = client.get("/todos/")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == 200
    assert "data" in data
    assert "todos" in data["data"]
```

---

## 5. 다른 프로젝트 적용법

### 🚀 빠른 프로젝트 생성

#### 방법 1: 템플릿 스크립트 사용
```python
# project_template.py (위에서 생성한 파일)
python project_template.py my_new_project
cd my_new_project
activate.bat  # 또는 ./activate.sh
pip install -r requirements.txt
```

#### 방법 2: 수동 복사
```bash
# 새 프로젝트 생성
mkdir my_new_project
cd my_new_project

# 가상환경 생성
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 기존 프로젝트에서 설정 파일 복사
cp ../existing_project/.vscode/settings.json .vscode/
cp ../existing_project/pytest.ini .
cp ../existing_project/Makefile .
cp ../existing_project/activate.bat .
cp ../existing_project/.gitignore .

# 패키지 설치
pip install -r ../existing_project/requirements.txt
```

### 📋 새 프로젝트 체크리스트
- [ ] 가상환경 생성 (`.venv/`)
- [ ] VS Code 설정 (`.vscode/settings.json`)
- [ ] pytest 설정 (`pytest.ini`)
- [ ] 개발 도구 (Makefile, activate scripts)
- [ ] Git 설정 (`.gitignore`)
- [ ] 의존성 설치 (`requirements.txt`)
- [ ] 테스트 환경 구축 (`tests/` 디렉토리)

---

## 6. 문제 해결

### ❌ 자주 발생하는 문제들

#### 1. "ModuleNotFoundError: No module named 'xxx'"
```bash
# 해결: 가상환경이 활성화되었는지 확인
python -c "import sys; print(sys.executable)"
# .venv 경로가 나와야 함

# 해결: 패키지 재설치
pip install -r requirements.txt
```

#### 2. VS Code에서 import 오류 표시
```bash
# 해결: Python 인터프리터 재선택
# Ctrl + Shift + P → "Python: Select Interpreter"
# .venv/Scripts/python.exe 선택
```

#### 3. "sqlalchemy.exc could not be resolved"
```bash
# 해결: 가상환경 활성화 후 VS Code 재시작
.venv\Scripts\activate
# VS Code 완전 종료 후 재시작
```

#### 4. pytest 실행 시 모듈을 찾을 수 없음
```bash
# 해결: pythonpath 설정 확인
# pytest.ini에서 pythonpath = . 설정 확인
```

### 🔧 유용한 명령어들

```bash
# 가상환경 상태 확인
pip list

# 가상환경 비활성화
deactivate

# 의존성 업데이트
pip install --upgrade -r requirements.txt

# 가상환경 완전 삭제 후 재생성
rm -rf .venv  # Linux/Mac
rmdir /s .venv  # Windows
python -m venv .venv
```

---

## 🎯 요약

### ✅ 완벽한 가상환경 설정을 위한 핵심 단계
1. **가상환경 생성**: `python -m venv .venv`
2. **VS Code 설정**: `.vscode/settings.json`으로 자동 인식
3. **테스트 환경**: `pytest.ini`와 `tests/` 구조
4. **개발 도구**: Makefile, 활성화 스크립트
5. **Git 설정**: `.gitignore`로 불필요한 파일 제외

### 🚀 이제 어떤 프로젝트든
- **5분 안에** 완벽한 개발 환경 구축 가능
- **VS Code 자동 인식**으로 편리한 개발
- **일관된 테스트 환경**으로 안정적인 코드
- **팀원들과 설정 공유**로 협업 효율성 증대

이 가이드를 따라하면 **어떤 Python 프로젝트든** 빠르고 안정적으로 개발 환경을 구축할 수 있습니다! 🎉
