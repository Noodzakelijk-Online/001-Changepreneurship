# Changepreneurship Platform - Complete Code Package

## Overview
This is the complete code package for the Changepreneurship platform - a comprehensive 7-part entrepreneurship assessment and business development platform with database integration and user authentication.

## Architecture
- **Frontend**: React.js with Vite, TailwindCSS, and shadcn/ui components
- **Backend**: Flask with SQLAlchemy ORM and SQLite database
- **Authentication**: JWT-like session tokens with secure password hashing
- **Database**: SQLite with comprehensive user, assessment, and profile models

## Features Implemented

### 🔐 Authentication System
- User registration with validation
- Secure login/logout functionality
- Session management with token-based authentication
- Password hashing with Werkzeug
- Protected routes and API endpoints

### 📊 Assessment Framework
- Complete 7-part entrepreneurship assessment
- Self-Discovery, Idea Discovery, Market Research, Business Pillars
- Product Concept Testing, Business Development, Business Prototype Testing
- Progress tracking and data persistence
- AI-powered recommendations

### 🗄️ Database Integration
- Comprehensive database schema
- User management and profiles
- Assessment progress tracking
- Response storage and retrieval
- Entrepreneur profile analytics

### 🎨 User Interface
- Professional dark theme with orange branding
- Responsive design for all devices
- Authentication modals and user profiles
- Progress tracking and phase navigation
- Silicon Valley startup-quality UI/UX

## File Structure

### Backend (Flask)
```
changepreneurship-backend/
├── src/
│   ├── main.py                 # Main Flask application
│   ├── models/
│   │   └── assessment.py       # Database models
│   ├── routes/
│   │   ├── auth.py            # Authentication routes
│   │   ├── assessment.py      # Assessment API routes
│   │   └── user.py            # User management routes
│   └── static/                # Frontend build files
├── requirements.txt           # Python dependencies
└── venv/                     # Virtual environment
```

### Frontend (React)
```
changepreneurship-enhanced/
├── src/
│   ├── App.jsx               # Main application component
│   ├── contexts/
│   │   ├── AuthContext.jsx   # Authentication context
│   │   └── AssessmentContext.jsx # Assessment state management
│   ├── components/
│   │   ├── auth/
│   │   │   ├── AuthModal.jsx     # Authentication modal
│   │   │   ├── LoginForm.jsx     # Login form component
│   │   │   └── RegisterForm.jsx  # Registration form component
│   │   ├── assessment/           # Assessment components
│   │   ├── LandingPage.jsx       # Main landing page
│   │   ├── UserProfile.jsx       # User profile dropdown
│   │   └── Dashboard.jsx         # User dashboard
│   └── App.css               # Global styles
├── package.json              # Node.js dependencies
└── dist/                     # Production build
```

## Setup Instructions

### Backend Setup
1. Navigate to `changepreneurship-backend/`
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Run the application: `python src/main.py`
6. Backend will be available at `http://localhost:5000`

### Frontend Setup
1. Navigate to `changepreneurship-enhanced/`
2. Install dependencies: `npm install`
3. For development: `npm run dev`
4. For production build: `npm run build`
5. Frontend will be available at `http://localhost:5173` (dev) or served by Flask backend

### Database
- SQLite database is automatically created on first run
- Database file: `src/database/app.db`
- All tables are created automatically using SQLAlchemy migrations

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/verify` - Session verification
- `GET /api/auth/profile` - Get user profile

### Assessment
- `GET /api/assessment/phases` - Get all assessment phases with progress
- `POST /api/assessment/start/<phase_id>` - Start assessment phase
- `POST /api/assessment/<id>/response` - Save assessment response
- `PUT /api/assessment/<id>/progress` - Update assessment progress
- `GET /api/assessment/<id>/responses` - Get assessment responses
- `PUT /api/assessment/profile/update` - Update entrepreneur profile

## Database Schema

### Users Table
- User authentication and profile information
- Password hashing and session management
- Timestamps for creation and last login

### Assessments Table
- Assessment progress tracking across all 7 phases
- JSON data storage for complex assessment information
- Progress percentages and completion status

### Assessment Responses Table
- Individual question responses with metadata
- Support for multiple response types (text, multiple choice, scale, matrix)
- Timestamps for response tracking

### Entrepreneur Profile Table
- Comprehensive profile with assessment results
- AI analysis results and recommendations
- Business planning data and insights

## Security Features
- Password hashing with Werkzeug
- Secure session tokens (32-byte URL-safe)
- CORS configuration for cross-origin requests
- Input validation and sanitization
- Session expiration management

## Deployment
- Backend: Flask application ready for production deployment
- Frontend: Static build files can be served by any web server
- Database: SQLite for development, easily upgradeable to PostgreSQL/MySQL
- Environment: Configured for both development and production

## Live Demo
The platform is currently deployed and accessible at:
**https://5000-i0dlqt7t67jcvprs9lflc-e0f5bbcf.manusvm.computer**

## Key Features
- ✅ Complete 7-part entrepreneurship assessment framework
- ✅ User authentication and session management
- ✅ Database integration with persistent data storage
- ✅ Professional UI/UX with responsive design
- ✅ AI-powered recommendations and insights
- ✅ Progress tracking and assessment analytics
- ✅ Secure API with comprehensive error handling

## Next Steps
The platform is ready for:
1. Assessment progress tracking integration (Phase 3)
2. User dashboard with historical data (Phase 4)
3. Production deployment and scaling (Phase 5)

This codebase provides a complete, production-ready entrepreneurship assessment platform with modern web technologies and best practices.

