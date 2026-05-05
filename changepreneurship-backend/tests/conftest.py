import os
import sys

import pytest
from flask import Flask


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)


from src.models.assessment import db
from src.models.founder_profile import FounderReadinessProfile, PhaseGate  # noqa: F401 — ensures db.create_all picks up tables
from src.models.user_action import UserAction, BlockerEvent  # noqa: F401
from src.models.venture_record import VentureRecord, EvidenceItem  # noqa: F401
from src.models.benchmark_data import BenchmarkData  # noqa: F401
from src.models.external_connection import ExternalConnection  # noqa: F401
from src.models.data_consent_log import DataConsentLog  # noqa: F401
from src.models.venture import Venture  # noqa: F401
from src.routes.auth import auth_bp
from src.routes.assessment import assessment_bp
from src.routes.dashboard import dashboard_bp
from src.routes.analytics import analytics_bp
from src.routes.ai_recommendations import ai_recommendations_bp
from src.routes.user import user_bp
from src.routes.mind_mapping import mind_mapping_bp
from src.routes.phase1 import phase1_bp
from src.routes.routing import routing_bp
from src.routes.phase2 import phase2_bp
from src.routes.actions import actions_bp
from src.routes.progress import progress_bp
from src.routes.safety import safety_bp
from src.routes.phase3 import phase3_bp
from src.routes.phase4 import phase4_bp
from src.routes.phase5 import phase5_bp
from src.routes.phase6 import phase6_bp
from src.routes.phase7 import phase7_bp
from src.routes.venture_profile import venture_profile_bp
from src.routes.account import account_bp
from src.models.market_research import CompetitorEntry, MarketContext, MarketValidityReport  # noqa: F401
from src.models.business_pillars import BusinessPillarsData, BusinessPillarsBlueprint  # noqa: F401
from src.models.concept_testing import ConceptTestData, ConceptTestResult  # noqa: F401
from src.models.business_development import BusinessDevData, VentureEnvironment  # noqa: F401
from src.models.prototype_testing import PrototypeTestData, PrototypeTestResult  # noqa: F401


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
    app.register_blueprint(phase1_bp, url_prefix="/api/v1")
    app.register_blueprint(routing_bp, url_prefix="/api/v1")
    app.register_blueprint(phase2_bp, url_prefix="/api/v1")
    app.register_blueprint(actions_bp, url_prefix="/api/v1")
    app.register_blueprint(progress_bp, url_prefix="/api/v1")
    app.register_blueprint(safety_bp, url_prefix="/api/v1")
    app.register_blueprint(phase3_bp, url_prefix="/api/v1")
    app.register_blueprint(phase4_bp, url_prefix="/api/v1")
    app.register_blueprint(phase5_bp, url_prefix="/api/v1")
    app.register_blueprint(phase6_bp, url_prefix="/api/v1")
    app.register_blueprint(phase7_bp, url_prefix="/api/v1")
    app.register_blueprint(venture_profile_bp, url_prefix="/api/v1")
    app.register_blueprint(account_bp, url_prefix="/api/v1")

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
