# 🔐 JWT & bcrypt 인증 시스템 리팩토링 문서

## 📋 목차
1. [개요](#개요)
2. [아키텍처 변경사항](#아키텍처-변경사항)
3. [핵심 구현 내용](#핵심-구현-내용)
4. [보안 기능](#보안-기능)
5. [API 엔드포인트](#api-엔드포인트)
6. [설정 및 의존성](#설정-및-의존성)
7. [데이터베이스 스키마](#데이터베이스-스키마)
8. [사용법](#사용법)
9. [테스트](#테스트)
10. [마이그레이션 과정](#마이그레이션-과정)
11. [성능 및 보안 고려사항](#성능-및-보안-고려사항)

---

## 📖 개요

기존 TODO API에 JWT(JSON Web Token) 기반 인증과 bcrypt 비밀번호 해시화 시스템을 추가하여 엔터프라이즈급 보안을 구현했습니다.

### 주요 개선사항
- ✅ **JWT 토큰 인증**: Stateless 인증 시스템
- ✅ **bcrypt 비밀번호 해시**: 안전한 비밀번호 저장
- ✅ **사용자 관리**: 완전한 사용자 CRUD 시스템
- ✅ **권한 기반 접근**: 인증된 사용자만 TODO 생성 가능
- ✅ **API 보안 강화**: Bearer 토큰 기반 인증

---

## 🏗️ 아키텍처 변경사항

### 새로운 모듈 구조
```
app/
├── core/
│   ├── auth.py          # 🆕 JWT 인증 유틸리티
│   └── database.py      # 기존 데이터베이스 연결
├── users/               # 🆕 사용자 관리 도메인
│   ├── domain/
│   │   ├── entities.py  # Pydantic 모델 (UserCreate, UserResponse, etc.)
│   │   └── models.py    # SQLAlchemy ORM 모델 (User)
│   ├── application/
│   │   └── services.py  # 비즈니스 로직 (UserService)
│   └── interfaces/
│       └── api/
│           └── controller.py # REST API 엔드포인트
└── todos/               # 기존 TODO 도메인 (수정됨)
    └── interfaces/api/controller.py # 인증 의존성 추가
```

### Clean Architecture 적용
- **Domain Layer**: User 엔티티 및 비즈니스 규칙
- **Application Layer**: 사용자 관리 서비스 로직
- **Infrastructure Layer**: 데이터베이스 및 외부 시스템
- **Interface Layer**: REST API 컨트롤러

---

## 🔧 핵심 구현 내용

### 1. JWT 인증 시스템 (`app/core/auth.py`)

#### 주요 함수들
```python
# JWT 토큰 생성
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str

# JWT 토큰 검증
def verify_token(token: str) -> Optional[str]

# 사용자 인증 (bcrypt 검증 포함)
def authenticate_user(db: Session, username: str, password: str) -> Union[User, bool]

# 현재 인증된 사용자 조회
def get_current_user(credentials: HTTPAuthorizationCredentials, db: Session) -> User
```

#### 핵심 코드 예시
```python
# bcrypt 비밀번호 해시화 컨텍스트
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 토큰 생성
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# 사용자 인증 (bcrypt 검증 포함)
def authenticate_user(db: Session, username: str, password: str) -> Union[User, bool]:
    user_service = UserService(db)
    user = user_service.get_user_by_username_orm(username)
    if not user:
        return False

    # bcrypt를 사용한 비밀번호 검증
    if not user_service.verify_password(password, user.password):
        return False

    return user
```

### 2. User 도메인 모델

#### SQLAlchemy ORM 모델 (`app/users/domain/models.py`)
```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=True, unique=True)
    password = Column(String(512), nullable=False)  # bcrypt 해시 저장
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

#### Pydantic 엔티티 (`app/users/domain/entities.py`)
```python
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[str] = Field(None, max_length=100)
    password: str = Field(..., min_length=8, max_length=100)

class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    created_at: datetime
    updated_at: datetime
    # password 필드는 응답에서 제외 (보안)

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
```

### 3. User 서비스 레이어 (`app/users/application/services.py`)

#### bcrypt 비밀번호 처리
```python
class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def _hash_password(self, password: str) -> str:
        """bcrypt로 비밀번호 해시화"""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """bcrypt로 비밀번호 검증"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_user(self, user_data: UserCreate) -> UserResponse:
        """사용자 생성 (비밀번호 자동 해시화)"""
        hashed_password = self._hash_password(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            password=hashed_password
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return UserResponse.model_validate(user)
```

---

## 🔒 보안 기능

### 1. bcrypt 비밀번호 해시화
- **Salt 자동 생성**: 각 비밀번호마다 고유한 salt
- **Adaptive hashing**: 시간이 지나도 보안 강도 유지
- **CPU 집약적**: 브루트포스 공격 방지
- **기본 라운드**: 12라운드 (권장값)

### 2. JWT 토큰 인증
- **Stateless**: 서버 세션 불필요
- **만료 시간**: 30분 기본 설정 (설정 가능)
- **Bearer 토큰**: HTTP Authorization 헤더 사용
- **HMAC-SHA256**: 안전한 서명 알고리즘

### 3. API 보안
- **인증 필수**: TODO 생성 시 JWT 토큰 필요
- **사용자 연결**: TODO와 사용자 연결 (user_id)
- **권한 분리**: 사용자별 데이터 격리
- **HTTPS 권장**: 프로덕션 환경에서 필수

---

## 🌐 API 엔드포인트

### 사용자 관리 API

#### 1. 사용자 등록
```http
POST /users/
Content-Type: application/json

{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
}
```

#### 2. 사용자 로그인
```http
POST /users/login
Content-Type: application/json

{
    "username": "testuser",
    "password": "password123"
}

Response:
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 1800
}
```

#### 3. 현재 사용자 정보 조회
```http
GET /users/me
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

#### 4. 사용자 목록 조회
```http
GET /users/?skip=0&limit=100
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### 보안 강화된 TODO API

#### 인증된 TODO 생성
```http
POST /todos/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json

{
    "title": "보안된 TODO",
    "description": "JWT 인증이 필요한 TODO",
    "priority": 3,
    "completed": false
}
```

---

## ⚙️ 설정 및 의존성

### 환경 변수 설정 (`config.py`)
```python
class Settings:
    # JWT 설정
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
```

### 새로운 의존성 (`requirements.txt`)
```txt
# 비밀번호 해시화 및 인증
passlib[bcrypt]              # bcrypt 해시화 라이브러리
python-jose[cryptography]    # JWT 토큰 처리 라이브러리
```

### 환경 변수 파일 (`.env`)
```env
# JWT 설정
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 데이터베이스 설정
DATABASE_URL=sqlite:///./todos.db
```

---

## 🗄️ 데이터베이스 스키마

### 새로운 users 테이블
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    password VARCHAR(512) NOT NULL,  -- bcrypt 해시 (예: $2b$12$...)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX ix_users_id ON users (id);
CREATE UNIQUE INDEX ix_users_username ON users (username);
CREATE UNIQUE INDEX ix_users_email ON users (email);
```

### 기존 todos 테이블 수정
```sql
-- user_id 컬럼 추가
ALTER TABLE todos ADD COLUMN user_id INTEGER;

-- 외래 키 제약 추가 (SQLite는 제한적 지원)
-- PostgreSQL에서는: ALTER TABLE todos ADD CONSTRAINT fk_todos_user_id FOREIGN KEY (user_id) REFERENCES users(id);
```

### 테이블 관계
```
users (1) ----< todos (N)
  |                |
  id            user_id
```

---

## 🚀 사용법

### 1. 서버 시작
```bash
# 가상환경 활성화
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 서버 시작
python run.py
```

### 2. 사용자 등록
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 3. 로그인 및 토큰 획득
```bash
curl -X POST "http://localhost:8000/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'

# 응답 예시:
# {
#   "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
#   "token_type": "bearer",
#   "expires_in": 1800
# }
```

### 4. 인증된 TODO 생성
```bash
curl -X POST "http://localhost:8000/todos/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "title": "보안된 TODO",
    "description": "JWT 인증이 필요한 TODO",
    "priority": 3
  }'
```

### 5. 현재 사용자 정보 조회
```bash
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

---

## 🧪 테스트

### 1. 인증 테스트 스크립트 실행
```bash
# 서버가 실행 중인 상태에서
python tests/scripts/test_auth_api_manual.py
```

### 2. pytest 테스트 실행
```bash
# 전체 테스트 실행
python -m pytest tests/ -v

# 인증 관련 테스트만 실행
python -m pytest tests/integration/test_auth_api.py -v

# 커버리지 포함 테스트
python -m pytest tests/ --cov=app --cov-report=html
```

### 3. 테스트 시나리오
```python
def test_complete_auth_flow():
    """완전한 인증 플로우 테스트"""
    # 1. 사용자 등록
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword123'
    }
    response = requests.post('http://localhost:8000/users/', json=user_data)
    assert response.status_code == 201

    # 2. 로그인
    login_data = {
        'username': 'testuser',
        'password': 'testpassword123'
    }
    response = requests.post('http://localhost:8000/users/login', json=login_data)
    assert response.status_code == 200
    token = response.json()['access_token']

    # 3. 인증된 요청
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get('http://localhost:8000/users/me', headers=headers)
    assert response.status_code == 200

    # 4. 인증된 TODO 생성
    todo_data = {
        'title': '보안된 TODO',
        'priority': 3
    }
    response = requests.post('http://localhost:8000/todos/', json=todo_data, headers=headers)
    assert response.status_code == 201
```

---

## 🔄 마이그레이션 과정

### 1. 기존 시스템 영향 분석
- ✅ **기존 TODO API**: 대부분 호환성 유지
- ⚠️ **TODO 생성**: 이제 JWT 인증 필요
- ✅ **데이터베이스**: 기존 데이터 보존
- ✅ **API 응답 형식**: 기존 형식 유지

### 2. 점진적 적용 전략
```
1단계: 사용자 시스템 추가
├── User 도메인 모델 생성
├── User 서비스 레이어 구현
├── User API 엔드포인트 추가
└── 데이터베이스 테이블 생성

2단계: JWT 인증 구현
├── JWT 유틸리티 함수 구현
├── bcrypt 비밀번호 해시화
├── 인증 미들웨어 추가
└── 로그인 API 구현

3단계: TODO API 보안 강화
├── TODO 생성 시 인증 필수
├── user_id 자동 할당
├── 기존 API 호환성 유지
└── 에러 핸들링 개선

4단계: 테스트 및 검증
├── 단위 테스트 작성
├── 통합 테스트 작성
├── 인증 플로우 테스트
└── 보안 테스트
```

### 3. 백워드 호환성
- **기존 클라이언트**: 인증이 필요한 엔드포인트만 영향
- **데이터 마이그레이션**: 자동으로 처리됨
- **API 버전**: 기존 버전 유지 가능

---

## 📈 성능 및 보안 고려사항

### 1. 성능 최적화
```python
# 인덱스 최적화
CREATE INDEX ix_users_username ON users (username);
CREATE INDEX ix_todos_user_id ON todos (user_id);

# JWT 검증 최적화
- 토큰 파싱: O(1) 시간 복잡도
- 서명 검증: HMAC-SHA256 (빠른 검증)
- 만료 시간 검사: 로컬 시간 비교

# bcrypt 성능 고려사항
- 해시 생성: ~100ms (12라운드)
- 해시 검증: ~100ms (12라운드)
- 비동기 처리 고려 필요
```

### 2. 보안 강화 방안
```python
# 프로덕션 환경 설정
SECRET_KEY = "강력한-랜덤-시크릿-키"  # 최소 32자
ACCESS_TOKEN_EXPIRE_MINUTES = 15      # 짧은 만료 시간
ALGORITHM = "HS256"                   # 안전한 알고리즘

# 추가 보안 고려사항
- HTTPS 사용 (프로덕션)
- CORS 설정 적절히 구성
- Rate Limiting 구현
- 토큰 갱신 메커니즘
- 로그아웃 시 토큰 무효화
```

### 3. 모니터링 및 로깅
```python
# 보안 이벤트 로깅
- 로그인 시도 (성공/실패)
- 토큰 검증 실패
- 권한 없는 접근 시도
- 비정상적인 API 사용 패턴

# 성능 메트릭
- JWT 토큰 생성/검증 시간
- bcrypt 해시 생성/검증 시간
- API 응답 시간
- 데이터베이스 쿼리 성능
```

---

## 🔧 문제 해결

### 1. 일반적인 문제들

#### JWT 토큰 관련
```python
# 문제: "Could not validate credentials"
# 해결: 토큰 형식 확인
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...

# 문제: "Token has expired"
# 해결: 토큰 재발급 필요
response = requests.post('/users/login', json=login_data)
```

#### bcrypt 관련
```python
# 문제: "Invalid password"
# 해결: 비밀번호 해시 방식 확인
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### 2. 디버깅 팁
```python
# JWT 토큰 디코딩 (개발용)
import jwt
token = "your-jwt-token"
payload = jwt.decode(token, options={"verify_signature": False})
print(payload)

# bcrypt 해시 확인
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
is_valid = pwd_context.verify("password", "$2b$12$...")
print(f"Password valid: {is_valid}")
```

---

## 📚 참고 자료

### 라이브러리 문서
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [python-jose](https://python-jose.readthedocs.io/)
- [passlib](https://passlib.readthedocs.io/)
- [bcrypt](https://github.com/pyca/bcrypt/)

### 보안 가이드라인
- [OWASP JWT Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

### 관련 표준
- [RFC 7519 - JSON Web Token (JWT)](https://tools.ietf.org/html/rfc7519)
- [RFC 7518 - JSON Web Algorithms (JWA)](https://tools.ietf.org/html/rfc7518)

---

## 🎯 결론

JWT와 bcrypt를 활용한 인증 시스템 리팩토링을 통해 다음과 같은 이점을 얻었습니다:

### ✅ 달성한 목표
- **보안 강화**: 안전한 비밀번호 저장 및 인증
- **확장성**: Stateless 인증으로 서버 확장 용이
- **표준 준수**: JWT 표준을 따른 안전한 토큰 인증
- **사용자 경험**: 간편한 로그인 및 API 사용

### 🚀 향후 개선 방향
- **토큰 갱신**: Refresh Token 구현
- **권한 관리**: Role-based Access Control (RBAC)
- **다중 인증**: OAuth 2.0, SAML 지원
- **모니터링**: 보안 이벤트 실시간 모니터링

이 문서를 통해 JWT와 bcrypt 기반 인증 시스템의 구현과 사용법을 완전히 이해할 수 있습니다. 🎉
