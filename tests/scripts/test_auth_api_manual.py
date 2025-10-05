#!/usr/bin/env python3
"""
bcrypt와 JWT 인증 API 테스트 스크립트
"""

import requests
import json
import time

def test_user_registration():
    """사용자 등록 테스트"""
    print("=== 사용자 등록 테스트 ===")
    user_data = {
        'username': f'testuser{int(time.time())}',
        'email': f'testuser{int(time.time())}@example.com',
        'password': 'testpassword123'
    }

    try:
        response = requests.post('http://localhost:8000/users/', json=user_data)
        print(f"등록 상태: {response.status_code}")

        if response.status_code == 201:
            print("✅ 사용자 등록 성공!")
            user_info = response.json()
            print(f"사용자 ID: {user_info['data']['id']}")
            print(f"사용자명: {user_info['data']['username']}")
            return user_data, user_info['data']['id']
        else:
            print(f"❌ 등록 실패: {response.text}")
            return None, None

    except Exception as e:
        print(f"❌ 오류: {e}")
        return None, None

def test_user_login(username, password):
    """사용자 로그인 테스트"""
    print("\n=== 사용자 로그인 테스트 ===")
    login_data = {
        'username': username,
        'password': password
    }

    try:
        response = requests.post('http://localhost:8000/users/login', json=login_data)
        print(f"로그인 상태: {response.status_code}")

        if response.status_code == 200:
            print("✅ 로그인 성공!")
            token_info = response.json()
            print(f"토큰 타입: {token_info['token_type']}")
            print(f"만료 시간: {token_info['expires_in']}초")
            print(f"액세스 토큰: {token_info['access_token'][:50]}...")
            return token_info['access_token']
        else:
            print(f"❌ 로그인 실패: {response.text}")
            return None

    except Exception as e:
        print(f"❌ 오류: {e}")
        return None

def test_protected_endpoint(token):
    """보호된 엔드포인트 테스트"""
    print("\n=== 보호된 엔드포인트 테스트 ===")
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get('http://localhost:8000/users/me', headers=headers)
        print(f"현재 사용자 조회 상태: {response.status_code}")

        if response.status_code == 200:
            print("✅ 보호된 엔드포인트 접근 성공!")
            user_info = response.json()
            print(f"현재 사용자: {user_info['data']['username']}")
        else:
            print(f"❌ 접근 실패: {response.text}")

    except Exception as e:
        print(f"❌ 오류: {e}")

def test_todo_creation_with_auth(token):
    """인증된 사용자로 TODO 생성 테스트"""
    print("\n=== 인증된 TODO 생성 테스트 ===")
    headers = {"Authorization": f"Bearer {token}"}
    todo_data = {
        'title': 'JWT로 보호된 TODO',
        'description': 'bcrypt와 JWT를 사용한 안전한 TODO 생성',
        'priority': 3
    }

    try:
        response = requests.post('http://localhost:8000/todos/', json=todo_data, headers=headers)
        print(f"TODO 생성 상태: {response.status_code}")

        if response.status_code == 201:
            print("✅ 인증된 TODO 생성 성공!")
            todo_info = response.json()
            print(f"TODO ID: {todo_info['data']['id']}")
            print(f"제목: {todo_info['data']['title']}")
        else:
            print(f"❌ TODO 생성 실패: {response.text}")

    except Exception as e:
        print(f"❌ 오류: {e}")

def main():
    """메인 테스트 함수"""
    print("🔐 bcrypt와 JWT 인증 시스템 테스트 시작\n")

    # 1. 사용자 등록
    user_data, user_id = test_user_registration()
    if not user_data:
        return

    # 2. 사용자 로그인
    token = test_user_login(user_data['username'], user_data['password'])
    if not token:
        return

    # 3. 보호된 엔드포인트 테스트
    test_protected_endpoint(token)

    # 4. 인증된 TODO 생성 테스트
    test_todo_creation_with_auth(token)

    print("\n🎉 모든 테스트 완료!")

if __name__ == "__main__":
    main()
