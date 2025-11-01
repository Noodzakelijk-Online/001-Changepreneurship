# 🚀 Changepreneurship - Quick Start Guide

## Installation (First Time Only)

1. **Right-click** `Install Changepreneurship.bat`
2. Select **"Run as administrator"**
3. Wait 5 minutes
4. Browser opens automatically

## Creating Test User

After installation, **double-click** `Create Test User.bat`

Or visit: http://localhost:5000/api/dashboard/complete-user/create

**Login with:**
- Username: `sarah_chen_founder`
- Password: `test123`

This gives you a fully populated demo account with 100% completion!

## Access URLs

- **App**: http://localhost:5173
- **API**: http://localhost:5000
- **Health**: http://localhost:5000/api/health

## Useful Commands

Run from `C:\Program Files\Changepreneurship`:

```powershell
# View logs
docker compose logs -f

# Stop services
docker compose down

# Restart
docker compose restart

# Update to latest
git pull origin main
docker compose up -d --build
```

## Troubleshooting

**Services not starting?**
- Ensure Docker Desktop is running
- Check logs: `docker compose logs`

**Can't login?**
- Create test user first (see above)
- Or register a new account

**Port conflicts?**
- Check what's using ports 5173 and 5000
- Stop conflicting services

## Need Help?

Check `WINDOWS_SETUP.md` for detailed documentation.
