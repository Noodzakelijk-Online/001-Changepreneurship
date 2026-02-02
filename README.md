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

### **🐳 Docker Deployment (Recommended)**

**Prerequisites:**
- Docker Desktop installed and running
- 4GB+ RAM available
- Ports 80, 5000, 5432, 6379 available

**Quick Start:**
```bash
# 1. Clone repository
git clone https://github.com/Noodzakelijk-Online/001-Changepreneurship.git
cd 001-Changepreneurship

# 2. Configure environment
# Edit .env file with your settings (GROQ_API_KEY, SECRET_KEY, etc.)

# 3. Start the stack
docker-compose up -d

# 4. Check status
docker-compose ps

# 5. View logs
docker-compose logs -f

# 6. Create test user (optional)
docker exec changepreneurship-backend python create_complete_sarah_chen.py
```

**Access the application:**
- Frontend: http://localhost
- Backend API: http://localhost:5000
- API Docs: http://localhost:5000/api/docs

**Test Login:**
- Username: `sarah_chen_founder`
- Password: `Test1234!`

### **Database Migrations (Inside Docker):**

```bash
# Apply migrations
docker exec changepreneurship-backend flask db upgrade

# Generate new migration (after model changes)
docker exec changepreneurship-backend flask db migrate -m "describe changes"
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

## 🚀 **Deployment**

### **🐳 Docker (Recommended - Production Ready)**

**Complete stack with PostgreSQL, Redis, Backend, and Frontend:**

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your GROQ_API_KEY, SECRET_KEY, etc.

# 2. Start the stack
docker-compose up -d

# 3. Check services
docker-compose ps
```

**Services:**
- Frontend (nginx): http://localhost
- Backend API: http://localhost:5000 (health: /api/health)
- PostgreSQL: localhost:5432 (internal: postgres:5432)
- Redis: localhost:6379 (internal: redis:6379)

**Automations:**
- Database migrations run automatically on backend startup
- Health checks ensure dependency readiness
- Session caching via Redis (30 day TTL)
- Principles dataset caching (1-5 min TTL)

**SPA Routing:**
- Frontend uses BrowserRouter
- nginx.conf handles `try_files` fallback to index.html

**Useful Commands:**
```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart services
docker-compose restart backend

# Rebuild after code changes
docker-compose build --no-cache backend
docker-compose up -d

# Run migrations manually
docker exec changepreneurship-backend flask db upgrade

# Create test user
docker exec changepreneurship-backend python create_complete_sarah_chen.py

# Stop everything
docker-compose down
```

### **☁️ Cloud Deployment**

- **Heroku / Render** – Use gunicorn + auto migrations (adapt entrypoint)
- **AWS/GCP** – Deploy container images or use managed services
- **Vercel/Netlify** – Frontend only (configure `VITE_API_BASE` to backend URL)

**Note:** Local venv development is deprecated. Use Docker for consistent environment.
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
