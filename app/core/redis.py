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
    """
    Redis 클라이언트 인스턴스를 제공하는 의존성 주입 함수
    
    FastAPI 라우트에서 Redis 클라이언트를 쉽게 사용할 수 있도록 합니다.
    
    Returns:
        redis.Redis: Redis 클라이언트 인스턴스
    """
    return redis_client


def test_redis_connection():
    """
    Redis 연결 테스트
    
    애플리케이션 시작 시 Redis 연결 상태를 확인합니다.
    """
    try:
        redis_client.ping()
        print("✅ Redis connected successfully!")
        return True
    except redis.exceptions.ConnectionError as e:
        print(f"❌ Could not connect to Redis: {e}")
        return False
    except Exception as e:
        print(f"❌ Redis connection error: {e}")
        return False


if __name__ == "__main__":
    test_redis_connection()
