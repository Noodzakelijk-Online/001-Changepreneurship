# 🐳 Quick Start - Docker Only

**Changepreneurship Platform** is now **Docker-first**. All development and production deployments use Docker Compose.

## Prerequisites

- **Docker Desktop** installed and running
- **4GB+ RAM** available
- Ports **80, 5000, 5432, 6379** available

## 🚀 Start in 3 Steps

### 1. Configure Environment

```bash
cd E:\GIT\001-Changepreneurship
cp .env.example .env
```

Edit `.env` and add your **GROQ_API_KEY** (get free key at https://console.groq.com):

```env
GROQ_API_KEY=gsk_your_key_here
SECRET_KEY=changepreneurship-production-secret-key
```

### 2. Start Docker Stack

```bash
docker-compose up -d
```

This starts:
- ✅ PostgreSQL database (port 5432)
- ✅ Redis cache (port 6379)
- ✅ Flask backend with Groq AI (port 5000)
- ✅ React frontend (port 80)

### 3. Create Test User

```bash
docker exec changepreneurship-backend python create_complete_sarah_chen.py
```

## 🎯 Access the Platform

**Frontend:** http://localhost

**Test Login:**
- Username: `sarah_chen_founder`
- Password: `Test1234!`

**Backend API:** http://localhost:5000/api/health

## 📊 Check Status

```bash
# View all containers
docker-compose ps

# View backend logs
docker-compose logs -f backend

# View all logs
docker-compose logs -f
```

## 🔧 Common Commands

### Restart Services
```bash
docker-compose restart backend
docker-compose restart frontend
```

### Rebuild After Code Changes
```bash
docker-compose build --no-cache backend
docker-compose up -d
```

### Run Database Migrations
```bash
docker exec changepreneurship-backend flask db upgrade
```

### Stop Everything
```bash
docker-compose down
```

### Clean Restart
```bash
docker-compose down -v  # Warning: Deletes database!
docker-compose up -d
```

## 🤖 Groq AI Integration

The platform uses **Groq's free LLM API** (Llama 3.3 70B) for:
- Executive Summary generation
- Personalized business insights
- Assessment analysis

**Free tier limits:**
- 30 requests/minute
- 14,400 requests/day

Get your free API key: https://console.groq.com

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Check what's using port 80
netstat -ano | findstr :80

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### Database Connection Error
```bash
# Restart PostgreSQL container
docker-compose restart postgres

# Check PostgreSQL logs
docker-compose logs postgres
```

### Backend Not Starting
```bash
# View backend logs
docker-compose logs backend

# Common fix: rebuild without cache
docker-compose build --no-cache backend
docker-compose up -d
```

### Frontend Not Loading
```bash
# Check nginx logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build --no-cache frontend
docker-compose up -d
```

## 📁 Project Structure

```
E:\GIT\001-Changepreneurship\
├── docker-compose.yml          # Orchestration config
├── .env                        # Environment variables
├── changepreneurship-backend/  # Flask API + Groq AI
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── src/
│   │   ├── main.py
│   │   ├── models/
│   │   ├── routes/
│   │   └── services/
│   │       └── llm_client.py   # Groq integration
│   └── migrations/
├── changepreneurship-enhanced/ # React frontend
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── src/
└── create_complete_sarah_chen.py  # Test user script
```

## ⚠️ Important Notes

- **No venv required** - Everything runs in Docker
- **Database persistence** - Data stored in Docker volumes on E: drive
- **Automatic migrations** - Run on backend container startup
- **Development workflow** - Edit code, rebuild container, restart

## 🎓 Next Steps

1. ✅ Login with test user
2. ✅ Explore dashboard and assessments
3. ✅ View AI-generated Executive Summary
4. ✅ Check backend API at http://localhost:5000/api/docs
5. ✅ Customize GROQ_API_KEY for your own insights

---

**For detailed documentation, see:**
- `README.md` - Full platform overview
- `GROQ_AI_INTEGRATION.md` - AI implementation details
- `PRODUCTION_STATUS.md` - Deployment guide
