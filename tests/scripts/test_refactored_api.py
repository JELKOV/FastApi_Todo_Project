"""
리팩토링된 TODO API 테스트 코드

이 테스트는 새로운 응답 시스템과 예외 처리가
제대로 작동하는지 확인합니다.
"""

import requests
import json
import time
from typing import Dict, Any


class TodoAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def test_root_endpoint(self) -> Dict[str, Any]:
        """루트 엔드포인트 테스트"""
        print("🔍 Testing root endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            return response.json()
        except Exception as e:
            print(f"❌ Error: {e}")
            return {}

    def test_health_endpoint(self) -> Dict[str, Any]:
        """헬스 체크 엔드포인트 테스트"""
        print("\n🔍 Testing health endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            return response.json()
        except Exception as e:
            print(f"❌ Error: {e}")
            return {}

    def test_create_todo(self, todo_data: Dict[str, Any]) -> Dict[str, Any]:
        """TODO 생성 테스트"""
        print(f"\n🔍 Testing create todo with data: {todo_data}")
        try:
            response = self.session.post(
                f"{self.base_url}/todos/",
                json=todo_data,
                headers={"Content-Type": "application/json"}
            )
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            return response.json()
        except Exception as e:
            print(f"❌ Error: {e}")
            return {}

    def test_get_todos(self, page: int = 1, size: int = 10) -> Dict[str, Any]:
        """TODO 목록 조회 테스트"""
        print(f"\n🔍 Testing get todos (page={page}, size={size})...")
        try:
            response = self.session.get(f"{self.base_url}/todos/?page={page}&size={size}")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            return response.json()
        except Exception as e:
            print(f"❌ Error: {e}")
            return {}

    def test_get_todo_by_id(self, todo_id: int) -> Dict[str, Any]:
        """특정 TODO 조회 테스트"""
        print(f"\n🔍 Testing get todo by ID: {todo_id}")
        try:
            response = self.session.get(f"{self.base_url}/todos/{todo_id}")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            return response.json()
        except Exception as e:
            print(f"❌ Error: {e}")
            return {}

    def test_update_todo(self, todo_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """TODO 수정 테스트"""
        print(f"\n🔍 Testing update todo {todo_id} with data: {update_data}")
        try:
            response = self.session.put(
                f"{self.base_url}/todos/{todo_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            return response.json()
        except Exception as e:
            print(f"❌ Error: {e}")
            return {}

    def test_toggle_todo(self, todo_id: int) -> Dict[str, Any]:
        """TODO 토글 테스트"""
        print(f"\n🔍 Testing toggle todo {todo_id}")
        try:
            response = self.session.patch(f"{self.base_url}/todos/{todo_id}/toggle")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            return response.json()
        except Exception as e:
            print(f"❌ Error: {e}")
            return {}

    def test_delete_todo(self, todo_id: int) -> Dict[str, Any]:
        """TODO 삭제 테스트"""
        print(f"\n🔍 Testing delete todo {todo_id}")
        try:
            response = self.session.delete(f"{self.base_url}/todos/{todo_id}")
            print(f"Status Code: {response.status_code}")
            if response.status_code == 204:
                print("✅ Todo deleted successfully (No Content)")
                return {"status": "deleted"}
            else:
                print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
                return response.json()
        except Exception as e:
            print(f"❌ Error: {e}")
            return {}

    def test_error_scenarios(self):
        """에러 시나리오 테스트"""
        print("\n🔍 Testing error scenarios...")

        # 존재하지 않는 TODO 조회
        print("\n📝 Testing 404 error (non-existent todo)...")
        self.test_get_todo_by_id(99999)

        # 잘못된 데이터로 TODO 생성
        print("\n📝 Testing validation error (invalid data)...")
        invalid_data = {
            "title": "",  # 빈 제목
            "priority": 10  # 잘못된 우선순위
        }
        self.test_create_todo(invalid_data)

    def run_comprehensive_test(self):
        """종합 테스트 실행"""
        print("🚀 Starting comprehensive API test...")
        print("=" * 60)

        # 1. 기본 엔드포인트 테스트
        self.test_root_endpoint()
        self.test_health_endpoint()

        # 2. TODO 생성
        todo_data = {
            "title": "리팩토링 테스트 TODO",
            "description": "새로운 응답 시스템 테스트용",
            "priority": 3,
            "completed": False
        }
        create_result = self.test_create_todo(todo_data)

        # 생성된 TODO ID 추출
        todo_id = None
        if create_result.get("data") and "id" in create_result["data"]:
            todo_id = create_result["data"]["id"]

        if todo_id:
            # 3. TODO 목록 조회
            self.test_get_todos()

            # 4. 특정 TODO 조회
            self.test_get_todo_by_id(todo_id)

            # 5. TODO 수정
            update_data = {
                "title": "수정된 리팩토링 테스트 TODO",
                "description": "수정된 설명",
                "priority": 5
            }
            self.test_update_todo(todo_id, update_data)

            # 6. TODO 토글
            self.test_toggle_todo(todo_id)

            # 7. TODO 삭제
            self.test_delete_todo(todo_id)

        # 8. 에러 시나리오 테스트
        self.test_error_scenarios()

        print("\n" + "=" * 60)
        print("✅ Comprehensive test completed!")


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
        time.sleep(delay)

    print("❌ Server failed to start within timeout period")
    return False


if __name__ == "__main__":
    # 서버 대기
    if not wait_for_server():
        print("Please start the server first with: python run.py")
        exit(1)

    # 테스트 실행
    tester = TodoAPITester()
    tester.run_comprehensive_test()
