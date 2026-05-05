"""Main Flask application - Changepreneurship Platform API"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy import inspect
from werkzeug.middleware.proxy_fix import ProxyFix

from src.models.assessment import db
from src.models.benchmark_data import BenchmarkData  # noqa: F401 — register with SQLAlchemy
from src.models.external_connection import ExternalConnection  # noqa: F401
from src.models.data_consent_log import DataConsentLog  # noqa: F401
from src.models.venture import Venture  # noqa: F401
from src.models.market_research import CompetitorEntry, MarketContext, MarketValidityReport  # noqa: F401
from src.utils.limiter import limiter
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.assessment import assessment_bp
from src.routes.analytics import analytics_bp
from src.routes.principles import principles_bp
from src.routes.dashboard import dashboard_bp
from src.routes.ai_recommendations import ai_recommendations_bp
from src.routes.ai_routes import ai_bp
from src.routes.data_import import data_import_bp
from src.routes.phase1 import phase1_bp
from src.routes.phase2 import phase2_bp
from src.routes.phase3 import phase3_bp
from src.routes.phase4 import phase4_bp
from src.routes.phase5 import phase5_bp
from src.routes.phase6 import phase6_bp
from src.routes.phase7 import phase7_bp
from src.routes.venture_profile import venture_profile_bp
from src.routes.account import account_bp
from src.routes.routing import routing_bp
from src.routes.actions import actions_bp
from src.routes.progress import progress_bp
from src.routes.safety import safety_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "static"))
# Trust exactly 1 proxy (Caddy) so get_remote_address returns the real client IP
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

# Configuration — SECRET_KEY must be set via environment variable in production
_secret_key = os.getenv("SECRET_KEY")
if not _secret_key:
    if os.getenv("FLASK_ENV") == "production":
        raise RuntimeError("SECRET_KEY environment variable must be set in production")
    _secret_key = "dev-only-insecure-key-do-not-use-in-production"
    print("[WARNING] SECRET_KEY not set — using insecure dev key. Set SECRET_KEY in production!")
app.config["SECRET_KEY"] = _secret_key

# CORS Configuration
_flask_env = os.getenv("FLASK_ENV", "development")
if _flask_env == "production":
    DEFAULT_ORIGINS = ""  # in production, ALLOWED_ORIGINS must be explicitly set
else:
    DEFAULT_ORIGINS = "http://localhost:5173,http://localhost:5174,http://localhost:5175"
origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", DEFAULT_ORIGINS).split(",") if o.strip()]

if _flask_env == "production" and not origins:
    raise RuntimeError("ALLOWED_ORIGINS environment variable must be set in production")

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


@app.after_request
def set_security_headers(response):
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if os.getenv("FLASK_ENV") == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


_SENSITIVE_PATHS = ('/api/auth/', '/api/users')

@app.before_request
def audit_log():
    """Log all requests to sensitive auth/user endpoints."""
    if request.path.startswith(_SENSITIVE_PATHS):
        token = request.headers.get('Authorization', '')
        token_hint = token[7:14] + '...' if token.startswith('Bearer ') else 'cookie/none'
        app.logger.info(
            f"[AUDIT] {request.method} {request.path} "
            f"ip={request.remote_addr} token={token_hint}"
        )


@app.before_request
def csrf_origin_check():
    """In production, reject state-changing requests from unexpected origins."""
    if os.getenv('FLASK_ENV') != 'production':
        return
    if request.method in ('GET', 'HEAD', 'OPTIONS'):
        return
    allowed = set(origins)  # `origins` already defined above in CORS config
    origin = request.headers.get('Origin') or request.headers.get('Referer', '')
    if origin and not any(origin.startswith(o) for o in allowed):
        app.logger.warning(f"[CSRF] Blocked request from origin: {origin}")
        return jsonify({'error': 'Forbidden'}), 403

# Register blueprints
app.register_blueprint(user_bp, url_prefix="/api")
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(assessment_bp, url_prefix="/api/assessment")
app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
app.register_blueprint(principles_bp, url_prefix="/api")
app.register_blueprint(dashboard_bp)
app.register_blueprint(ai_recommendations_bp)
app.register_blueprint(ai_bp, url_prefix="/api/ai")
app.register_blueprint(data_import_bp, url_prefix="/api/data/import")
app.register_blueprint(phase1_bp, url_prefix="/api/v1")
app.register_blueprint(phase2_bp, url_prefix="/api/v1")
app.register_blueprint(phase3_bp, url_prefix="/api/v1")
app.register_blueprint(phase4_bp, url_prefix="/api/v1")
app.register_blueprint(phase5_bp, url_prefix="/api/v1")
app.register_blueprint(phase6_bp, url_prefix="/api/v1")
app.register_blueprint(phase7_bp, url_prefix="/api/v1")
app.register_blueprint(venture_profile_bp, url_prefix="/api/v1")
app.register_blueprint(account_bp, url_prefix="/api/v1")
app.register_blueprint(routing_bp, url_prefix="/api/v1")
app.register_blueprint(actions_bp, url_prefix="/api/v1")
app.register_blueprint(progress_bp, url_prefix="/api/v1")
app.register_blueprint(safety_bp, url_prefix="/api/v1")

# Database configuration
database_url = os.getenv("DATABASE_URL")
if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    # Fallback to SQLite for development without DATABASE_URL
    db_path = os.path.join(os.path.dirname(__file__), "database", "app.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_size": 10,
    "pool_recycle": 300,
    "pool_pre_ping": True,
    "max_overflow": 5,
}
db.init_app(app)
migrate = Migrate(app, db)
limiter.init_app(app)

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
@limiter.exempt
def health():
    return jsonify({"status": "ok"})
