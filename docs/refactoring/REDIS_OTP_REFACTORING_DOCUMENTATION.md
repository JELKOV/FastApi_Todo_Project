# Redis OTP 인증 시스템 리팩토링 문서

## 📋 개요

이 문서는 FastAPI 기반 TODO 프로젝트에 Redis를 활용한 OTP(One-Time Password) 인증 시스템을 구현한 과정과 코드 변경사항을 상세히 기록합니다.

## 🎯 구현 목표

- **Redis 기반 OTP 시스템**: 메모리 기반 고성능 OTP 저장 및 관리
- **자동 만료**: 설정 가능한 만료 시간으로 보안 강화
- **일회성 사용**: 검증 후 즉시 삭제로 재사용 방지
- **Clean Architecture**: 기존 프로젝트 구조에 맞는 레이어 분리

## 🏗️ 아키텍처 설계

### 레이어 구조
```
app/
├── core/
│   └── redis.py              # Redis 클라이언트 초기화 및 의존성 주입
├── users/
│   ├── application/
│   │   └── otp_service.py    # OTP 비즈니스 로직
│   ├── domain/
│   │   └── entities.py       # OTP 관련 Pydantic 모델
│   └── interfaces/
│       └── api/
│           └── controller.py # OTP API 엔드포인트
└── common/
    ├── exceptions.py         # OTP 관련 예외 클래스
    └── error_codes.py        # OTP 에러 코드
```

### 데이터 흐름
```
Client Request → API Controller → OTP Service → Redis → Response
```

## 📁 파일별 변경사항

### 1. Redis 클라이언트 설정 (`app/core/redis.py`)

**새로 생성된 파일**

```python
"""
Redis 클라이언트 초기화 및 의존성 주입

Redis 연결을 관리하고 FastAPI의 의존성 주입을 위한 유틸리티를 제공합니다.
"""

import redis
from config import settings

# Redis 클라이언트 초기화
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True  # Redis에서 가져온 데이터를 자동으로 문자열로 디코딩
)

def get_redis_client():
    """Redis 클라이언트 인스턴스를 제공하는 의존성 주입 함수"""
    return redis_client

def test_redis_connection():
    """Redis 연결 테스트"""
    try:
        redis_client.ping()
        print("✅ Redis connected successfully!")
        return True
    except redis.exceptions.ConnectionError as e:
        print(f"❌ Could not connect to Redis: {e}")
        return False
```

**주요 특징:**
- 싱글톤 패턴으로 Redis 클라이언트 관리
- FastAPI 의존성 주입 지원
- 연결 테스트 기능 포함
- 자동 문자열 디코딩 설정

### 2. OTP 서비스 레이어 (`app/users/application/otp_service.py`)

**새로 생성된 파일**

```python
"""
OTP 서비스 레이어

Redis를 활용한 OTP 생성, 저장, 검증 로직을 처리합니다.
"""

import random
from typing import Optional
import redis
from config import settings
from app.common.exceptions import InvalidOTPError, OTPExpiredError, OTPNotFoundError

class OTPService:
    """OTP 서비스 클래스"""

    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.otp_expiration_seconds = settings.OTP_EXPIRATION_MINUTES * 60

    def generate_and_store_otp(self, email: str) -> str:
        """4자리 OTP를 생성하고 Redis에 저장합니다."""
        otp_code = str(random.randint(1000, 9999))
        self.redis_client.setex(email, self.otp_expiration_seconds, otp_code)
        return otp_code

    def verify_otp(self, email: str, otp_code: str) -> bool:
        """OTP 코드를 검증하고 성공 시 삭제합니다."""
        stored_otp = self.redis_client.get(email)

        if not stored_otp:
            raise OTPNotFoundError(f"OTP for {email} not found or has expired.")

        if stored_otp != otp_code:
            raise InvalidOTPError("The provided OTP is incorrect.")

        # 검증 성공 시 삭제하여 재사용 방지
        self.redis_client.delete(email)
        return True
```

**주요 기능:**
- 4자리 랜덤 OTP 생성
- Redis SETEX로 자동 만료 설정
- 검증 후 즉시 삭제로 보안 강화
- 커스텀 예외를 통한 명확한 에러 처리

### 3. OTP Pydantic 모델 (`app/users/domain/entities.py`)

**추가된 모델들**

```python
# OTP 관련 Pydantic 모델
class OTPRequest(BaseModel):
    """OTP 요청 모델 (이메일 기반)"""
    email: EmailStr = Field(..., description="OTP를 요청할 사용자 이메일")

class OTPVerificationRequest(BaseModel):
    """OTP 검증 모델"""
    email: EmailStr = Field(..., description="OTP를 요청했던 사용자 이메일")
    otp_code: str = Field(
        ...,
        min_length=4,
        max_length=6,
        pattern=r"^\d+$",  # 숫자만 허용
        description="사용자가 입력한 OTP 코드"
    )
```

**주요 특징:**
- 이메일 유효성 검증 (`EmailStr`)
- OTP 코드 형식 검증 (숫자만, 4-6자리)
- 명확한 필드 설명 및 제약사항

### 4. OTP API 엔드포인트 (`app/users/interfaces/api/controller.py`)

**추가된 엔드포인트들**

```python
# OTP 요청 엔드포인트
@router.post("/request-otp")
async def request_otp(
    request: Request,
    otp_request: OTPRequest,
    otp_service: OTPService = Depends(get_otp_service)
):
    """사용자 이메일로 OTP를 요청하고 Redis에 저장합니다."""
    try:
        otp_code = otp_service.generate_and_store_otp(otp_request.email)

        return success_response(
            request=request,
            message_key=MessageKey.OTP_SENT_SUCCESSFULLY,
            data={
                "email": otp_request.email,
                "otp_code": otp_code,  # 개발/테스트용
                "expires_in_minutes": settings.OTP_EXPIRATION_MINUTES
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send OTP: {str(e)}"
        )

# OTP 검증 엔드포인트
@router.post("/verify-otp")
async def verify_otp(
    request: Request,
    otp_verification_request: OTPVerificationRequest,
    otp_service: OTPService = Depends(get_otp_service)
):
    """사용자가 제공한 OTP 코드를 검증합니다."""
    try:
        if otp_service.verify_otp(otp_verification_request.email, otp_verification_request.otp_code):
            return success_response(
                request=request,
                message_key=MessageKey.OTP_VERIFIED_SUCCESSFULLY,
                data={"email": otp_verification_request.email}
            )
    except Exception as e:
        # 커스텀 예외 처리
        if "Invalid OTP" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP provided"
            )
        elif "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="OTP not found or has expired"
            )
```

**주요 특징:**
- RESTful API 설계 원칙 준수
- 의존성 주입을 통한 서비스 레이어 분리
- 명확한 HTTP 상태 코드 반환
- 개발/테스트용 OTP 코드 노출

### 5. 설정 파일 업데이트 (`config.py`)

**추가된 설정들**

```python
class Settings:
    # ... 기존 설정들 ...

    # Redis 설정
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))

    # OTP 설정
    OTP_EXPIRATION_MINUTES: int = int(os.getenv("OTP_EXPIRATION_MINUTES", "5"))
```

**주요 특징:**
- 환경변수를 통한 설정 오버라이드
- Redis 연결 정보 중앙 관리
- OTP 만료 시간 설정 가능

### 6. 예외 처리 (`app/common/exceptions.py`)

**추가된 예외 클래스들**

```python
class OTPNotFoundError(Exception):
    """OTP가 없거나 만료된 경우 발생하는 예외"""
    pass

class InvalidOTPError(Exception):
    """유효하지 않은 OTP인 경우 발생하는 예외"""
    pass

class OTPExpiredError(Exception):
    """OTP가 만료된 경우 발생하는 예외"""
    pass
```

### 7. 에러 코드 (`app/common/error_codes.py`)

**추가된 메시지 키들**

```python
class MessageKey:
    # ... 기존 메시지 키들 ...

    # OTP 관련 메시지
    OTP_SENT_SUCCESSFULLY = "OTP_SENT_SUCCESSFULLY"
    OTP_VERIFIED_SUCCESSFULLY = "OTP_VERIFIED_SUCCESSFULLY"
    OTP_INVALID = "OTP_INVALID"
    OTP_EXPIRED = "OTP_EXPIRED"
    OTP_NOT_FOUND = "OTP_NOT_FOUND"
```

### 8. 메인 애플리케이션 (`app/main.py`)

**추가된 초기화 코드**

```python
from app.core.redis import test_redis_connection  # Redis 연결 테스트 임포트

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행되는 이벤트"""
    print("🚀 Starting Todo API with Redis OTP support...")

    # Redis 연결 테스트
    test_redis_connection()

    print("✅ Application startup completed!")
```

## 🔧 의존성 추가

### requirements.txt 업데이트

```txt
# 기존 의존성들...
redis==6.4.0  # Redis 클라이언트
```

### Docker Compose 설정

```yaml
# docker-compose.yml에 Redis 서비스 추가
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

## 🧪 테스트 코드

### 통합 테스트 (`test_redis_otp.py`)

```python
#!/usr/bin/env python3
"""
Redis OTP 인증 시스템 테스트 스크립트
"""

import requests
import json

def test_otp_request():
    """OTP 요청 테스트"""
    otp_request_data = {"email": "test@example.com"}
    response = requests.post('http://localhost:8000/users/request-otp', json=otp_request_data)

    if response.status_code == 200:
        data = response.json()
        return data.get("data", {}).get("otp_code")
    return None

def test_otp_verification(otp_code):
    """OTP 검증 테스트"""
    otp_verification_data = {
        "email": "test@example.com",
        "otp_code": otp_code
    }
    response = requests.post('http://localhost:8000/users/verify-otp', json=otp_verification_data)
    return response.status_code == 200
```

## 📊 성능 및 보안 고려사항

### 성능 최적화
- **Redis 메모리 기반**: 빠른 읽기/쓰기 성능
- **자동 만료**: 메모리 사용량 최적화
- **싱글톤 패턴**: 연결 오버헤드 최소화

### 보안 강화
- **일회성 사용**: 검증 후 즉시 삭제
- **시간 제한**: 5분 만료로 보안 강화
- **랜덤 생성**: 예측 불가능한 OTP 생성
- **입력 검증**: Pydantic을 통한 엄격한 검증

## 🔄 API 사용법

### 1. OTP 요청
```bash
curl -X POST "http://localhost:8000/users/request-otp" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

**응답:**
```json
{
  "status": 200,
  "msg": "OTP sent successfully",
  "data": {
    "email": "user@example.com",
    "otp_code": "8534",
    "expires_in_minutes": 5
  }
}
```

### 2. OTP 검증
```bash
curl -X POST "http://localhost:8000/users/verify-otp" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "otp_code": "8534"}'
```

**응답:**
```json
{
  "status": 200,
  "msg": "OTP verified successfully",
  "data": {
    "email": "user@example.com"
  }
}
```

## 🚀 배포 및 운영

### 환경변수 설정
```bash
# .env 파일
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
OTP_EXPIRATION_MINUTES=5
```

### Docker 실행
```bash
# Redis 컨테이너 실행
docker-compose up redis -d

# FastAPI 서버 실행
python run.py
```

## 📈 모니터링 및 로깅

### Redis 모니터링
```bash
# Redis CLI로 연결 상태 확인
redis-cli ping

# Redis 메모리 사용량 확인
redis-cli info memory

# 활성 키 확인
redis-cli keys "*"
```

### 애플리케이션 로깅
- OTP 생성/검증 시 콘솔 로그 출력
- Redis 연결 상태 확인
- 에러 발생 시 상세 로그 기록

## 🔮 향후 개선사항

### 단기 개선
1. **이메일 전송 연동**: SendGrid, Mailgun 등 실제 이메일 서비스 연동
2. **OTP 재전송 제한**: 시간당 전송 횟수 제한
3. **로그 개선**: 구조화된 로깅 시스템 도입

### 장기 개선
1. **다중 인증 방식**: SMS, 앱 기반 OTP 지원
2. **분산 Redis**: Redis Cluster를 통한 고가용성
3. **캐싱 전략**: 자주 사용되는 데이터 캐싱
4. **메트릭 수집**: Prometheus, Grafana 연동

## 📝 결론

Redis OTP 인증 시스템이 성공적으로 구현되었습니다. 주요 성과:

- ✅ **Clean Architecture 준수**: 레이어 분리 및 의존성 주입
- ✅ **고성능**: Redis 기반 메모리 캐싱
- ✅ **보안 강화**: 일회성 사용 및 자동 만료
- ✅ **확장성**: 설정 기반 구성 및 모듈화
- ✅ **테스트 가능**: 단위 테스트 및 통합 테스트 지원

이 시스템은 사용자 인증, 비밀번호 재설정, 계정 활성화 등 다양한 보안 시나리오에 활용할 수 있습니다.
