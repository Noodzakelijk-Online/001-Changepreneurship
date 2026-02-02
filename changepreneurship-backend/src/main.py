"""Main Flask application - Changepreneurship Platform API"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy import inspect

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
from src.routes.dashboard import dashboard_bp
from src.routes.ai_recommendations import ai_recommendations_bp
from src.routes.ai_routes import ai_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "static"))

# Configuration
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "changepreneurship-secret-key-2024-secure")

# CORS Configuration
DEFAULT_ORIGINS = "http://localhost:5173,http://localhost:5174,http://localhost:5175,https://changepreneurship-1.onrender.com"
origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", DEFAULT_ORIGINS).split(",") if o.strip()]

print(f"[Startup] CORS ALLOWED_ORIGINS => {origins}")

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
        }
    },
)

# Register blueprints
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
app.register_blueprint(dashboard_bp)
app.register_blueprint(ai_recommendations_bp)
app.register_blueprint(ai_bp, url_prefix="/api/ai")

# Database configuration
database_url = os.getenv("DATABASE_URL")
if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    # Fallback to SQLite for development without DATABASE_URL
    db_path = os.path.join(os.path.dirname(__file__), "database", "app.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
migrate = Migrate(app, db)

# Auto-create tables for SQLite only
with app.app_context():
    try:
        engine_name = db.engine.url.get_backend_name()
        if engine_name == 'sqlite':
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            if not tables:
                print("[Startup] SQLite: No tables found, creating...")
                db.create_all()
            else:
                required = {"user", "entrepreneur_profile", "user_session"}
                missing = required.difference(tables)
                if missing:
                    print(f"[Startup] SQLite: Missing {missing}, creating...")
                    db.create_all()
        else:
            print(f"[Startup] Using {engine_name}, skipping auto-create (use migrations)")
    except Exception as e:
        print(f"[Startup] DB init error: {e}")


@app.route("/api/<path:any_path>", methods=["OPTIONS"])
def cors_preflight(any_path):
    """Handle CORS preflight requests"""
    return ("", 204)

@app.get("/", defaults={"path": ""})
@app.get("/<path:path>")
def serve(path):
    # API routes return 404 JSON
    if path.startswith("api/"):
        return jsonify({"error": "Endpoint not found"}), 404
    
    # Serve static files for frontend
    static_folder_path = app.static_folder
    if static_folder_path and os.path.exists(static_folder_path):
        file_path = os.path.join(static_folder_path, path)
        if path and os.path.exists(file_path):
            return send_from_directory(static_folder_path, path)
        
        index_path = os.path.join(static_folder_path, "index.html")
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, "index.html")
    
    return jsonify({"error": "Not found"}), 404


@app.get('/api/health')
def health():
    return jsonify({"status": "ok"})
