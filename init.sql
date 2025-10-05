ㅇ-- PostgreSQL 초기 데이터베이스 설정 스크립트
-- 이 파일은 PostgreSQL 컨테이너가 처음 시작될 때 자동으로 실행됩니다.

-- 데이터베이스 생성 (이미 docker-compose.yml에서 생성됨)
-- CREATE DATABASE todo_db;

-- 사용자 권한 설정 (선택사항)
-- GRANT ALL PRIVILEGES ON DATABASE todo_db TO todo_user;

-- 추가 확장 모듈 설치 (필요시)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 테이블 생성은 FastAPI 애플리케이션에서 자동으로 처리됩니다.
-- SQLAlchemy의 Base.metadata.create_all()이 담당합니다.

-- 개발용 샘플 데이터 (선택사항)
-- INSERT INTO todos (title, description, completed, priority) VALUES
-- ('FastAPI 학습', 'FastAPI를 사용한 RESTful API 개발', false, 3),
-- ('PostgreSQL 설정', 'Docker로 PostgreSQL 환경 구성', true, 2),
-- ('코드 리팩토링', 'Clean Architecture 패턴 적용', false, 4);
