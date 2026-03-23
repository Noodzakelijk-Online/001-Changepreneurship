#!/usr/bin/env python3
"""Create beginner founder user from JSON fixture with all assessments fully answered."""
import json
from datetime import datetime
from pathlib import Path

from werkzeug.security import generate_password_hash

from src.main import app, db
from src.models.assessment import User, Assessment, AssessmentResponse, EntrepreneurProfile, UserSession


PHASE_ID_MAP = {
    "Self Discovery Assessment": "self_discovery",
    "Idea Discovery Assessment": "idea_discovery",
    "Market Research": "market_research",
    "Business Pillars Planning": "business_pillars",
    "Product Concept Testing": "product_concept_testing",
    "Business Development": "business_development",
    "Business Prototype Testing": "business_prototype_testing",
}


def to_phase_id(phase_name: str) -> str:
    if phase_name in PHASE_ID_MAP:
        return PHASE_ID_MAP[phase_name]
    return phase_name.lower().replace(" ", "_")


def load_fixture() -> dict:
    project_root = Path(__file__).resolve().parent.parent
    fixture_path = project_root / "beginner_founder_complete_data.json"
    with fixture_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def delete_existing_user(username: str, email: str) -> None:
    existing_users = User.query.filter((User.username == username) | (User.email == email)).all()
    for existing in existing_users:
        UserSession.query.filter_by(user_id=existing.id).delete()
        assessments = Assessment.query.filter_by(user_id=existing.id).all()
        for assessment in assessments:
            AssessmentResponse.query.filter_by(assessment_id=assessment.id).delete()
            db.session.delete(assessment)
        EntrepreneurProfile.query.filter_by(user_id=existing.id).delete()
        db.session.delete(existing)
    if existing_users:
        db.session.commit()


def create_user_with_assessments(password: str = "Test1234!") -> tuple[User, int, int]:
    data = load_fixture()
    user_data = data["user"]

    delete_existing_user(user_data["username"], user_data["email"])

    user = User(
        username=user_data["username"],
        email=user_data["email"],
        password_hash=generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()

    assessment_count = 0
    response_count = 0

    for assessment_data in data.get("assessments", []):
        phase_name = assessment_data["phase_name"]
        assessment = Assessment(
            user_id=user.id,
            phase_id=to_phase_id(phase_name),
            phase_name=phase_name,
            is_completed=bool(assessment_data.get("progress_percentage", 0) >= 100),
            progress_percentage=float(assessment_data.get("progress_percentage", 0.0)),
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )
        db.session.add(assessment)
        db.session.commit()
        assessment_count += 1

        for response in assessment_data.get("responses", []):
            db.session.add(
                AssessmentResponse(
                    assessment_id=assessment.id,
                    section_id=response["section_id"],
                    question_id=response["question_id"],
                    question_text=response["question_text"],
                    response_type=response["response_type"],
                    response_value=str(response.get("response_value", "")),
                )
            )
            response_count += 1

        db.session.commit()

    return user, assessment_count, response_count


if __name__ == "__main__":
    with app.app_context():
        user, assessments, responses = create_user_with_assessments(password="Test1234!")

        print("=" * 60)
        print("✅ BEGINNER FOUNDER USER CREATED")
        print("=" * 60)
        print(f"Username: {user.username}")
        print("Password: Test1234!")
        print(f"Email: {user.email}")
        print(f"User ID: {user.id}")
        print(f"Assessments: {assessments}")
        print(f"Responses: {responses}")
