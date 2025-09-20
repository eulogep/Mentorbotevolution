#!/usr/bin/env python3
"""
Backend API Testing Suite for Euloge Learning Platform
======================================================

Tests the FastAPI gateway mounting the Flask app with all API endpoints.
Base URL: http://localhost (ingress routes /api -> backend 0.0.0.0:8001)

Test Coverage:
1. GET /api/health -> FastAPI health check
2. GET /api/mastery/get-subjects -> Mastery dashboard data
3. GET /api/learning/progress -> Learning progress data
4. GET /api/spaced-repetition/get-schedule -> Spaced repetition schedule
5. POST /api/spaced-repetition/create-card -> Create flashcard
6. POST /api/spaced-repetition/review-card -> Review flashcard
7. POST /api/user/register + POST /api/user/login -> User authentication
8. POST /api/analysis/generate-plan -> Generate learning plan
"""

import requests
import json
import sys
from typing import Dict, Any, Optional
import uuid
import time

class BackendTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.user_id = None
        self.card_id = None
        self.access_token = None

    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {response_data}")
        print()
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data
        })
    
    def validate_json_schema(self, data: Dict[Any, Any], required_fields: list, test_name: str) -> bool:
        """Validate JSON response has required fields"""
        missing_fields = []
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
        
        if missing_fields:
            self.log_test(test_name, False, f"Missing required fields: {missing_fields}", data)
            return False
        return True
    
    def test_health_endpoint(self):
        """Test GET /api/health"""
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Health Check", False, f"Status code: {response.status_code}", response.text)
                return False
            
            data = response.json()
            required_fields = ["status", "service", "version"]
            
            if not self.validate_json_schema(data, required_fields, "Health Check Schema"):
                return False
            
            if data["status"] != "healthy":
                self.log_test("Health Check", False, f"Status not healthy: {data['status']}", data)
                return False
            
            if data["service"] != "fastapi-gateway":
                self.log_test("Health Check", False, f"Unexpected service: {data['service']}", data)
                return False
            
            self.log_test("Health Check", True, f"Service: {data['service']}, Version: {data['version']}")
            return True
            
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_mastery_subjects(self):
        """Test GET /api/mastery/get-subjects"""
        try:
            response = self.session.get(f"{self.base_url}/api/mastery/get-subjects", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Mastery Subjects", False, f"Status code: {response.status_code}", response.text)
                return False
            
            data = response.json()
            required_fields = ["status", "subjects"]
            
            if not self.validate_json_schema(data, required_fields, "Mastery Subjects Schema"):
                return False
            
            if data["status"] != "success":
                self.log_test("Mastery Subjects", False, f"Status not success: {data['status']}", data)
                return False
            
            # Validate subjects array structure
            if not isinstance(data["subjects"], list):
                self.log_test("Mastery Subjects", False, "Subjects is not an array", data)
                return False
            
            # If subjects exist, validate their structure
            if data["subjects"]:
                subject = data["subjects"][0]
                subject_fields = ["id", "name", "description", "progress", "target_score", "current_score"]
                for field in subject_fields:
                    if field not in subject:
                        self.log_test("Mastery Subjects", False, f"Subject missing field: {field}", subject)
                        return False
            
            self.log_test("Mastery Subjects", True, f"Found {len(data['subjects'])} subjects")
            return True
            
        except Exception as e:
            self.log_test("Mastery Subjects", False, f"Exception: {str(e)}")
            return False
    
    def test_learning_progress(self):
        """Test GET /api/learning/progress"""
        try:
            response = self.session.get(f"{self.base_url}/api/learning/progress", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Learning Progress", False, f"Status code: {response.status_code}", response.text)
                return False
            
            data = response.json()
            # Check for expected fields based on review request
            expected_fields = ["currentScore", "targetScore"]
            
            has_expected = any(field in data for field in expected_fields)
            if not has_expected:
                self.log_test("Learning Progress", False, f"Missing expected fields like currentScore, targetScore", data)
                return False
            
            self.log_test("Learning Progress", True, f"Progress data retrieved with fields: {list(data.keys())}")
            return True
            
        except Exception as e:
            self.log_test("Learning Progress", False, f"Exception: {str(e)}")
            return False
    
    def test_spaced_repetition_schedule(self):
        """Test GET /api/spaced-repetition/get-schedule?days_ahead=3"""
        try:
            headers = {}
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"
            response = self.session.get(f"{self.base_url}/api/spaced-repetition/get-schedule?days_ahead=3", timeout=10, headers=headers)
            
            if response.status_code != 200:
                self.log_test("Spaced Repetition Schedule", False, f"Status code: {response.status_code}", response.text)
                return False
            
            data = response.json()
            required_fields = ["status", "schedule", "summary"]
            
            if not self.validate_json_schema(data, required_fields, "Spaced Repetition Schedule Schema"):
                return False
            
            if data["status"] != "success":
                self.log_test("Spaced Repetition Schedule", False, f"Status not success: {data['status']}", data)
                return False
            
            self.log_test("Spaced Repetition Schedule", True, "Schedule retrieved successfully")
            return True
            
        except Exception as e:
            self.log_test("Spaced Repetition Schedule", False, f"Exception: {str(e)}")
            return False
    
    def test_create_card(self):
        """Test POST /api/spaced-repetition/create-card"""
        try:
            card_data = {
                "concept_name": "TOEIC Listening Comprehension",
                "content": "Practice identifying main ideas in audio passages"
            }
            
            headers = {}
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"
            response = self.session.post(
                f"{self.base_url}/api/spaced-repetition/create-card",
                json=card_data,
                timeout=10,
                headers=headers
            )
            
            if response.status_code not in [200, 201]:
                self.log_test("Create Card", False, f"Status code: {response.status_code}", response.text)
                return False
            
            data = response.json()
            required_fields = ["status", "card"]
            
            if not self.validate_json_schema(data, required_fields, "Create Card Schema"):
                return False
            
            if data["status"] != "success":
                self.log_test("Create Card", False, f"Status not success: {data['status']}", data)
                return False
            
            # Store card_id for review test
            if "card" in data and isinstance(data["card"], dict) and "id" in data["card"]:
                self.card_id = data["card"]["id"]
            
            self.log_test("Create Card", True, f"Card created successfully")
            return True
            
        except Exception as e:
            self.log_test("Create Card", False, f"Exception: {str(e)}")
            return False
    
    def test_review_card(self):
        """Test POST /api/spaced-repetition/review-card"""
        try:
            # Use a test card_id if we don't have one from create
            test_card_id = self.card_id or str(uuid.uuid4())
            
            review_data = {
                "card_id": test_card_id,
                "quality_response": 4,
                "current_interval": 1,
                "current_easiness": 2.5,
                "review_count": 1,
                "success_rate": 0.8,
                "average_response_time": 15.5,
                "response_time": 12.3
            }
            
            headers = {}
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"
            response = self.session.post(
                f"{self.base_url}/api/spaced-repetition/review-card",
                json=review_data,
                timeout=10,
                headers=headers
            )
            
            if response.status_code not in [200, 201]:
                self.log_test("Review Card", False, f"Status code: {response.status_code}", response.text)
                return False
            
            data = response.json()
            # Check for expected return fields
            expected_fields = ["updated_card", "retention_probability"]
            
            has_expected = any(field in data for field in expected_fields)
            if not has_expected:
                self.log_test("Review Card", False, f"Missing expected fields: {expected_fields}", data)
                return False
            
            self.log_test("Review Card", True, "Card reviewed successfully")
            return True
            
        except Exception as e:
            self.log_test("Review Card", False, f"Exception: {str(e)}")
            return False
    
    def test_user_registration_and_login(self):
        """Test POST /api/user/register and POST /api/user/login (JWT)"""
        try:
            # Generate unique test user
            test_email = f"test.user.{int(time.time())}@euloge.com"
            test_username = f"testuser{int(time.time())}"
            test_password = "TestPassw0rd!"

            # Registration
            register_data = {
                "username": test_username,
                "email": test_email,
                "password": test_password
            }
            response = self.session.post(
                f"{self.base_url}/api/user/register",
                json=register_data,
                timeout=10
            )
            if response.status_code != 201:
                self.log_test("User Registration", False, f"Status code: {response.status_code}", response.text)
                return False
            data = response.json()
            if "user" not in data or "access_token" not in data:
                self.log_test("User Registration", False, "Missing user or access_token in response", data)
                return False
            self.user_id = data["user"]["id"]
            self.access_token = data["access_token"]
            self.log_test("User Registration", True, f"User registered: {self.user_id}")

            # Login
            login_data = {"email": test_email, "password": test_password}
            response = self.session.post(
                f"{self.base_url}/api/user/login",
                json=login_data,
                timeout=10
            )
            if response.status_code != 200:
                self.log_test("User Login", False, f"Status code: {response.status_code}", response.text)
                return False
            data = response.json()
            if "access_token" not in data:
                self.log_test("User Login", False, "Missing access_token in response", data)
                return False
            self.access_token = data["access_token"]
            self.log_test("User Login", True, "User logged in successfully")
            return True
            
        except Exception as e:
            self.log_test("User Registration/Login", False, f"Exception: {str(e)}")
            return False
    
    def test_generate_plan(self):
        """Test POST /api/analysis/generate-plan"""
        try:
            plan_data = {
                "target_score": 850,
                "timeframe_months": 6,
                "daily_study_hours": 2,
                "learning_style": "visual",
                "chronotype": "morning",
                "concepts": [
                    {
                        "name": "Listening Comprehension",
                        "difficulty": "medium",
                        "importance": "high"
                    },
                    {
                        "name": "Reading Comprehension",
                        "difficulty": "hard",
                        "importance": "high"
                    },
                    {
                        "name": "Grammar",
                        "difficulty": "easy",
                        "importance": "medium"
                    }
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/api/analysis/generate-plan",
                json=plan_data,
                timeout=15
            )
            
            if response.status_code not in [200, 201]:
                self.log_test("Generate Plan", False, f"Status code: {response.status_code}", response.text)
                return False
            
            data = response.json()
            if "status" not in data or data["status"] != "success":
                self.log_test("Generate Plan", False, f"Status not success: {data.get('status')}", data)
                return False
            
            # Check for plan fields
            if "plan" not in data:
                self.log_test("Generate Plan", False, "Missing plan field in response", data)
                return False
            
            self.log_test("Generate Plan", True, "Learning plan generated successfully")
            return True
            
        except Exception as e:
            self.log_test("Generate Plan", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Backend API Tests for Euloge Learning Platform")
        print("=" * 60)
        print()
        
        tests = [
            ("Health Check", self.test_health_endpoint),
            ("User Registration/Login", self.test_user_registration_and_login),
            ("Mastery Subjects", self.test_mastery_subjects),
            ("Learning Progress", self.test_learning_progress),
            ("Spaced Repetition Schedule", self.test_spaced_repetition_schedule),
            ("Create Card", self.test_create_card),
            ("Review Card", self.test_review_card),
            ("Generate Plan", self.test_generate_plan),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"Running {test_name}...")
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_test(test_name, False, f"Unexpected error: {str(e)}")
        
        print("=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Backend is working correctly.")
            return True
        else:
            print(f"⚠️  {total - passed} tests failed. See details above.")
            return False

def main():
    """Main test runner"""
    print("Backend API Testing Suite")
    print("Base URL: http://localhost:8001")
    print()
    
    tester = BackendTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
