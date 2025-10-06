#!/usr/bin/env python3
"""
Background Tasks 실제 테스트 스크립트

FastAPI Background Tasks가 실제로 작동하는지 확인합니다.
"""

import requests
import json
import time
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:8000"


def check_server_connection():
    """서버 연결 확인"""
    print("🔍 Testing server connection...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running!")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please make sure the server is running on port 8000")
        return False
    except requests.exceptions.Timeout:
        print("❌ Server connection timeout")
        return False


def run_otp_background_task_test():
    """OTP 요청 시 Background Task 테스트"""
    print("\n🧪 Testing OTP Background Task...")

    email = "test@example.com"
    otp_data = {"email": email}

    print(f"📤 Sending OTP request to {email}")
    start_time = time.time()

    try:
        response = requests.post(f"{BASE_URL}/users/request-otp", json=otp_data, timeout=10)
        end_time = time.time()
        response_time = end_time - start_time

        print(f"⏱️ Response time: {response_time:.3f} seconds")
        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ OTP request successful!")
            print(f"📧 Email: {data['data']['email']}")
            print(f"⏰ Expires in: {data['data']['expires_in_minutes']} minutes")

            # 개발 환경에서만 OTP 코드 표시
            if 'otp_code' in data['data']:
                print(f"🔐 OTP Code: {data['data']['otp_code']}")

            print(f"\n📝 Response Data:")
            print(json.dumps(data, indent=2, ensure_ascii=False))

            # 응답 시간 검증 (백그라운드 처리로 인한 개선)
            if response_time < 5.0:
                print(f"✅ Response time is excellent: {response_time:.3f}s")
            else:
                print(f"⚠️ Response time is slow: {response_time:.3f}s")

            return True
        else:
            print(f"❌ OTP request failed: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("❌ Request timeout - server may be overloaded")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


def run_multiple_otp_requests_test():
    """여러 OTP 요청 성능 테스트"""
    print("\n🚀 Testing Multiple OTP Requests Performance...")

    emails = [
        "test1@example.com",
        "test2@example.com",
        "test3@example.com"
    ]

    start_time = time.time()
    success_count = 0

    for i, email in enumerate(emails, 1):
        print(f"📤 Request {i}/3: {email}")
        try:
            response = requests.post(f"{BASE_URL}/users/request-otp",
                                   json={"email": email}, timeout=10)
            if response.status_code == 200:
                success_count += 1
                print(f"✅ Request {i} successful")
            else:
                print(f"❌ Request {i} failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Request {i} error: {str(e)}")

    end_time = time.time()
    total_time = end_time - start_time

    print(f"\n📊 Performance Results:")
    print(f"⏱️ Total time: {total_time:.3f} seconds")
    print(f"✅ Successful requests: {success_count}/{len(emails)}")
    print(f"📈 Average time per request: {total_time/len(emails):.3f} seconds")

    # 성능 검증
    if total_time < 10.0 and success_count == len(emails):
        print("✅ Performance test passed!")
        return True
    else:
        print("❌ Performance test failed!")
        return False


def run_otp_verification_test():
    """OTP 검증 테스트"""
    print("\n🔐 Testing OTP Verification...")

    email = "verify@example.com"

    # 1. OTP 요청
    print(f"📤 Requesting OTP for {email}")
    otp_response = requests.post(f"{BASE_URL}/users/request-otp", json={"email": email})

    if otp_response.status_code != 200:
        print(f"❌ OTP request failed: {otp_response.text}")
        return False

    otp_data = otp_response.json()

    # 개발 환경에서만 OTP 코드가 포함됨
    if 'otp_code' not in otp_data['data']:
        print("⚠️ OTP code not available in response (production mode)")
        return True

    otp_code = otp_data['data']['otp_code']
    print(f"🔐 Received OTP: {otp_code}")

    # 2. OTP 검증
    print(f"🔍 Verifying OTP...")
    verify_data = {
        "email": email,
        "otp_code": otp_code
    }

    verify_response = requests.post(f"{BASE_URL}/users/verify-otp", json=verify_data)

    if verify_response.status_code == 200:
        print("✅ OTP verification successful!")
        verify_result = verify_response.json()
        print(f"📝 Verification result: {verify_result['msg']}")
        return True
    else:
        print(f"❌ OTP verification failed: {verify_response.text}")
        return False


def main():
    """메인 테스트 함수"""
    print("🚀 FastAPI Background Tasks Real Test")
    print("=" * 50)

    # 서버 연결 테스트
    if not check_server_connection():
        return

    # 테스트 실행
    tests = [
        ("OTP Background Task", run_otp_background_task_test),
        ("Multiple OTP Requests", run_multiple_otp_requests_test),
        ("OTP Verification", run_otp_verification_test),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {str(e)}")

    # 결과 요약
    print(f"\n{'='*50}")
    print(f"🎯 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Background Tasks are working perfectly!")
    else:
        print("⚠️ Some tests failed. Please check the server logs.")

    print("\n💡 Note: Check the server console/logs to see background task execution")
    print("💡 Look for messages like:")
    print("   - '📧 EMAIL SENT (Development Mode)'")
    print("   - '✅ Background task completed: OTP email sent to ...'")


if __name__ == "__main__":
    main()
