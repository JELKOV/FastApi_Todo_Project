.PHONY: help install test test-cov run dev clean format lint

help: ## 도움말 표시
	@echo "🚀 Todo FastAPI Backend 개발 명령어"
	@echo ""
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

setup: ## 초기 설정
	python -m venv .venv
	.venv\Scripts\activate && pip install -r requirements.txt
	@echo "✅ 초기 설정 완료! activate.bat을 실행하여 가상환경을 활성화하세요."
