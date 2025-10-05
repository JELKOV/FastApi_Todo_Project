#!/usr/bin/env python3
"""
FastAPI 프로젝트 템플릿 생성기

이 스크립트는 새로운 FastAPI 프로젝트를 빠르게 설정하기 위한 템플릿을 생성합니다.
사용법: python project_template.py <프로젝트명>
"""

import os
import sys
import subprocess
from pathlib import Path

def create_project_template(project_name: str):
    """새로운 FastAPI 프로젝트 템플릿 생성"""

    # 프로젝트 디렉토리 생성
    project_dir = Path(project_name)
    project_dir.mkdir(exist_ok=True)

    # 가상환경 생성
    print(f"🔧 {project_name} 가상환경 생성 중...")
    subprocess.run([sys.executable, "-m", "venv", ".venv"], cwd=project_dir)

    # 템플릿 파일들 복사
    template_files = [
        ".vscode/settings.json",
        "pytest.ini",
        "Makefile",
        "activate.bat",
        "activate.sh",
        ".gitignore",
        "requirements.txt"
    ]

    for file_path in template_files:
        src = Path(file_path)
        dst = project_dir / file_path

        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(src.read_text())
            print(f"✅ {file_path} 복사 완료")

    # 기본 앱 구조 생성
    app_dir = project_dir / "app"
    app_dir.mkdir(exist_ok=True)

    # __init__.py 파일들 생성
    init_files = [
        "app/__init__.py",
        "app/core/__init__.py",
        "app/common/__init__.py",
        "tests/__init__.py"
    ]

    for init_file in init_files:
        file_path = project_dir / init_file
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text('"""Package initialization"""\n')

    print(f"\n🎉 {project_name} 프로젝트 템플릿 생성 완료!")
    print(f"📁 프로젝트 위치: {project_dir.absolute()}")
    print(f"\n🚀 다음 단계:")
    print(f"   1. cd {project_name}")
    print(f"   2. activate.bat (Windows) 또는 ./activate.sh (Linux/Mac)")
    print(f"   3. pip install -r requirements.txt")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("사용법: python project_template.py <프로젝트명>")
        sys.exit(1)

    project_name = sys.argv[1]
    create_project_template(project_name)
