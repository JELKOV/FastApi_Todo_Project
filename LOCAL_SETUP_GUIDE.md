# 🏠 개인 로컬 환경 일관성 가이드

## 🎯 목표
개인 컴퓨터에서 **모든 Python 프로젝트**에 동일한 개발 환경을 적용하여 일관성 있는 개발 경험을 제공합니다.

---

## 📁 개인 개발 환경 구조

```
📁 개발환경/
├── 📁 templates/                    # 프로젝트 템플릿 저장소
│   ├── fastapi_template/            # FastAPI 프로젝트 템플릿
│   ├── django_template/             # Django 프로젝트 템플릿
│   └── flask_template/              # Flask 프로젝트 템플릿
├── 📁 scripts/                      # 자동화 스크립트
│   ├── create_project.py            # 프로젝트 생성 스크립트
│   ├── setup_dev_env.py             # 개발환경 설정 스크립트
│   └── sync_settings.py             # 설정 동기화 스크립트
├── 📁 configs/                      # 공통 설정 파일
│   ├── vscode_settings.json         # VS Code 설정
│   ├── pytest_template.ini          # pytest 설정 템플릿
│   ├── makefile_template            # Makefile 템플릿
│   └── gitignore_template           # .gitignore 템플릿
└── 📁 projects/                     # 실제 프로젝트들
    ├── 📁 project1/
    ├── 📁 project2/
    └── 📁 project3/
```

---

## 🚀 Step 1: 개인 템플릿 저장소 구축

### 1️⃣ 템플릿 디렉토리 생성
```bash
# 홈 디렉토리에 개발 환경 폴더 생성
mkdir -p ~/dev_environment/templates/fastapi_template
mkdir -p ~/dev_environment/scripts
mkdir -p ~/dev_environment/configs
```

### 2️⃣ FastAPI 템플릿 생성
```bash
# FastAPI 템플릿 디렉토리로 이동
cd ~/dev_environment/templates/fastapi_template

# 템플릿 파일들 생성
mkdir .vscode tests app
```

---

## 📝 Step 2: 공통 설정 파일 생성

### 1️⃣ VS Code 설정 (`configs/vscode_settings.json`)
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
    "python.testing.unittestEnabled": false,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true,
        ".coverage": true,
        "htmlcov": true,
        ".mypy_cache": true
    },
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "python.analysis.autoImportCompletions": true,
    "python.analysis.typeCheckingMode": "basic"
}
```

### 2️⃣ pytest 설정 (`configs/pytest_template.ini`)
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
    api: API 테스트

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

### 3️⃣ Makefile 템플릿 (`configs/makefile_template`)
```makefile
.PHONY: help install test test-cov run dev clean format lint setup

help: ## 도움말 표시
	@echo "🚀 Python 프로젝트 개발 명령어"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## 의존성 설치
	pip install -r requirements.txt

install-dev: ## 개발 의존성 설치
	pip install -r requirements-dev.txt

test: ## 테스트 실행
	pytest

test-cov: ## 커버리지 포함 테스트
	pytest --cov=app --cov-report=html --cov-report=term

test-unit: ## 단위 테스트만 실행
	pytest -m unit

test-integration: ## 통합 테스트만 실행
	pytest -m integration

run: ## 애플리케이션 실행
	python main.py

dev: ## 개발 서버 실행 (자동 재시작)
	python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

format: ## 코드 포맷팅
	black .
	isort .

lint: ## 린팅 검사
	flake8 .
	mypy .

lint-fix: ## 린팅 오류 자동 수정
	black .
	isort .
	autoflake --remove-all-unused-imports --recursive --in-place .

clean: ## 캐시 및 임시 파일 정리
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf .mypy_cache

setup: ## 프로젝트 초기 설정
	python -m venv .venv
	.venv\Scripts\activate && pip install --upgrade pip
	pip install -r requirements.txt

setup-dev: ## 개발 환경 설정
	$(MAKE) setup
	pip install -r requirements-dev.txt
	$(MAKE) format
	$(MAKE) lint
```

### 4️⃣ .gitignore 템플릿 (`configs/gitignore_template`)
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
logs/
temp/
```

---

## 🤖 Step 3: 자동화 스크립트 생성

### 1️⃣ 프로젝트 생성 스크립트 (`scripts/create_project.py`)
```python
#!/usr/bin/env python3
"""
개인 프로젝트 생성 스크립트

사용법:
    python create_project.py <프로젝트명> [프로젝트타입]

프로젝트 타입:
    - fastapi (기본값)
    - django
    - flask
    - basic (기본 Python 프로젝트)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# 설정 경로
DEV_ENV_PATH = Path.home() / "dev_environment"
TEMPLATES_PATH = DEV_ENV_PATH / "templates"
CONFIGS_PATH = DEV_ENV_PATH / "configs"
PROJECTS_PATH = Path.home() / "projects"

def get_template_path(project_type):
    """프로젝트 타입에 따른 템플릿 경로 반환"""
    templates = {
        "fastapi": TEMPLATES_PATH / "fastapi_template",
        "django": TEMPLATES_PATH / "django_template",
        "flask": TEMPLATES_PATH / "flask_template",
        "basic": TEMPLATES_PATH / "basic_template"
    }
    return templates.get(project_type, templates["fastapi"])

def create_project(project_name, project_type="fastapi"):
    """새 프로젝트 생성"""

    # 프로젝트 디렉토리 생성
    project_path = PROJECTS_PATH / project_name
    if project_path.exists():
        print(f"❌ 프로젝트 '{project_name}'가 이미 존재합니다!")
        return False

    print(f"🚀 {project_name} ({project_type}) 프로젝트 생성 중...")

    # 프로젝트 디렉토리 생성
    project_path.mkdir(parents=True, exist_ok=True)

    # 가상환경 생성
    print("📦 가상환경 생성 중...")
    subprocess.run([sys.executable, "-m", "venv", ".venv"], cwd=project_path)

    # 템플릿 복사
    template_path = get_template_path(project_type)
    if template_path.exists():
        print(f"📋 템플릿 복사 중... ({project_type})")
        shutil.copytree(template_path, project_path, dirs_exist_ok=True)
    else:
        print(f"⚠️  템플릿을 찾을 수 없습니다: {template_path}")
        print("기본 구조를 생성합니다...")
        create_basic_structure(project_path, project_type)

    # 공통 설정 파일 복사
    copy_common_configs(project_path)

    # 가상환경 활성화 및 패키지 설치
    print("🔧 패키지 설치 중...")
    if project_type == "fastapi":
        install_fastapi_packages(project_path)
    elif project_type == "django":
        install_django_packages(project_path)
    elif project_type == "flask":
        install_flask_packages(project_path)
    else:
        install_basic_packages(project_path)

    print(f"\n✅ {project_name} 프로젝트 생성 완료!")
    print(f"📁 프로젝트 위치: {project_path}")
    print(f"\n🚀 다음 단계:")
    print(f"   1. cd {project_path}")
    print(f"   2. .venv\\Scripts\\activate (Windows) 또는 source .venv/bin/activate (Linux/Mac)")
    print(f"   3. make setup (또는 make install)")

    return True

def create_basic_structure(project_path, project_type):
    """기본 프로젝트 구조 생성"""

    # 디렉토리 생성
    dirs = ["app", "tests", ".vscode"]
    for dir_name in dirs:
        (project_path / dir_name).mkdir(exist_ok=True)

    # __init__.py 파일들 생성
    init_files = ["app/__init__.py", "tests/__init__.py"]
    for init_file in init_files:
        (project_path / init_file).write_text('"""Package initialization"""\n')

def copy_common_configs(project_path):
    """공통 설정 파일 복사"""

    configs = [
        ("vscode_settings.json", ".vscode/settings.json"),
        ("pytest_template.ini", "pytest.ini"),
        ("makefile_template", "Makefile"),
        ("gitignore_template", ".gitignore")
    ]

    for config_file, dest_path in configs:
        src = CONFIGS_PATH / config_file
        dst = project_path / dest_path

        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"  ✅ {dest_path} 복사 완료")

def install_fastapi_packages(project_path):
    """FastAPI 패키지 설치"""
    packages = [
        "fastapi", "uvicorn[standard]", "python-multipart",
        "pydantic", "pydantic-settings", "sqlalchemy",
        "python-dotenv", "psycopg2-binary", "orjson",
        "pytest", "pytest-asyncio", "pytest-cov", "httpx",
        "black", "flake8", "mypy", "isort", "autoflake"
    ]

    subprocess.run([
        project_path / ".venv" / "Scripts" / "pip.exe",
        "install"
    ] + packages, cwd=project_path)

def install_django_packages(project_path):
    """Django 패키지 설치"""
    packages = [
        "django", "djangorestframework", "django-cors-headers",
        "pytest", "pytest-django", "pytest-cov",
        "black", "flake8", "mypy", "isort"
    ]

    subprocess.run([
        project_path / ".venv" / "Scripts" / "pip.exe",
        "install"
    ] + packages, cwd=project_path)

def install_flask_packages(project_path):
    """Flask 패키지 설치"""
    packages = [
        "flask", "flask-sqlalchemy", "flask-migrate",
        "pytest", "pytest-cov", "httpx",
        "black", "flake8", "mypy", "isort"
    ]

    subprocess.run([
        project_path / ".venv" / "Scripts" / "pip.exe",
        "install"
    ] + packages, cwd=project_path)

def install_basic_packages(project_path):
    """기본 Python 패키지 설치"""
    packages = [
        "pytest", "pytest-cov",
        "black", "flake8", "mypy", "isort"
    ]

    subprocess.run([
        project_path / ".venv" / "Scripts" / "pip.exe",
        "install"
    ] + packages, cwd=project_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python create_project.py <프로젝트명> [프로젝트타입]")
        print("프로젝트 타입: fastapi, django, flask, basic")
        sys.exit(1)

    project_name = sys.argv[1]
    project_type = sys.argv[2] if len(sys.argv) > 2 else "fastapi"

    create_project(project_name, project_type)
```

### 2️⃣ 설정 동기화 스크립트 (`scripts/sync_settings.py`)
```python
#!/usr/bin/env python3
"""
기존 프로젝트들의 설정을 최신 템플릿으로 동기화

사용법:
    python sync_settings.py [프로젝트경로]
"""

import os
import sys
import shutil
from pathlib import Path

# 설정 경로
DEV_ENV_PATH = Path.home() / "dev_environment"
CONFIGS_PATH = DEV_ENV_PATH / "configs"

def sync_project_settings(project_path):
    """프로젝트 설정 동기화"""

    project_path = Path(project_path)
    if not project_path.exists():
        print(f"❌ 프로젝트 경로를 찾을 수 없습니다: {project_path}")
        return False

    print(f"🔄 {project_path.name} 설정 동기화 중...")

    # 백업 생성
    backup_path = project_path / "settings_backup"
    if not backup_path.exists():
        backup_path.mkdir()

        # 기존 설정 백업
        config_files = [".vscode/settings.json", "pytest.ini", "Makefile", ".gitignore"]
        for config_file in config_files:
            src = project_path / config_file
            if src.exists():
                shutil.copy2(src, backup_path / config_file.name)
        print("  📋 기존 설정 백업 완료")

    # 최신 설정 복사
    configs = [
        ("vscode_settings.json", ".vscode/settings.json"),
        ("pytest_template.ini", "pytest.ini"),
        ("makefile_template", "Makefile"),
        ("gitignore_template", ".gitignore")
    ]

    for config_file, dest_path in configs:
        src = CONFIGS_PATH / config_file
        dst = project_path / dest_path

        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"  ✅ {dest_path} 업데이트 완료")

    print(f"✅ {project_path.name} 설정 동기화 완료!")
    return True

def sync_all_projects():
    """모든 프로젝트 설정 동기화"""

    projects_path = Path.home() / "projects"
    if not projects_path.exists():
        print("❌ projects 디렉토리를 찾을 수 없습니다!")
        return False

    print("🔄 모든 프로젝트 설정 동기화 중...")

    for project_dir in projects_path.iterdir():
        if project_dir.is_dir() and (project_dir / ".venv").exists():
            sync_project_settings(project_dir)
            print()

    print("✅ 모든 프로젝트 설정 동기화 완료!")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 특정 프로젝트만 동기화
        project_path = sys.argv[1]
        sync_project_settings(project_path)
    else:
        # 모든 프로젝트 동기화
        sync_all_projects()
```

---

## 🛠️ Step 4: 사용법

### 1️⃣ 초기 설정
```bash
# 개발 환경 디렉토리 생성
mkdir -p ~/dev_environment/{templates,scripts,configs}

# 스크립트들을 실행 가능하게 만들기
chmod +x ~/dev_environment/scripts/*.py

# PATH에 스크립트 디렉토리 추가 (선택사항)
echo 'export PATH="$HOME/dev_environment/scripts:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 2️⃣ 새 프로젝트 생성
```bash
# FastAPI 프로젝트 생성
python ~/dev_environment/scripts/create_project.py my_fastapi_project fastapi

# Django 프로젝트 생성
python ~/dev_environment/scripts/create_project.py my_django_project django

# 기본 Python 프로젝트 생성
python ~/dev_environment/scripts/create_project.py my_basic_project basic
```

### 3️⃣ 기존 프로젝트 설정 동기화
```bash
# 특정 프로젝트만 동기화
python ~/dev_environment/scripts/sync_settings.py ~/projects/existing_project

# 모든 프로젝트 동기화
python ~/dev_environment/scripts/sync_settings.py
```

---

## 🎯 장점

### ✅ **일관성**
- 모든 프로젝트에서 동일한 개발 환경
- 동일한 도구와 설정 사용

### ✅ **효율성**
- 새 프로젝트 5분 안에 설정 완료
- 복사-붙여넣기 불필요

### ✅ **유지보수성**
- 중앙에서 설정 관리
- 한 번 업데이트하면 모든 프로젝트에 적용

### ✅ **확장성**
- 새로운 프레임워크 템플릿 쉽게 추가
- 개인 취향에 맞게 커스터마이징

---

## 📋 체크리스트

### 초기 설정
- [ ] `~/dev_environment/` 디렉토리 구조 생성
- [ ] 공통 설정 파일들 생성
- [ ] 자동화 스크립트 작성
- [ ] PATH 설정 (선택사항)

### 프로젝트 생성
- [ ] 템플릿 기반 프로젝트 생성
- [ ] 가상환경 자동 생성
- [ ] 패키지 자동 설치
- [ ] 설정 파일 자동 복사

### 유지보수
- [ ] 정기적인 설정 동기화
- [ ] 템플릿 업데이트
- [ ] 새로운 도구 추가

이제 **개인 로컬에서 모든 Python 프로젝트**를 일관되게 관리할 수 있습니다! 🎉
