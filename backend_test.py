#!/usr/bin/env python3
"""
Backend API Testing Suite for Euloge Learning Platform
======================================================

Tests the Flask app directly.
Base URL: http://localhost:5000

Test Coverage:
1. GET /api/health (simulated or actual if implemented)
2. GET /api/mastery/get-subjects
3. GET /api/learning/progress
4. GET /api/spaced-repetition/get-schedule
5. POST /api/spaced-repetition/create-card
6. POST /api/spaced-repetition/review-card
7. POST /api/user/register + POST /api/user/login (with password hashing and JWT)
8. POST /api/analysis/generate-plan
"""

import requests
import json
import sys
from typing import Dict, Any, Optional
import uuid
import time

class BackendTester:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.user_id = None
        self.card_id = None
        self.token = None
        
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
    
    def test_user_registration_and_login(self):
        """Test POST /api/user/register and POST /api/user/login"""
        try:
            # Generate unique test user
            test_email = f"test.user.{int(time.time())}@euloge.com"
            test_username = f"testuser{int(time.time())}"
            test_password = "securePassword123"
            
            # Test registration
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
            if "user_id" not in data:
                self.log_test("User Registration", False, "Missing user_id in response", data)
                return False
            
            if "token" not in data:
                self.log_test("User Registration", False, "Missing token in response", data)
                return False

            self.user_id = data["user_id"]
            self.token = data["token"]
            self.log_test("User Registration", True, f"User registered with ID: {self.user_id} and received token")
            
            # Test login
            login_data = {
                "email": test_email,
                "password": test_password
            }

            response = self.session.post(
                f"{self.base_url}/api/user/login",
                json=login_data,
                timeout=10
            )

            if response.status_code != 200:
                self.log_test("User Login", False, f"Status code: {response.status_code}", response.text)
                return False
            
            data = response.json()
            if "token" not in data:
                 self.log_test("User Login", False, "Missing token in response", data)
                 return False

            # Update token from login
            self.token = data["token"]

            # Update session headers with token
            self.session.headers.update({'Authorization': f'Bearer {self.token}'})

            self.log_test("User Login", True, "User logged in successfully and token received")
            return True
            
        except Exception as e:
            self.log_test("User Registration/Login", False, f"Exception: {str(e)}")
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
            response = self.session.get(f"{self.base_url}/api/spaced-repetition/get-schedule?days_ahead=3", timeout=10)
            
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
            
            response = self.session.post(
                f"{self.base_url}/api/spaced-repetition/create-card",
                json=card_data,
                timeout=10
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
            
            response = self.session.post(
                f"{self.base_url}/api/spaced-repetition/review-card",
                json=review_data,
                timeout=10
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
    print("Base URL: http://localhost:5000")
    print()
    
    tester = BackendTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
