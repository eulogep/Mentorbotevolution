import requests
import time

BASE_URL = "http://localhost:5000"


def debug_auth():
    print("Debugging Authentication Flow...")

    # 1. Register/Login
    email = f"debug.{int(time.time())}@euloge.com"
    password = "password123"
    username = f"debug{int(time.time())}"

    print(f"Registering user: {email}")
    resp = requests.post(
        f"{BASE_URL}/api/user/register",
        json={"username": username, "email": email, "password": password},
    )
    print(f"Register Status: {resp.status_code}")
    print(f"Register Response: {resp.text}")

    print(f"Logging in user: {email}")
    resp = requests.post(
        f"{BASE_URL}/api/user/login", json={"email": email, "password": password}
    )
    print(f"Login Status: {resp.status_code}")
    print(f"Login Response: {resp.text}")

    if resp.status_code != 200:
        print("Login failed, aborting.")
        return

    data = resp.json()
    token = data.get("access_token")
    if not token:
        print("No access token found!")
        return

    print(f"Got Access Token: {token[:20]}...")

    # 2. Access Protected Route
    print("Accessing Protected Route: /api/analysis/generate-plan")
    headers = {"Authorization": f"Bearer {token}"}
    plan_data = {
        "target_score": 850,
        "timeframe_months": 6,
        "daily_study_hours": 2,
        "learning_style": "visual",
    }

    resp = requests.post(
        f"{BASE_URL}/api/analysis/generate-plan", json=plan_data, headers=headers
    )
    print(f"Protected Route Status: {resp.status_code}")
    print(f"Protected Route Response: {resp.text}")


if __name__ == "__main__":
    debug_auth()
