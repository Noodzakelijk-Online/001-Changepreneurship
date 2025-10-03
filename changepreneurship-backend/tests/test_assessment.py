from datetime import datetime, timedelta

from src.models.assessment import (
    Assessment,
    AssessmentResponse,
    User,
    UserSession,
    db,
)


def create_assessment_with_session(app, session_token):
    with app.app_context():
        user = User(username="tester", email=f"{session_token}@example.com", password_hash="hashed")
        db.session.add(user)
        db.session.flush()

        session = UserSession(
            user_id=user.id,
            session_token=session_token,
            expires_at=datetime.utcnow() + timedelta(days=1),
            is_active=True,
        )
        db.session.add(session)

        assessment = Assessment(
            user_id=user.id,
            phase_id="self_discovery",
            phase_name="Self Discovery",
            started_at=datetime.utcnow(),
        )
        db.session.add(assessment)
        db.session.commit()

        return assessment.id



def test_save_response_updates_existing_response(app, client):
    with app.app_context():
        user = User(username="tester", email="tester@example.com", password_hash="hashed")
        db.session.add(user)
        db.session.flush()

        session = UserSession(
            user_id=user.id,
            session_token="test-token",
            expires_at=datetime.utcnow() + timedelta(days=1),
            is_active=True,
        )
        db.session.add(session)

        assessment = Assessment(
            user_id=user.id,
            phase_id="self_discovery",
            phase_name="Self Discovery",
            started_at=datetime.utcnow(),
        )
        db.session.add(assessment)
        db.session.flush()

        existing_response = AssessmentResponse(
            assessment_id=assessment.id,
            section_id="section-1",
            question_id="q1",
            question_text="Original question",
            response_type="text",
        )
        existing_response.set_response_value("Original answer")
        db.session.add(existing_response)
        db.session.commit()

        assessment_id = assessment.id
        question_id = existing_response.question_id

    payload = {
        "section_id": "section-1",
        "question_id": question_id,
        "question_text": "Updated question",
        "response_type": "json",
        "response_value": {"answer": ["A", "B"]},
    }
    headers = {"Authorization": "Bearer test-token"}

    response = client.post(
        f"/api/assessment/{assessment_id}/response",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 200

    with app.app_context():
        updated_response = AssessmentResponse.query.filter_by(
            assessment_id=assessment_id, question_id=question_id
        ).one()

        assert updated_response.response_type == "json"
        assert updated_response.question_text == "Updated question"
        assert updated_response.get_response_value() == {"answer": ["A", "B"]}
        assert updated_response.updated_at is not None


def test_update_progress_valid_value(app, client):
    assessment_id = create_assessment_with_session(app, "token-progress-valid")
    headers = {"Authorization": "Bearer token-progress-valid"}

    response = client.put(
        f"/api/assessment/{assessment_id}/progress",
        json={"progress_percentage": 45.5},
        headers=headers,
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["assessment"]["progress_percentage"] == 45.5

    with app.app_context():
        assessment = Assessment.query.get(assessment_id)
        assert assessment.progress_percentage == 45.5


def test_update_progress_rejects_non_numeric_value(app, client):
    assessment_id = create_assessment_with_session(app, "token-progress-invalid")
    headers = {"Authorization": "Bearer token-progress-invalid"}

    response = client.put(
        f"/api/assessment/{assessment_id}/progress",
        json={"progress_percentage": "not-a-number"},
        headers=headers,
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Invalid progress_percentage. Must be a numeric value."

    with app.app_context():
        assessment = Assessment.query.get(assessment_id)
        assert assessment.progress_percentage == 0.0


def test_update_progress_clamps_out_of_range_value(app, client):
    assessment_id = create_assessment_with_session(app, "token-progress-out-of-range")
    headers = {"Authorization": "Bearer token-progress-out-of-range"}

    response = client.put(
        f"/api/assessment/{assessment_id}/progress",
        json={"progress_percentage": 150},
        headers=headers,
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["assessment"]["progress_percentage"] == 100.0

    with app.app_context():
        assessment = Assessment.query.get(assessment_id)
        assert assessment.progress_percentage == 100.0
