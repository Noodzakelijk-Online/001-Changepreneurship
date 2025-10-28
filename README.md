# Changepreneurship Platform - Complete Codebase

## 🎉 **Complete 7-Part Entrepreneurship Assessment Platform**

This package contains the complete, production-ready Changepreneurship platform with database integration, user authentication, and comprehensive analytics.

## 🌐 **Live Demo**

**Current Deployment**: https://ogh5izc8jkq6.manus.space

## 📦 **Package Contents**

### **Backend (Flask) - `changepreneurship-backend/`**

- **Complete REST API** with authentication and assessment endpoints
- **SQLite Database** with comprehensive schema
- **User Management** with secure session handling
- **Assessment Progress Tracking** and data persistence
- **Analytics API** for dashboard insights

### **Frontend (React) - `changepreneurship-enhanced/`**

- **Complete 7-part assessment framework**
- **User authentication** with beautiful modals
- **Real-time progress tracking** across all phases
- **Analytics dashboard** with comprehensive insights
- **Professional UI/UX** with dark theme and orange branding

## 🚀 **Key Features**

### **✅ Complete Assessment Framework:**

1. **Self-Discovery Assessment** - Entrepreneurial personality analysis
2. **Idea Discovery** - Business opportunity identification
3. **Market Research** - Competitive analysis and validation
4. **Business Pillars Planning** - Comprehensive business plan development
5. **Product Concept Testing** - Market acceptability and pricing validation
6. **Business Development** - Strategic decision-making and resource alignment
7. **Business Prototype Testing** - Complete business model validation

### **✅ Database Integration:**

- **User Registration/Login** with secure authentication (username or email)
- **Session Management** with persistent login
- **Assessment Progress** automatically saved to database
- **Cross-device Continuity** - users can continue on any device
- **Data Export** capabilities for users

### **✅ Advanced Features:**

- **AI-Powered Recommendations** with success probability analysis
- **User Dashboard** with comprehensive analytics
- **Progress Tracking** across all 7 phases
- **Authentication Bypass Mode** for testing (configurable)
- **Responsive Design** works on all devices
- **Redis-backed Caching** for session tokens and principles dataset
- **PostgreSQL-ready** with automated Alembic migrations on container start
- **Healthcheck Endpoints & Docker Healthchecks** for observability
- **SPA Routing via BrowserRouter + nginx fallback** in production container

## 🛠️ **Setup Instructions**

### **Backend Setup:**

```bash
cd changepreneurship-backend/
python -m venv venv
.\.venv\Scripts\Activate.ps1

source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
pip install -r requirements.txt
flask --app src.main db upgrade  # Apply database migrations
python src/main.py
```

### **Database Migrations:**

```bash
# Generate a new migration after model changes
flask --app src.main db migrate -m "describe changes"


# Apply migrations to the database
flask --app src.main db upgrade

flask db upgrade
```

### **Frontend Setup:**

```bash
cd changepreneurship-enhanced/
npm install
npm run dev  # Development server
npm run build  # Production build
```

### **Full-Stack Deployment:**

1. Build the React frontend: `npm run build`
2. Copy build files to Flask static directory: `cp -r dist/* ../changepreneurship-backend/src/static/`
3. Run Flask backend: `python src/main.py`
4. Access at: `http://localhost:5000`

## 🔧 **Configuration Options**

### **Authentication Bypass (Testing Mode):**

In `/changepreneurship-enhanced/src/contexts/AuthContext.jsx`:

- Set `BYPASS_AUTH = true` for testing (no login required)
- Set `BYPASS_AUTH = false` for production (normal authentication)

### **Database Configuration:**

In `/changepreneurship-backend/src/main.py`:

- SQLite database automatically created as `assessment.db`
- Modify database URI for PostgreSQL/MySQL if needed

### **API Configuration:**

In `/changepreneurship-enhanced/src/services/api.js`:

- Update `BASE_URL` for production deployment
- Configure CORS settings in Flask backend

## 📊 **Database Schema**

### **Core Tables:**

- **users** - User accounts and authentication
- **user_sessions** - Session management
- **entrepreneur_profiles** - Assessment results and archetypes
- **assessments** - Assessment progress tracking
- **assessment_responses** - Individual question responses

### **Key Features:**

- **Automatic table creation** on first run
- **JSON field support** for complex data structures
- **Cascade delete** for data integrity
- **Timestamp tracking** for all records

## 🎯 **Testing Guide**

### **Direct Phase Access (Recommended for Testing):**

- **Phase 1**: `/assessment?phase=1` (Self Discovery)
- **Phase 2**: `/assessment?phase=2` (Idea Discovery)
- **Phase 3**: `/assessment?phase=3` (Market Research)
- **Phase 4**: `/assessment?phase=4` (Business Pillars)
- **Phase 5**: `/assessment?phase=5` (Product Concept Testing)
- **Phase 6**: `/assessment?phase=6` (Business Development)
- **Phase 7**: `/assessment?phase=7` (Business Prototype Testing)

### **User Dashboard:**

- Access at `/user-dashboard` (requires authentication)
- View progress, analytics, and insights
- Export assessment data

### **AI Recommendations:**

- Access at `/ai-recommendations`
- View success probability and personalized insights

## 🔐 **Security Features**

### **Authentication:**

- **Password hashing** with Werkzeug
- **Secure session tokens** (32-byte URL-safe)
- **Session expiration** management
- **Email validation** and password strength requirements

### **API Security:**

- **CORS configuration** for cross-origin requests
- **Protected routes** requiring authentication
- **Input validation** and sanitization
- **Error handling** without information leakage

## 📈 **Analytics & Insights**

### **User Analytics:**

- **Progress tracking** across all 7 phases
- **Time investment** monitoring
- **Completion rates** and milestones
- **Achievement system** with unlockable badges

### **Assessment Analytics:**

- **Response analysis** and pattern recognition
- **Success probability** calculation
- **Entrepreneur archetype** determination
- **Personalized recommendations** based on progress

## 🚀 **Deployment Options**

### **Local Development:**

- Flask development server on `localhost:5000`
- React development server on `localhost:5173`

### **Production Deployment:**

- **Docker / docker-compose** (recommended) – orchestrates PostgreSQL, Redis, backend (gunicorn), and frontend (nginx)
- **Heroku / Render** – Use gunicorn + auto migrations (adapt entrypoint)
- **AWS/GCP** – Container images or managed services
- **Vercel/Netlify** – Frontend only (configure `VITE_API_BASE` to backend URL)

### **Docker Quick Start**

```
cp .env.example .env   # Adjust secrets as needed
docker compose up --build
```

Services:
* Backend API: http://localhost:5000 (health: /api/health)
* Frontend SPA: http://localhost:5173
* PostgreSQL: localhost:5433 (internal service name: postgres)
* Redis: localhost:6380

Automations:
* wait_for_db + Alembic upgrade runs before gunicorn starts
* Healthchecks ensure dependency readiness sequencing

Caching Layers:
* Sessions: Redis keys `session:<token>` (30 day TTL)
* Principles queries: Redis keys `json:principles:...` (1–5 min TTL depending on query)

SPA Routing:
* Frontend uses BrowserRouter; nginx config (`nginx.conf`) handles `try_files` fallback to index.html.

### ▶️ Running WITHOUT Docker (Parity Notes)

You can run the backend and frontend locally without containers. Behavior is equivalent provided you follow these steps:

1. Choose your database:
	* SQLite (default): No action needed. On first run the backend will auto-create tables (only for SQLite) and you can ignore migrations for quick prototyping.
	* PostgreSQL (recommended): Set `DATABASE_URL` and run the migration bootstrap script BEFORE starting the dev server.

2. Environment variables (create `.env` or export in shell):
	* `DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/cp_db`
	* `SECRET_KEY=your-dev-secret`
	* `ALLOWED_ORIGINS=http://localhost:5173`
	* (Optional) `REDIS_URL=redis://localhost:6379/0` for session + principles caching.

3. Start services:
	* Postgres: Ensure the database exists (e.g. `createdb cp_db`).
	* Redis (optional but recommended): `redis-server` (or Docker `redis:alpine`).

4. Install backend deps & run migration bootstrap (this replicates container entrypoint logic):
	```powershell
	cd changepreneurship-backend
	python -m venv .venv; .venv\Scripts\Activate.ps1
	pip install -r requirements.txt
	# Idempotent bootstrap (stamps legacy schema or upgrades normally)
	python migrate_upgrade.py
	# Run dev server
	python run_dev.py
	```
	If you prefer classic Flask-Migrate workflow on a fresh Postgres DB you can instead do:
	```powershell
	flask --app src.main db upgrade
	python run_dev.py
	```

5. Frontend:
	```powershell
	cd changepreneurship-enhanced
	pnpm install  # or npm install
	pnpm run dev  # http://localhost:5173
	```

6. API base URL configuration:
	* If the frontend expects a different base, set `VITE_API_BASE=http://localhost:5000` when running `pnpm run dev`.

7. Registration & migrations safety:
	* Re-running `python migrate_upgrade.py` is safe; it detects if `alembic_version` exists and only performs a normal upgrade.
	* For a legacy DB created before Alembic (tables but no `alembic_version`), the script stamps the base revision then patches differences (e.g. enlarging `password_hash`) and marks head.

8. Troubleshooting:
	* Password length errors -> ensure latest migration head applied (`python migrate_upgrade.py`).
	* Duplicate table errors -> confirm you are not invoking `db.create_all()` on Postgres (code already skips it). Remove any manual create scripts.
	* Connection refused -> check `DATABASE_URL`, Postgres running, and firewall/port 5432.

Summary: Outside Docker the only extra step vs. containers is to call `python migrate_upgrade.py` manually (the Docker entrypoint does this automatically). All other runtime behavior (CORS, caching, routes, migrations) is identical.

## 📝 **File Structure**

```
changepreneurship-final-package/
├── changepreneurship-backend/          # Flask Backend
│   ├── src/
│   │   ├── main.py                     # Main Flask application
│   │   ├── models/                     # Database models
│   │   │   ├── user.py                 # User model
│   │   │   └── assessment.py           # Assessment models
│   │   ├── routes/                     # API routes
│   │   │   ├── auth.py                 # Authentication endpoints
│   │   │   ├── assessment.py           # Assessment endpoints
│   │   │   └── analytics.py            # Analytics endpoints
│   │   └── static/                     # Frontend build files
│   ├── requirements.txt                # Python dependencies
│   └── venv/                          # Virtual environment
├── changepreneurship-enhanced/         # React Frontend
│   ├── src/
│   │   ├── components/                 # React components
│   │   │   ├── assessment/             # Assessment components
│   │   │   ├── auth/                   # Authentication components
│   │   │   ├── dashboard/              # Dashboard components
│   │   │   └── ui/                     # UI components
│   │   ├── contexts/                   # React contexts
│   │   │   ├── AuthContext.jsx         # Authentication state
│   │   │   └── AssessmentContext.jsx   # Assessment state
│   │   ├── services/                   # API services
│   │   │   └── api.js                  # Backend API client
│   │   ├── hooks/                      # Custom hooks
│   │   │   └── useAssessmentAPI.js     # Assessment API hook
│   │   ├── App.jsx                     # Main application
│   │   └── main.jsx                    # Application entry point
│   ├── package.json                    # Node.js dependencies
│   ├── vite.config.js                  # Vite configuration
│   └── dist/                          # Production build
└── README.md                          # This file
```

## 🎯 **Next Steps**

### **Immediate:**

1. **Test all 7 assessment phases** using direct URLs
2. **Verify user authentication** and session management
3. **Check database integration** and data persistence
4. **Review analytics dashboard** functionality

### **Production Deployment:**

1. **Configure production database** (PostgreSQL recommended)
2. **Set up environment variables** for sensitive data
3. **Configure domain and SSL** certificates
4. **Set up monitoring** and logging
5. **Implement backup strategy** for user data

### **Future Enhancements:**

1. **Email integration** for assessment results
2. **Payment processing** for premium features
3. **Mobile app** development
4. **Advanced analytics** and reporting
5. **Integration** with business tools and CRMs

## 📞 **Support**

This is a complete, production-ready entrepreneurship assessment platform with comprehensive documentation and setup instructions. All components have been tested and verified to work correctly.

**Platform Status**: ✅ Fully Operational
**Last Updated**: October 2025
**Version**: 2.1 (Docker, Redis Caching, Healthchecks)

---

🎉 **Your complete Changepreneurship platform is ready for deployment and real-world use!** 🎉
