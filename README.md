# Todo RESTful API

FastAPI와 PostgreSQL을 사용한 완전한 TODO 관리 RESTful API입니다. Clean Architecture 패턴을 적용하여 확장 가능하고 유지보수가 용이한 구조로 설계되었습니다. **Background Tasks**를 통한 비동기 처리로 성능이 크게 향상되었습니다.

## 🏗️ 프로젝트 구조 (Clean Architecture)

```
todo_fastapi_be/
├── app/                          # 애플리케이션 메인 디렉토리
│   ├── main.py                   # FastAPI 애플리케이션 진입점
│   ├── core/                     # 핵심 설정
│   │   ├── database.py           # 데이터베이스 연결 설정
│   │   ├── auth.py               # JWT 인증 및 bcrypt 해싱
│   │   ├── email_service.py      # 이메일 전송 서비스
│   │   └── background_tasks.py   # 백그라운드 작업 함수들
│   ├── common/                   # 공통 모듈
│   │   ├── schemas.py            # 공통 Pydantic 스키마
│   │   ├── error_codes.py        # 에러 코드 및 메시지 관리
│   │   ├── exceptions.py         # 커스텀 예외 클래스
│   │   ├── exception_handlers.py # 전역 예외 핸들러
│   │   └── response_helpers.py   # 표준화된 응답 헬퍼
│   ├── todos/                    # TODO 도메인
│   │   ├── domain/               # 도메인 레이어
│   │   │   ├── entities.py       # Pydantic 모델 (요청/응답 스키마)
│   │   │   └── models.py         # SQLAlchemy ORM 모델
│   │   ├── application/          # 애플리케이션 레이어
│   │   │   └── services.py       # 비즈니스 로직
│   │   ├── infrastructure/       # 인프라 레이어
│   │   └── interfaces/           # 인터페이스 레이어
│   │       └── api/
│   │           └── controller.py # FastAPI 라우터 (API 엔드포인트)
│   └── users/                    # 사용자 도메인
│       ├── domain/               # 도메인 레이어
│       │   ├── entities.py       # Pydantic 모델 (요청/응답 스키마)
│       │   └── models.py         # SQLAlchemy ORM 모델
│       ├── application/          # 애플리케이션 레이어
│       │   └── services.py       # 비즈니스 로직
│       └── interfaces/           # 인터페이스 레이어
│           └── api/
│               └── controller.py # FastAPI 라우터 (API 엔드포인트)
├── tests/                        # 테스트 디렉토리
│   ├── conftest.py               # Pytest 설정 및 공통 픽스처
│   ├── unit/                     # 단위 테스트
│   │   ├── test_basic.py         # 기본 기능 테스트
│   │   ├── test_fixtures.py      # 픽스처 테스트
│   │   ├── test_mocking.py       # 모킹 테스트
│   │   ├── test_email_service.py # 이메일 서비스 테스트
│   │   └── test_background_tasks_functions.py # 백그라운드 작업 테스트
│   ├── integration/              # 통합 테스트
│   │   ├── test_get_todos.py     # TODO 목록 조회 테스트
│   │   ├── test_get_todo.py      # TODO 단일 조회 테스트
│   │   ├── test_post_todo.py     # TODO 생성 테스트
│   │   ├── test_patch_todo.py    # TODO 수정 테스트
│   │   ├── test_delete_todo.py   # TODO 삭제 테스트
│   │   ├── test_user_api_complete.py # 사용자 API 통합 테스트
│   │   ├── test_auth_api.py      # 인증 API 테스트
│   │   └── test_background_tasks.py # 백그라운드 작업 통합 테스트
│   └── scripts/                  # 실제 테스트 스크립트
│       └── background_tasks_real_test.py # 백그라운드 작업 실제 테스트
├── config.py                     # 애플리케이션 설정 관리
├── run.py                        # 개발 서버 실행 스크립트
├── requirements.txt              # Python 의존성
├── pytest.ini                   # Pytest 설정
├── Makefile                      # 개발 명령어 모음
├── docker-compose.yml           # PostgreSQL & pgAdmin 컨테이너 설정
├── .env                         # 환경 변수 (PostgreSQL 연결 정보)
├── activate.bat                 # Windows 가상환경 활성화 스크립트
├── activate.sh                  # Linux/Mac 가상환경 활성화 스크립트
└── README.md                    # 프로젝트 문서
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 가상환경 생성 및 활성화
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 의존성 설치
pip install -r requirements.txt

# 또는 Makefile 사용
make install
```

### 2. 데이터베이스 실행

```bash
# PostgreSQL 컨테이너 시작
docker-compose up -d postgres

# 컨테이너 상태 확인
docker ps

# 또는 Makefile 사용
make db-start
```

### 3. 애플리케이션 실행

```bash
# 개발 서버 시작
python run.py

# 또는 Makefile 사용
make run
```

서버가 http://localhost:8000 에서 실행됩니다.

### 4. 테스트 실행

```bash
# 전체 테스트 실행
python -m pytest tests/ -v

# 커버리지 포함 테스트
python -m pytest tests/ --cov=app --cov-report=html

# 또는 Makefile 사용
make test
make coverage
```

## 📚 API 문서

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 API 엔드포인트

### 기본 엔드포인트
- `GET /` - API 정보
- `GET /health` - 헬스 체크

### TODO 관리
- `GET /todos/` - TODO 목록 조회 (페이지네이션, 필터링, 정렬 지원)
- `POST /todos/` - 새 TODO 생성
- `GET /todos/{id}` - 특정 TODO 조회
- `PUT /todos/{id}` - TODO 수정
- `DELETE /todos/{id}` - TODO 삭제
- `PATCH /todos/{id}/toggle` - TODO 완료 상태 토글

### 사용자 관리 & 인증
- `POST /users/` - 새 사용자 생성
- `GET /users/` - 사용자 목록 조회 (페이지네이션 지원)
- `GET /users/{user_id}` - 특정 사용자 조회
- `PUT /users/{user_id}` - 사용자 정보 수정
- `PATCH /users/{user_id}` - 사용자 정보 부분 수정
- `DELETE /users/{user_id}` - 사용자 삭제
- `GET /users/username/{username}` - 사용자명으로 사용자 조회
- `GET /users/email/{email}` - 이메일로 사용자 조회
- `GET /users/me` - 현재 사용자 정보 조회 (JWT 인증 필요)

### OTP 인증 (Redis 기반)
- `POST /users/request-otp` - OTP 요청 (백그라운드 이메일 전송)
- `POST /users/verify-otp` - OTP 검증

### JWT 인증
- `POST /auth/login` - 사용자 로그인 (JWT 토큰 발급)
- `GET /auth/me` - 현재 사용자 정보 조회 (JWT 토큰 필요)

### 쿼리 파라미터 (GET /todos/)
- `page`: 페이지 번호 (기본값: 1)
- `size`: 페이지 크기 (기본값: 10)
- `completed`: 완료 상태 필터 (true/false)
- `priority`: 우선순위 필터 (1-5)
- `sort`: 정렬 기준 (created_at, updated_at, priority, title)
- `order`: 정렬 순서 (asc, desc)

### 쿼리 파라미터 (GET /users/)
- `page`: 페이지 번호 (기본값: 1)
- `size`: 페이지 크기 (기본값: 10)
- `sort`: 정렬 기준 (created_at, updated_at, username)
- `order`: 정렬 순서 (asc, desc)

## 🗄️ 데이터베이스 설정

### PostgreSQL 연결 정보
- **호스트**: localhost (127.0.0.1)
- **포트**: 5433
- **데이터베이스**: todo_db
- **사용자**: todo_user
- **비밀번호**: 1234

### pgAdmin 접근
- **URL**: http://localhost:5050
- **이메일**: admin@todo.com
- **비밀번호**: admin123

### 데이터베이스 스키마

#### Users 테이블
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Todos 테이블
```sql
CREATE TABLE todos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    priority INTEGER DEFAULT 1 CHECK (priority >= 1 AND priority <= 5),
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🏛️ Clean Architecture 구조

### 레이어별 책임

1. **Domain Layer** (`domain/`)
   - 비즈니스 로직의 핵심
   - 엔티티와 도메인 규칙 정의
   - 외부 의존성 없음

2. **Application Layer** (`application/`)
   - 유스케이스 구현
   - 도메인 로직 조합
   - 트랜잭션 관리

3. **Infrastructure Layer** (`infrastructure/`)
   - 외부 시스템과의 연동
   - 데이터베이스 구현
   - 외부 API 연동

4. **Interface Layer** (`interfaces/`)
   - 외부와의 통신
   - API 엔드포인트
   - 요청/응답 변환

### 공통 모듈 (`common/`)

- **schemas.py**: 공통 Pydantic 스키마 정의
- **error_codes.py**: 에러 코드 및 다국어 메시지 관리
- **exceptions.py**: 커스텀 예외 클래스
- **exception_handlers.py**: 전역 예외 핸들러
- **response_helpers.py**: 표준화된 HTTP 응답 헬퍼

## 🧪 테스트 구조

### 테스트 개요
이 프로젝트는 **183개의 포괄적인 테스트**를 포함하고 있으며, 다음과 같은 영역을 커버합니다:

- **인증 API**: 10개 테스트 (bcrypt, JWT)
- **TODO API**: 60개 테스트 (CRUD, 필터링, 페이징)
- **User API**: 20개 테스트 (CRUD, OTP)
- **Background Tasks**: 13개 테스트 (이메일 서비스, 백그라운드 작업)
- **단위 테스트**: 80개 테스트 (기본 기능, Fixture, Mocking, 이메일 서비스)

### 테스트 통계
- ✅ **성공률**: 99.5% (182/183) - 1개 테스트만 설정 관련 이슈
- ⚡ **실행 시간**: ~1분 18초
- 🚫 **경고**: 4개 (실제 테스트 스크립트 관련, 기능에는 영향 없음)
- 🎯 **커버리지**: 90%+

### 테스트 유형

1. **Unit Tests** (`tests/unit/`)
   - 개별 함수/메서드 테스트
   - 모킹을 통한 격리된 테스트
   - 픽스처 사용법 테스트
   - 이메일 서비스 테스트
   - 백그라운드 작업 함수 테스트

2. **Integration Tests** (`tests/integration/`)
   - API 엔드포인트 통합 테스트
   - 데이터베이스 연동 테스트
   - 전체 워크플로우 테스트
   - Redis OTP 인증 테스트
   - Background Tasks 통합 테스트

3. **Real Tests** (`tests/scripts/`)
   - 실제 서버와의 통신 테스트
   - 성능 측정 테스트
   - 백그라운드 작업 실제 동작 확인

### 테스트 실행

```bash
# 전체 테스트 실행
pytest

# 상세 출력으로 실행
pytest -v

# 특정 테스트 파일 실행
pytest tests/integration/test_post_todo.py -v

# OTP 테스트만 실행
pytest tests/integration/test_user_api_complete.py -k "otp" -v

# 커버리지 포함 실행
pytest --cov=app --cov-report=html

# 전체 테스트 (Makefile 사용)
make test

# 커버리지 리포트
make coverage
```

### 테스트 문서
- 📖 [테스트 가이드](docs/TESTING_GUIDE.md) - 완전한 테스트 가이드
- 📊 [테스트 커버리지 리포트](docs/TEST_COVERAGE_REPORT.md) - 상세한 커버리지 분석
- 🔐 [Redis OTP 테스트 가이드](docs/REDIS_OTP_TESTING_GUIDE.md) - OTP 테스트 전용 가이드
```

## 🐛 주요 에러 해결 가이드

### 1. PostgreSQL 연결 오류

#### 문제: `connection to server at "127.0.0.1", port 5432 failed`

**원인**: 포트 충돌 - 로컬 Windows PostgreSQL과 Docker PostgreSQL이 같은 5432 포트 사용

**해결방법**:
```bash
# 1. docker-compose.yml에서 포트 변경
ports:
  - "5433:5432"  # 5432 → 5433으로 변경

# 2. .env 파일 업데이트
DATABASE_URL=postgresql+psycopg2://todo_user:1234@127.0.0.1:5433/todo_db

# 3. 컨테이너 재시작
docker-compose down -v
docker-compose up -d
```

#### 문제: `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xb8`

**원인**: Windows 환경에서 .env 파일 인코딩 문제

**해결방법**:
```bash
# .env 파일을 UTF-8 (BOM 없음)로 재생성
@'
APP_NAME="Todo RESTful API (PostgreSQL)"
DATABASE_URL=postgresql+psycopg2://todo_user:1234@127.0.0.1:5433/todo_db
'@ | Out-File -FilePath .env -Encoding UTF8
```

### 2. Docker 관련 오류

#### 문제: `unable to get image 'postgres:15-alpine'`

**원인**: Docker Desktop이 실행되지 않음

**해결방법**:
1. Docker Desktop 시작
2. 컨테이너 상태 확인: `docker ps`

#### 문제: `POSTGRES_HOST_AUTH_METHOD has been set to "trust"`

**원인**: 개발용 trust 모드 경고 (정상 동작)

**해결방법**: 프로덕션 환경에서만 제거, 개발 환경에서는 무시 가능

### 3. FastAPI 관련 오류

#### 문제: `ModuleNotFoundError: No module named 'app'`

**원인**: Python 경로 문제

**해결방법**:
```bash
# 프로젝트 루트에서 실행
cd todo_fastapi_be
python run.py
```

#### 문제: `Port 8000 already in use`

**원인**: 다른 프로세스가 8000 포트 사용 중

**해결방법**:
```bash
# 포트 사용 프로세스 종료
taskkill /F /IM python.exe

# 또는 다른 포트 사용
# run.py에서 포트 변경
```

### 4. 의존성 관련 오류

#### 문제: `ERROR: Failed building wheel for psycopg2-binary`

**원인**: Windows에서 C++ 빌드 도구 부족

**해결방법**:
```bash
# Microsoft C++ Build Tools 설치 후
pip install psycopg2-binary==2.9.9
```

### 5. 테스트 관련 오류

#### 문제: `PydanticDeprecatedSince20: Pydantic V1 style @validator validators are deprecated`

**원인**: Pydantic V1 스타일 validator 사용

**해결방법**: `@validator`를 `@field_validator`로 변경하고 `@classmethod` 추가

#### 문제: `DeprecationWarning: 'HTTP_422_UNPROCESSABLE_ENTITY' is deprecated`

**원인**: FastAPI 상태 코드 변경

**해결방법**: `HTTP_422_UNPROCESSABLE_ENTITY`를 `HTTP_422_UNPROCESSABLE_CONTENT`로 변경

## 🔍 디버깅 도구

### 연결 테스트 스크립트
```bash
# PostgreSQL 직접 연결 테스트
python test_1234_password.py

# 컨테이너 내부 연결 테스트
docker exec todo_postgres psql -U todo_user -d todo_db -c "SELECT version();"
```

### 로그 확인
```bash
# PostgreSQL 컨테이너 로그
docker logs todo_postgres

# FastAPI 서버 로그
# 터미널에서 직접 확인
```

### 네트워크 상태 확인
```bash
# 포트 사용 상태 확인
netstat -ano | findstr :5433

# 컨테이너 상태 확인
docker ps
```

## 🛠️ 개발 환경 설정

### 환경 변수 (.env)
```env
APP_NAME="Todo RESTful API (PostgreSQL)"
APP_VERSION=1.0.0
DEBUG=True
DATABASE_URL=postgresql+psycopg2://todo_user:1234@127.0.0.1:5433/todo_db
HOST=0.0.0.0
PORT=8000
```

### 주요 의존성
- **FastAPI**: 웹 프레임워크
- **SQLAlchemy**: ORM
- **psycopg2-binary**: PostgreSQL 드라이버
- **Pydantic**: 데이터 검증
- **uvicorn**: ASGI 서버
- **pytest**: 테스트 프레임워크
- **pytest-asyncio**: 비동기 테스트 지원
- **httpx**: HTTP 클라이언트 (테스트용)
- **pytest-cov**: 커버리지 측정

### Makefile 명령어
```bash
make install      # 의존성 설치
make run          # 개발 서버 시작
make test         # 테스트 실행
make coverage     # 커버리지 리포트 생성
make lint         # 코드 린팅
make format       # 코드 포맷팅
make clean        # 임시 파일 정리
make db-start     # 데이터베이스 시작
make db-stop      # 데이터베이스 중지
```

## 📝 사용 예시

### TODO 생성
```bash
curl -X POST "http://localhost:8000/todos/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "새로운 작업",
    "description": "작업 설명",
    "priority": 3
  }'
```

### TODO 목록 조회
```bash
curl "http://localhost:8000/todos/?page=1&size=10&completed=false"
```

### TODO 완료 토글
```bash
curl -X PATCH "http://localhost:8000/todos/1/toggle"
```

### 사용자 생성
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

### 사용자 목록 조회
```bash
curl "http://localhost:8000/users/?page=1&size=10"
```

## 🎯 주요 특징

### 아키텍처 특징
- **Clean Architecture**: 도메인 중심의 계층화된 구조
- **Dependency Injection**: FastAPI Depends를 통한 의존성 주입
- **Repository Pattern**: 데이터 접근 계층 분리
- **Service Layer**: 비즈니스 로직 캡슐화

### API 특징
- **RESTful API**: 표준 HTTP 메서드 사용
- **표준화된 응답**: 일관된 응답 구조
- **에러 핸들링**: 상세한 에러 응답 및 코드
- **다국어 지원**: 한국어/영어 메시지
- **자동 문서화**: Swagger UI & ReDoc
- **Background Tasks**: 비동기 작업 처리로 성능 향상
- **JWT 인증**: 안전한 사용자 인증
- **OTP 인증**: Redis 기반 이메일 OTP 시스템

### 성능 특징
- **비동기 처리**: Background Tasks로 응답 시간 66.7% 향상
- **이메일 서비스**: 개발/프로덕션 모드 지원
- **사용자 활동 로깅**: 백그라운드에서 자동 로깅
- **알림 시스템**: TODO 완료 시 자동 알림

### 데이터베이스 특징
- **PostgreSQL**: 강력한 관계형 데이터베이스
- **SQLAlchemy ORM**: 타입 안전한 데이터베이스 접근
- **관계 설정**: Users와 Todos 간 외래키 관계
- **자동 타임스탬프**: 생성/수정 시간 자동 관리

### 테스트 특징
- **포괄적 테스트**: 단위/통합 테스트 모두 포함
- **모킹**: 외부 의존성 격리
- **픽스처**: 재사용 가능한 테스트 데이터
- **커버리지**: 코드 커버리지 측정

### 개발 도구
- **페이지네이션**: 대용량 데이터 처리
- **필터링 & 정렬**: 유연한 데이터 조회
- **타입 안전성**: Pydantic 모델 사용
- **개발 편의성**: Makefile, 스크립트 제공

## 📊 프로젝트 통계

- **총 테스트**: 183개 (182개 통과, 99.5% 성공률)
- **테스트 커버리지**: 90%+
- **API 엔드포인트**: TODO 6개 + 사용자 7개 + 인증 2개 + OTP 2개
- **데이터베이스 테이블**: 2개 (users, todos)
- **아키텍처 레이어**: 4개 (Domain, Application, Infrastructure, Interface)
- **Background Tasks**: 5개 함수 (이메일, 로깅, 알림, 정리, 분석)
- **성능 향상**: OTP 응답 시간 66.7% 개선 (6.114초 → 2.034초)

## 📞 지원

문제가 발생하면 다음 순서로 확인해보세요:

1. **포트 충돌 확인**: `netstat -ano | findstr :5433`
2. **컨테이너 상태 확인**: `docker ps`
3. **로그 확인**: `docker logs todo_postgres`
4. **연결 테스트**: `python test_1234_password.py`
5. **환경 변수 확인**: `.env` 파일 내용
6. **테스트 실행**: `make test`

## 📚 프로젝트 문서

모든 문서는 `docs/` 디렉토리에 체계적으로 정리되어 있습니다.

### 🎯 **문서 가이드**
- [📚 docs/PROJECT_DOCUMENTATION_GUIDE.md](docs/PROJECT_DOCUMENTATION_GUIDE.md) - **리팩토링 순서별 문서 정리**
- [📋 docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md) - **빠른 문서 참조 인덱스**

### 🔧 **환경 설정**
- [docs/setup/DEVELOPMENT_SETUP.md](docs/setup/DEVELOPMENT_SETUP.md) - 개발 환경 구축
- [docs/setup/LOCAL_SETUP_GUIDE.md](docs/setup/LOCAL_SETUP_GUIDE.md) - 로컬 개발 환경 설정
- [docs/setup/VIRTUAL_ENV_GUIDE.md](docs/setup/VIRTUAL_ENV_GUIDE.md) - 가상환경 설정 가이드
- [docs/setup/setup_global_vscode.md](docs/setup/setup_global_vscode.md) - VS Code 전역 설정

### 🗄️ **데이터베이스**
- [docs/setup/README_POSTGRESQL.md](docs/setup/README_POSTGRESQL.md) - PostgreSQL 마이그레이션 가이드

### 🚀 **기능 구현**
- [docs/refactoring/USER_API_REFACTORING_DOCUMENTATION.md](docs/refactoring/USER_API_REFACTORING_DOCUMENTATION.md) - 사용자 API 리팩토링 문서
- [docs/refactoring/JWT_BCRYPT_AUTHENTICATION_DOCUMENTATION.md](docs/refactoring/JWT_BCRYPT_AUTHENTICATION_DOCUMENTATION.md) - JWT + bcrypt 인증 시스템
- [docs/refactoring/REDIS_OTP_REFACTORING_DOCUMENTATION.md](docs/refactoring/REDIS_OTP_REFACTORING_DOCUMENTATION.md) - **Redis OTP 인증 시스템**
- [docs/FASTAPI_BACKGROUND_TASKS_GUIDE.md](docs/FASTAPI_BACKGROUND_TASKS_GUIDE.md) - **Background Tasks 구현 가이드**

### 🧪 **테스트**
- [docs/testing/PYTEST_TUTORIAL_PROGRESS.md](docs/testing/PYTEST_TUTORIAL_PROGRESS.md) - Pytest 튜토리얼 진행 상황

> 💡 **문서 전체 보기**: [docs/README.md](docs/README.md) - 문서 디렉토리 개요

---

**Happy Coding! 🚀**
