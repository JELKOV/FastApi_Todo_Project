# 📚 프로젝트 문서 인덱스

## 🎯 빠른 참조 가이드

이 문서는 프로젝트의 모든 MD 문서들을 빠르게 찾고 참조할 수 있도록 정리한 인덱스입니다.

## 📋 문서별 요약

### 🏠 **메인 문서**
| 문서 | 목적 | 주요 내용 | 리팩토링 시점 |
|------|------|-----------|---------------|
| `README.md` | 프로젝트 전체 개요 | Clean Architecture, API 목록, 설치/실행 방법 | 프로젝트 초기 |
| `PROJECT_DOCUMENTATION_GUIDE.md` | 문서 가이드 | 모든 문서의 순서별 정리 및 활용법 | 문서 정리 시점 |

### 🔧 **환경 설정**
| 문서 | 목적 | 주요 내용 | 리팩토링 시점 |
|------|------|-----------|---------------|
| `DEVELOPMENT_SETUP.md` | 개발 환경 설정 | Python, 의존성, 데이터베이스 설정 | 프로젝트 초기 |
| `LOCAL_SETUP_GUIDE.md` | 로컬 개발 가이드 | 환경변수, DB 초기화, 서버 실행 | 프로젝트 초기 |
| `VIRTUAL_ENV_GUIDE.md` | 가상환경 관리 | venv 생성/활성화, 패키지 관리, VS Code 설정 | 환경 문제 해결 |
| `setup_global_vscode.md` | VS Code 설정 | Python 인터프리터, 확장프로그램, 디버깅 | IDE 설정 문제 |

### 🗄️ **데이터베이스**
| 문서 | 목적 | 주요 내용 | 리팩토링 시점 |
|------|------|-----------|---------------|
| `README_POSTGRESQL.md` | PostgreSQL 마이그레이션 | SQLite→PostgreSQL, Docker 설정, 연결 문제 해결 | DB 마이그레이션 |

### 🚀 **기능 구현**
| 문서 | 목적 | 주요 내용 | 리팩토링 시점 |
|------|------|-----------|---------------|
| `USER_API_REFACTORING_DOCUMENTATION.md` | User API 구현 | User 도메인, API 엔드포인트, 에러 처리 | User API 추가 |
| `JWT_BCRYPT_AUTHENTICATION_DOCUMENTATION.md` | JWT 인증 시스템 | JWT 토큰, bcrypt 해싱, 로그인/회원가입, 미들웨어 | 인증 시스템 추가 |
| `REDIS_OTP_REFACTORING_DOCUMENTATION.md` | Redis OTP 시스템 | Redis 클라이언트, OTP 서비스, 보안 강화 | OTP 시스템 추가 |

### 🧪 **테스트**
| 문서 | 목적 | 주요 내용 | 리팩토링 시점 |
|------|------|-----------|---------------|
| `PYTEST_TUTORIAL_PROGRESS.md` | Pytest 테스트 시스템 | Fixture, Mocking, 통합테스트, 인증 테스트 | 테스트 시스템 구축 |

## 🔍 상황별 문서 찾기

### 🆕 **새로운 개발자라면?**
1. `README.md` - 프로젝트 전체 이해
2. `DEVELOPMENT_SETUP.md` - 개발 환경 설정
3. `LOCAL_SETUP_GUIDE.md` - 로컬 실행 방법

### 🐛 **문제가 생겼다면?**

#### 환경 문제
- **가상환경 문제**: `VIRTUAL_ENV_GUIDE.md`
- **VS Code 문제**: `setup_global_vscode.md`
- **패키지 설치 문제**: `DEVELOPMENT_SETUP.md`

#### 데이터베이스 문제
- **PostgreSQL 연결 문제**: `README_POSTGRESQL.md`
- **데이터베이스 초기화**: `LOCAL_SETUP_GUIDE.md`

#### API 문제
- **User API**: `USER_API_REFACTORING_DOCUMENTATION.md`
- **인증 문제**: `JWT_BCRYPT_AUTHENTICATION_DOCUMENTATION.md`
- **OTP 문제**: `REDIS_OTP_REFACTORING_DOCUMENTATION.md`

#### 테스트 문제
- **테스트 실행 문제**: `PYTEST_TUTORIAL_PROGRESS.md`

### 🔧 **특정 기능을 구현하려면?**

#### 인증 시스템
- `JWT_BCRYPT_AUTHENTICATION_DOCUMENTATION.md` - JWT + bcrypt
- `REDIS_OTP_REFACTORING_DOCUMENTATION.md` - OTP 시스템

#### API 개발
- `USER_API_REFACTORING_DOCUMENTATION.md` - User API 구현 방법
- `README.md` - 전체 API 구조 이해

#### 테스트 작성
- `PYTEST_TUTORIAL_PROGRESS.md` - Pytest 활용법

## 📊 문서별 상세 정보

### 📖 **README.md**
- **크기**: 대형 (전체 프로젝트 설명)
- **업데이트 빈도**: 기능 추가 시마다
- **대상 독자**: 모든 개발자
- **핵심 내용**: 프로젝트 구조, API 목록, 설치/실행

### 🔧 **환경 설정 문서들**
- **크기**: 중형 (설정 방법 상세 설명)
- **업데이트 빈도**: 환경 변경 시
- **대상 독자**: 새로운 개발자, 환경 문제 해결자
- **핵심 내용**: 단계별 설정 방법, 문제 해결

### 🚀 **기능 구현 문서들**
- **크기**: 대형 (구현 과정 상세 기록)
- **업데이트 빈도**: 기능 변경 시
- **대상 독자**: 해당 기능 개발자, 코드 리뷰어
- **핵심 내용**: 설계 의도, 구현 과정, 코드 변경사항

### 🧪 **테스트 문서**
- **크기**: 중형 (테스트 작성 방법)
- **업데이트 빈도**: 테스트 추가/변경 시
- **대상 독자**: 테스트 작성자, QA
- **핵심 내용**: 테스트 전략, 작성 방법, 실행 방법

## 🎯 문서 활용 팁

### 📚 **문서 읽기 순서**
1. **전체 이해**: `README.md`
2. **환경 설정**: `DEVELOPMENT_SETUP.md` → `LOCAL_SETUP_GUIDE.md`
3. **기능 이해**: 각 기능별 리팩토링 문서
4. **문제 해결**: 상황에 맞는 문서 참조

### 🔍 **효율적인 문서 검색**
- **키워드 검색**: `Ctrl+F`로 원하는 키워드 검색
- **목차 활용**: 각 문서의 목차를 먼저 확인
- **코드 예시**: 실제 코드와 함께 설명된 부분 중점 확인

### 📝 **문서 업데이트 시**
- **변경사항 기록**: 무엇이 왜 변경되었는지 명시
- **코드 예시 업데이트**: 변경된 코드로 예시 갱신
- **문제 해결 추가**: 새로 발견된 문제와 해결책 기록

## 🎉 마무리

이 인덱스를 통해 프로젝트의 모든 문서를 효율적으로 활용할 수 있습니다. 각 문서는 특정 목적과 시점에 맞춰 작성되었으므로, 상황에 맞는 문서를 선택하여 참조하시기 바랍니다.

**문서의 목적:**
- 📖 **지식 전수**: 프로젝트 구조와 설계 의도 전달
- 🔧 **문제 해결**: 각종 설정 및 구현 문제 해결
- 🚀 **개발 지원**: 새로운 기능 개발 시 참고 자료
- 🧪 **품질 보장**: 테스트 작성 및 실행 가이드
