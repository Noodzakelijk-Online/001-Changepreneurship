from src.models.assessment import User, EntrepreneurProfile
from src.routes import auth as auth_module


def test_register_rolls_back_user_on_profile_failure(app, client, monkeypatch):
    def failing_profile(*args, **kwargs):
        raise RuntimeError("Simulated failure while creating profile")

    monkeypatch.setattr(auth_module, "EntrepreneurProfile", failing_profile)

    payload = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Password123",
    }

    response = client.post("/api/auth/register", json=payload)

    assert response.status_code == 500

    with app.app_context():
        assert User.query.count() == 0
        assert EntrepreneurProfile.query.count() == 0
