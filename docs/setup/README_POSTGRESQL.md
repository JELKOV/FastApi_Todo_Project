# PostgreSQL 설정 가이드

PostgreSQL 데이터베이스 설정 및 연결 가이드입니다.

## Docker를 사용한 PostgreSQL 설정

### 1. 컨테이너 실행
```bash
docker-compose up -d postgres
```

### 2. 연결 정보
- **호스트**: localhost (127.0.0.1)
- **포트**: 5433
- **데이터베이스**: todo_db
- **사용자**: todo_user
- **비밀번호**: 1234

### 3. pgAdmin 접근
- **URL**: http://localhost:5050
- **이메일**: admin@todo.com
- **비밀번호**: admin123

## 로컬 PostgreSQL 설정

### 1. PostgreSQL 설치
Windows에서 PostgreSQL을 직접 설치하는 경우:

1. PostgreSQL 공식 사이트에서 설치 파일 다운로드
2. 설치 과정에서 비밀번호 설정
3. 포트는 5432로 설정 (Docker와 충돌 방지)

### 2. 데이터베이스 및 사용자 생성
```sql
-- PostgreSQL에 연결 후 실행
CREATE DATABASE todo_db;
CREATE USER todo_user WITH PASSWORD '1234';
GRANT ALL PRIVILEGES ON DATABASE todo_db TO todo_user;
```

## 문제 해결

### 포트 충돌 문제
로컬 PostgreSQL과 Docker PostgreSQL이 같은 포트를 사용할 경우:
- Docker: 포트 5433 사용
- 로컬: 포트 5432 사용 (기본값)

### 연결 테스트
```bash
# Docker PostgreSQL 테스트
psql -h 127.0.0.1 -p 5433 -U todo_user -d todo_db

# 로컬 PostgreSQL 테스트
psql -h 127.0.0.1 -p 5432 -U todo_user -d todo_db
```
