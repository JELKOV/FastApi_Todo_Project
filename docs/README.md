# 📚 프로젝트 문서

이 디렉토리는 FastAPI TODO 프로젝트의 모든 문서를 체계적으로 정리한 곳입니다.

## 📁 디렉토리 구조

```
docs/
├── README.md                                    # 이 파일 (문서 개요)
├── TESTING_GUIDE.md                             # 🆕 완전한 테스트 가이드
├── TEST_COVERAGE_REPORT.md                      # 🆕 테스트 커버리지 리포트
├── REDIS_OTP_TESTING_GUIDE.md                  # 🆕 Redis OTP 테스트 가이드
├── PROJECT_DOCUMENTATION_GUIDE.md              # 리팩토링 순서별 문서 가이드
├── DOCUMENTATION_INDEX.md                      # 빠른 참조 인덱스
├── setup/                                       # 환경 설정 문서
│   ├── DEVELOPMENT_SETUP.md                    # 개발 환경 구축
│   ├── LOCAL_SETUP_GUIDE.md                    # 로컬 개발 환경 설정
│   ├── VIRTUAL_ENV_GUIDE.md                    # 가상환경 설정 가이드
│   ├── setup_global_vscode.md                  # VS Code 전역 설정
│   └── README_POSTGRESQL.md                    # PostgreSQL 마이그레이션 가이드
├── refactoring/                                 # 기능 구현 문서
│   ├── USER_API_REFACTORING_DOCUMENTATION.md   # 사용자 API 리팩토링
│   ├── JWT_BCRYPT_AUTHENTICATION_DOCUMENTATION.md # JWT + bcrypt 인증 시스템
│   └── REDIS_OTP_REFACTORING_DOCUMENTATION.md  # Redis OTP 인증 시스템
└── testing/                                     # 테스트 문서
    └── PYTEST_TUTORIAL_PROGRESS.md              # Pytest 튜토리얼 진행 상황
```

## 🎯 문서 활용 가이드

### 🆕 **새로운 개발자라면?**
1. **[PROJECT_DOCUMENTATION_GUIDE.md](PROJECT_DOCUMENTATION_GUIDE.md)** - 전체 문서 구조 이해
2. **[setup/DEVELOPMENT_SETUP.md](setup/DEVELOPMENT_SETUP.md)** - 개발 환경 설정
3. **[setup/LOCAL_SETUP_GUIDE.md](setup/LOCAL_SETUP_GUIDE.md)** - 로컬 실행 방법

### 🔍 **빠른 참조**
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - 상황별 문서 찾기
- **[PROJECT_DOCUMENTATION_GUIDE.md](PROJECT_DOCUMENTATION_GUIDE.md)** - 리팩토링 순서별 가이드

### 🐛 **문제 해결**

#### 환경 문제
- **가상환경**: [setup/VIRTUAL_ENV_GUIDE.md](setup/VIRTUAL_ENV_GUIDE.md)
- **VS Code**: [setup/setup_global_vscode.md](setup/setup_global_vscode.md)
- **PostgreSQL**: [setup/README_POSTGRESQL.md](setup/README_POSTGRESQL.md)

#### 기능 구현
- **User API**: [refactoring/USER_API_REFACTORING_DOCUMENTATION.md](refactoring/USER_API_REFACTORING_DOCUMENTATION.md)
- **인증 시스템**: [refactoring/JWT_BCRYPT_AUTHENTICATION_DOCUMENTATION.md](refactoring/JWT_BCRYPT_AUTHENTICATION_DOCUMENTATION.md)
- **OTP 시스템**: [refactoring/REDIS_OTP_REFACTORING_DOCUMENTATION.md](refactoring/REDIS_OTP_REFACTORING_DOCUMENTATION.md)

#### 테스트
- **Pytest**: [testing/PYTEST_TUTORIAL_PROGRESS.md](testing/PYTEST_TUTORIAL_PROGRESS.md)

## 📊 문서 카테고리별 설명

### 🔧 **setup/** - 환경 설정
개발 환경 구축에 필요한 모든 문서들입니다.
- 개발 환경 설정 방법
- 로컬 개발 환경 구축
- 가상환경 관리
- IDE 설정
- 데이터베이스 설정

### 🚀 **refactoring/** - 기능 구현
프로젝트의 주요 기능 구현 과정을 상세히 기록한 문서들입니다.
- User API 구현 과정
- JWT + bcrypt 인증 시스템
- Redis OTP 인증 시스템
- 각 기능의 설계 의도와 구현 과정

### 🧪 **테스트 문서**
테스트 시스템 구축 및 활용 방법을 다룬 문서들입니다.

#### 📖 **핵심 테스트 문서**
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - 완전한 테스트 가이드 (140개 테스트)
- **[TEST_COVERAGE_REPORT.md](TEST_COVERAGE_REPORT.md)** - 상세한 커버리지 분석
- **[REDIS_OTP_TESTING_GUIDE.md](REDIS_OTP_TESTING_GUIDE.md)** - Redis OTP 테스트 전용 가이드

#### 🎓 **테스트 학습 자료**
- **[testing/PYTEST_TUTORIAL_PROGRESS.md](testing/PYTEST_TUTORIAL_PROGRESS.md)** - Pytest 튜토리얼 진행 상황

#### 테스트 내용
- Pytest 설정 및 활용
- Fixture 사용법
- Mocking 테스트
- 통합 테스트 작성
- Redis OTP 인증 테스트
- 140개 포괄적 테스트 (100% 성공률)

## 🔄 리팩토링 순서

프로젝트의 리팩토링 과정을 시간순으로 정리하면:

1. **프로젝트 초기 설정** → `setup/` 문서들
2. **SQLite → PostgreSQL 마이그레이션** → `setup/README_POSTGRESQL.md`
3. **User API 구현** → `refactoring/USER_API_REFACTORING_DOCUMENTATION.md`
4. **JWT + bcrypt 인증 시스템** → `refactoring/JWT_BCRYPT_AUTHENTICATION_DOCUMENTATION.md`
5. **Pytest 테스트 시스템** → `testing/PYTEST_TUTORIAL_PROGRESS.md`
6. **Redis OTP 시스템** → `refactoring/REDIS_OTP_REFACTORING_DOCUMENTATION.md`

## 📝 문서 업데이트 가이드

### ✏️ **새로운 기능 추가 시**
1. `refactoring/` 디렉토리에 새로운 리팩토링 문서 생성
2. `PROJECT_DOCUMENTATION_GUIDE.md` 업데이트
3. `DOCUMENTATION_INDEX.md` 업데이트

### 🔄 **기존 기능 수정 시**
1. 해당 리팩토링 문서에 변경사항 기록
2. 영향받는 다른 문서들 업데이트

### 📚 **문서 작성 규칙**
- **목적 명확화**: 문서의 목적과 대상 독자 명시
- **단계별 설명**: 복잡한 과정은 단계별로 분해
- **코드 예시**: 실제 코드와 함께 설명
- **문제 해결**: 발생할 수 있는 문제와 해결책 포함

## 🎉 마무리

이 문서들은 프로젝트의 리팩토링 과정을 체계적으로 기록한 것입니다. 각 문서는 특정 시점의 변경사항과 그 이유를 명확히 설명하고 있어, 프로젝트의 진화 과정을 이해하는 데 도움이 됩니다.

**문서의 목적:**
- 📖 **지식 전수**: 프로젝트 구조와 설계 의도 전달
- 🔧 **문제 해결**: 각종 설정 및 구현 문제 해결
- 🚀 **개발 지원**: 새로운 기능 개발 시 참고 자료
- 🧪 **품질 보장**: 테스트 작성 및 실행 가이드

---

**Happy Coding! 🚀**
