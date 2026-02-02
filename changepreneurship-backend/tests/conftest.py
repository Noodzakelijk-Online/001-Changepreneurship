import os
import sys

import pytest
from flask import Flask


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)


from src.models.assessment import db
from src.routes.auth import auth_bp
from src.routes.assessment import assessment_bp
from src.routes.dashboard import dashboard_bp
from src.routes.analytics import analytics_bp
from src.routes.ai_recommendations import ai_recommendations_bp
from src.routes.user import user_bp
from src.routes.mind_mapping import mind_mapping_bp


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY="test-secret-key",
    )

    db.init_app(app)
    
    # Register all blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(assessment_bp, url_prefix="/api/assessment")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
    app.register_blueprint(ai_recommendations_bp, url_prefix="/api")
    app.register_blueprint(user_bp, url_prefix="/api/user")
    app.register_blueprint(mind_mapping_bp, url_prefix="/api/mind-mapping")

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
