# Todo RESTful API

FastAPI와 PostgreSQL을 사용한 완전한 TODO 관리 RESTful API입니다.

## 🏗️ 프로젝트 구조 (Clean Architecture)

```
todo_fastapi_be/
├── app/                          # 애플리케이션 메인 디렉토리
│   ├── main.py                   # FastAPI 애플리케이션 진입점
│   ├── core/                     # 핵심 설정
│   │   └── database.py           # 데이터베이스 연결 설정
│   └── todos/                    # TODO 도메인
│       ├── domain/               # 도메인 레이어
│       │   ├── entities.py       # Pydantic 모델 (요청/응답 스키마)
│       │   └── models.py         # SQLAlchemy ORM 모델
│       ├── application/          # 애플리케이션 레이어
│       │   └── services.py       # 비즈니스 로직
│       ├── infrastructure/       # 인프라 레이어
│       └── interfaces/           # 인터페이스 레이어
│           └── api/
│               └── controller.py # FastAPI 라우터 (API 엔드포인트)
├── config.py                     # 애플리케이션 설정 관리
├── run.py                        # 개발 서버 실행 스크립트
├── requirements.txt              # Python 의존성
├── docker-compose.yml           # PostgreSQL & pgAdmin 컨테이너 설정
├── .env                         # 환경 변수 (PostgreSQL 연결 정보)
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
```

### 2. 데이터베이스 실행

```bash
# PostgreSQL 컨테이너 시작
docker-compose up -d postgres

# 컨테이너 상태 확인
docker ps
```

### 3. 애플리케이션 실행

```bash
# 개발 서버 시작
python run.py
```

서버가 http://localhost:8000 에서 실행됩니다.

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

### 쿼리 파라미터 (GET /todos/)
- `page`: 페이지 번호 (기본값: 1)
- `size`: 페이지 크기 (기본값: 10)
- `completed`: 완료 상태 필터 (true/false)
- `priority`: 우선순위 필터 (1-5)
- `sort`: 정렬 기준 (created_at, updated_at, priority, title)
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

## 🎯 주요 특징

- **Clean Architecture**: 도메인 중심의 계층화된 구조
- **RESTful API**: 표준 HTTP 메서드 사용
- **PostgreSQL**: 강력한 관계형 데이터베이스
- **자동 문서화**: Swagger UI & ReDoc
- **타입 안전성**: Pydantic 모델 사용
- **에러 핸들링**: 상세한 에러 응답
- **페이지네이션**: 대용량 데이터 처리
- **필터링 & 정렬**: 유연한 데이터 조회

## 📞 지원

문제가 발생하면 다음 순서로 확인해보세요:

1. **포트 충돌 확인**: `netstat -ano | findstr :5433`
2. **컨테이너 상태 확인**: `docker ps`
3. **로그 확인**: `docker logs todo_postgres`
4. **연결 테스트**: `python test_1234_password.py`
5. **환경 변수 확인**: `.env` 파일 내용

---

**Happy Coding! 🚀**
