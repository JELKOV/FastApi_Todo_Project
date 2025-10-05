"""
구조화된 요청 모델 테스트

이 테스트는 새로 만든 구조화된 요청 모델들이
제대로 작동하는지 확인합니다.
"""

import requests
import json
from typing import Dict, Any


class StructuredRequestTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def test_structured_create_request(self):
        """구조화된 생성 요청 테스트"""
        print("🔍 Testing structured create request...")

        # 기본 생성 요청
        create_data = {
            "title": "구조화된 요청 테스트",
            "description": "새로운 요청 모델 시스템 테스트",
            "priority": 4,
            "completed": False
        }

        try:
            response = self.session.post(
                f"{self.base_url}/todos/",
                json=create_data,
                headers={"Content-Type": "application/json"}
            )
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            return response.json()
        except Exception as e:
            print(f"❌ Error: {e}")
            return {}

    def test_structured_list_request(self):
        """구조화된 목록 요청 테스트"""
        print("\n🔍 Testing structured list request...")

        # 다양한 필터와 정렬 옵션 테스트
        test_cases = [
            {
                "name": "기본 페이징",
                "params": {"page": 1, "size": 5}
            },
            {
                "name": "완료 상태 필터",
                "params": {"completed": False, "page": 1, "size": 10}
            },
            {
                "name": "우선순위 필터",
                "params": {"priority": 3, "page": 1, "size": 10}
            },
            {
                "name": "정렬 옵션",
                "params": {"sort_by": "priority", "sort_order": "asc", "page": 1, "size": 10}
            },
            {
                "name": "복합 필터",
                "params": {
                    "completed": True,
                    "priority": 2,
                    "sort_by": "updated_at",
                    "sort_order": "desc",
                    "page": 1,
                    "size": 5
                }
            }
        ]

        for test_case in test_cases:
            print(f"\n📝 Testing: {test_case['name']}")
            try:
                response = self.session.get(
                    f"{self.base_url}/todos/",
                    params=test_case['params']
                )
                print(f"Status Code: {response.status_code}")
                result = response.json()
                print(f"Total: {result.get('data', {}).get('total', 0)}")
                print(f"Page: {result.get('data', {}).get('page', 0)}")
                print(f"Size: {result.get('data', {}).get('size', 0)}")
                print(f"Todos count: {len(result.get('data', {}).get('todos', []))}")
            except Exception as e:
                print(f"❌ Error: {e}")

    def test_structured_update_request(self):
        """구조화된 수정 요청 테스트"""
        print("\n🔍 Testing structured update request...")

        # 먼저 TODO 생성
        create_data = {
            "title": "수정 테스트용 TODO",
            "description": "수정 전 설명",
            "priority": 1,
            "completed": False
        }

        try:
            # TODO 생성
            create_response = self.session.post(
                f"{self.base_url}/todos/",
                json=create_data
            )
            if create_response.status_code == 201:
                todo_id = create_response.json()['data']['id']
                print(f"Created TODO with ID: {todo_id}")

                # 부분 업데이트 테스트
                update_data = {
                    "title": "수정된 제목",
                    "priority": 5
                }

                update_response = self.session.put(
                    f"{self.base_url}/todos/{todo_id}",
                    json=update_data
                )
                print(f"Update Status Code: {update_response.status_code}")
                print(f"Update Response: {json.dumps(update_response.json(), indent=2, ensure_ascii=False)}")

                # TODO 삭제 (정리)
                delete_response = self.session.delete(f"{self.base_url}/todos/{todo_id}")
                print(f"Cleanup - Delete Status: {delete_response.status_code}")

        except Exception as e:
            print(f"❌ Error: {e}")

    def test_validation_errors(self):
        """검증 오류 테스트"""
        print("\n🔍 Testing validation errors...")

        test_cases = [
            {
                "name": "빈 제목",
                "data": {"title": "", "priority": 1}
            },
            {
                "name": "너무 긴 제목",
                "data": {"title": "x" * 201, "priority": 1}
            },
            {
                "name": "잘못된 우선순위 (너무 높음)",
                "data": {"title": "테스트", "priority": 10}
            },
            {
                "name": "잘못된 우선순위 (너무 낮음)",
                "data": {"title": "테스트", "priority": 0}
            },
            {
                "name": "정렬 순서 오류",
                "params": {"sort_order": "invalid"}
            }
        ]

        for test_case in test_cases:
            print(f"\n📝 Testing validation: {test_case['name']}")
            try:
                if 'data' in test_case:
                    response = self.session.post(
                        f"{self.base_url}/todos/",
                        json=test_case['data']
                    )
                else:
                    response = self.session.get(
                        f"{self.base_url}/todos/",
                        params=test_case['params']
                    )

                print(f"Status Code: {response.status_code}")
                if response.status_code != 200:
                    result = response.json()
                    print(f"Error: {result.get('msg', 'Unknown error')}")
                    if 'validation_errors' in result.get('data', {}):
                        for error in result['data']['validation_errors']:
                            print(f"  - {error.get('msg', 'Unknown validation error')}")
            except Exception as e:
                print(f"❌ Error: {e}")

    def test_advanced_features(self):
        """고급 기능 테스트"""
        print("\n🔍 Testing advanced request features...")

        # 검색 기능 (실제로는 백엔드에서 구현되어야 함)
        print("\n📝 Testing search functionality...")
        try:
            response = self.session.get(
                f"{self.base_url}/todos/",
                params={"query": "테스트", "page": 1, "size": 10}
            )
            print(f"Search Status Code: {response.status_code}")
            result = response.json()
            print(f"Search Results: {result.get('data', {}).get('total', 0)} items found")
        except Exception as e:
            print(f"❌ Error: {e}")

        # 복잡한 필터링
        print("\n📝 Testing complex filtering...")
        try:
            response = self.session.get(
                f"{self.base_url}/todos/",
                params={
                    "completed": False,
                    "priority": 3,
                    "sort_by": "created_at",
                    "sort_order": "desc",
                    "page": 1,
                    "size": 3
                }
            )
            print(f"Complex Filter Status Code: {response.status_code}")
            result = response.json()
            print(f"Filtered Results: {result.get('data', {}).get('total', 0)} items")
        except Exception as e:
            print(f"❌ Error: {e}")

    def run_comprehensive_test(self):
        """종합 테스트 실행"""
        print("🚀 Starting structured request model test...")
        print("=" * 60)

        # 1. 구조화된 생성 요청
        self.test_structured_create_request()

        # 2. 구조화된 목록 요청
        self.test_structured_list_request()

        # 3. 구조화된 수정 요청
        self.test_structured_update_request()

        # 4. 검증 오류 테스트
        self.test_validation_errors()

        # 5. 고급 기능 테스트
        self.test_advanced_features()

        print("\n" + "=" * 60)
        print("✅ Structured request model test completed!")


def wait_for_server(max_retries: int = 30, delay: int = 2):
    """서버가 시작될 때까지 대기"""
    print("⏳ Waiting for server to start...")
    for i in range(max_retries):
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except:
            pass

        print(f"⏳ Attempt {i+1}/{max_retries} - Waiting {delay}s...")
        import time
        time.sleep(delay)

    print("❌ Server failed to start within timeout period")
    return False


if __name__ == "__main__":
    # 서버 대기
    if not wait_for_server():
        print("Please start the server first with: python run.py")
        exit(1)

    # 테스트 실행
    tester = StructuredRequestTester()
    tester.run_comprehensive_test()
