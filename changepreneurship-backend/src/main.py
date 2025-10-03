import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from src.models.assessment import db
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.assessment import assessment_bp
from src.routes.analytics import analytics_bp
from src.routes.principles import principles_bp
from src.routes.purpose_discovery import purpose_discovery_bp
from src.routes.mind_mapping import mind_mapping_bp
from src.routes.value_zone_validator import value_zone_bp
from src.routes.ai_adoption_roadmap import ai_adoption_bp
from src.routes.enhanced_assessment import enhanced_assessment_bp

app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), "static")
)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "changepreneurship-secret-key-2024-secure")

DEFAULT_ORIGINS = "http://localhost:5173,https://changepreneurship-1.onrender.com"
ALLOWED_ORIGINS = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", DEFAULT_ORIGINS).split(",") if o.strip()]

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": ALLOWED_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
        }
    },
)

app.register_blueprint(user_bp, url_prefix="/api")
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(assessment_bp, url_prefix="/api/assessment")
app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
app.register_blueprint(principles_bp, url_prefix="/api")
app.register_blueprint(purpose_discovery_bp, url_prefix="/api/purpose-discovery")
app.register_blueprint(mind_mapping_bp, url_prefix="/api/mind-mapping")
app.register_blueprint(value_zone_bp, url_prefix="/api/value-zone")
app.register_blueprint(ai_adoption_bp, url_prefix="/api/ai-adoption")
app.register_blueprint(enhanced_assessment_bp, url_prefix="/api/enhanced-assessment")

db_path = os.path.join(os.path.dirname(__file__), "database", "app.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
migrate = Migrate(app, db)

@app.route("/api/<path:any_path>", methods=["OPTIONS"])
def cors_preflight(any_path):
    return ("", 204)

@app.get("/", defaults={"path": ""})
@app.get("/<path:path>")
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    file_path = os.path.join(static_folder_path, path)
    if path != "" and os.path.exists(file_path):
        return send_from_directory(static_folder_path, path)

    index_path = os.path.join(static_folder_path, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(static_folder_path, "index.html")

    return "index.html not found", 404
