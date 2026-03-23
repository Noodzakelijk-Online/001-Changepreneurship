#!/usr/bin/env python3
import json
from pathlib import Path

import requests

BASE_URL = "http://localhost:5000"
PASSWORD = "Test1234!"

PHASE_ID_MAP = {
    "Self Discovery Assessment": "self_discovery",
    "Idea Discovery Assessment": "idea_discovery",
    "Market Research": "market_research",
    "Business Pillars Planning": "business_pillars",
    "Product Concept Testing": "product_concept_testing",
    "Business Development": "business_development",
    "Business Prototype Testing": "business_prototype_testing",
}


def main() -> None:
    fixture_path = Path(__file__).resolve().parent / "beginner_founder_complete_data.json"
    data = json.loads(fixture_path.read_text(encoding="utf-8"))
    user_data = data["user"]

    users_resp = requests.get(f"{BASE_URL}/api/users", timeout=20)
    users_resp.raise_for_status()
    for user in users_resp.json():
        if user.get("username") == user_data["username"] or user.get("email") == user_data["email"]:
            requests.delete(f"{BASE_URL}/api/users/{user['id']}", timeout=20).raise_for_status()

    reg_payload = {
        "username": user_data["username"],
        "email": user_data["email"],
        "password": PASSWORD,
    }
    reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json=reg_payload, timeout=20)
    reg_resp.raise_for_status()

    login_resp = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": user_data["username"], "password": PASSWORD},
        timeout=20,
    )
    login_resp.raise_for_status()
    token = login_resp.json()["session_token"]
    headers = {"Authorization": f"Bearer {token}"}

    total_responses = 0

    for assessment_data in data["assessments"]:
        phase_name = assessment_data["phase_name"]
        phase_id = PHASE_ID_MAP[phase_name]

        start_resp = requests.post(
            f"{BASE_URL}/api/assessment/start/{phase_id}",
            headers=headers,
            timeout=20,
        )
        start_resp.raise_for_status()
        assessment_id = start_resp.json()["assessment"]["id"]

        for response in assessment_data["responses"]:
            save_payload = {
                "section_id": response["section_id"],
                "question_id": response["question_id"],
                "question_text": response["question_text"],
                "response_type": response["response_type"],
                "response_value": response.get("response_value", ""),
            }
            save_resp = requests.post(
                f"{BASE_URL}/api/assessment/{assessment_id}/response",
                headers=headers,
                json=save_payload,
                timeout=20,
            )
            save_resp.raise_for_status()
            total_responses += 1

        progress_payload = {
            "progress_percentage": float(assessment_data.get("progress_percentage", 100.0)),
            "is_completed": True,
        }
        progress_resp = requests.put(
            f"{BASE_URL}/api/assessment/{assessment_id}/progress",
            headers=headers,
            json=progress_payload,
            timeout=20,
        )
        progress_resp.raise_for_status()

    verify_login = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": user_data["username"], "password": PASSWORD},
        timeout=20,
    )
    verify_login.raise_for_status()

    print("=" * 60)
    print("BEGINNER USER SEEDED IN LIVE APP DB")
    print("=" * 60)
    print(f"Username: {user_data['username']}")
    print(f"Email: {user_data['email']}")
    print(f"Password: {PASSWORD}")
    print(f"Assessments: {len(data['assessments'])}")
    print(f"Responses: {total_responses}")
    print("Login check: OK")


if __name__ == "__main__":
    main()
