# Changepreneurship - Windows Setup Guide

## 📋 Prerequisites

Before running the installation script, you need:

1. **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop)
   - Install and start Docker Desktop
   - Wait until the Docker icon in system tray shows "Docker Desktop is running"

2. **Git for Windows** - [Download here](https://git-scm.com/download/win)
   - Install with default options

3. **Administrator Access** - You'll need to run PowerShell as Administrator

## 🚀 One-Time Setup (First Time Only)

**No special setup required!** Just make sure Docker Desktop and Git are installed.

The installer automatically handles PowerShell execution policy using `-ExecutionPolicy Bypass`.

## 📥 Installation

### Easy Installation (Recommended)

1. Download or clone this repository
2. **Right-click** `Install Changepreneurship.bat`
3. Select **"Run as administrator"**
4. Wait for installation to complete
5. Browser opens automatically

### Alternative: Using PowerShell Directly

If you prefer PowerShell:

```powershell
# Run as Administrator
cd path\to\001-Changepreneurship
.\install-changepreneurship.ps1
```

## 🎯 What the Script Does

The installation script will automatically:

1. ✅ Check for required software (Docker, Git)
2. 📁 Create installation directory at `C:\Program Files\Changepreneurship`
3. 📦 Clone/update the repository from GitHub
4. 🐳 Build and start Docker containers
5. ⏳ Wait for all services to be healthy
6. 🌐 Open your browser to the application

## 🔧 Manual Installation (Alternative)

If you prefer to install manually:

```powershell
# 1. Create directory
New-Item -Path "C:\Program Files\Changepreneurship" -ItemType Directory -Force
cd "C:\Program Files\Changepreneurship"

# 2. Clone repository
git clone https://github.com/Noodzakelijk-Online/001-Changepreneurship.git .

# 3. Start services
docker compose up -d --build

# 4. Open browser
Start-Process "http://localhost:5173"
```

## 🌐 Accessing the Application

Once installation is complete:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health

### 🧪 Creating Test User

To demonstrate the platform with full data, create the Sarah Chen test user:

**Double-click** `Create Test User.bat` or run:
```powershell
curl -X POST http://localhost:5000/api/dashboard/complete-user/create
```

Then login with:
- **Username**: `sarah_chen_founder`
- **Password**: `test123`

This user has 100% completion across all 7 assessments with realistic business data.

## 🛠️ Useful Commands

After installation, navigate to the installation directory:

```powershell
cd "C:\Program Files\Changepreneurship"
```

### View Logs
```powershell
docker compose logs -f
```

### Stop Services
```powershell
docker compose down
```

### Restart Services
```powershell
docker compose restart
```

### Check Service Status
```powershell
docker compose ps
```

### Update to Latest Version
```powershell
git pull origin main
docker compose up -d --build
```

### Complete Cleanup (Remove All Data)
```powershell
docker compose down -v
```

## ❌ Troubleshooting

### "Administrator Rights Required" message

The batch file detected you need admin rights:
1. **Right-click** `Install Changepreneurship.bat`
2. Select **"Run as administrator"**
3. Click **Yes** when prompted

### "Running scripts is disabled on this system"

This shouldn't happen with the `.bat` installer. If you see this while running `.ps1` directly:
```powershell
PowerShell -ExecutionPolicy Bypass -File install-changepreneurship.ps1
```

### "Docker daemon is not running"

1. Start Docker Desktop from Start Menu
2. Wait for the Docker icon to show "Docker Desktop is running"
3. Run the script again

### "Cannot connect to Docker daemon"

1. Ensure Docker Desktop is installed
2. Restart Docker Desktop
3. Check if Docker is starting correctly in Docker Desktop → Troubleshoot

### Services Not Starting

View detailed logs:
```powershell
cd "C:\Program Files\Changepreneurship"
docker compose logs
```

### Port Already in Use

If ports 5173 or 5000 are already in use:
```powershell
# Find what's using the port
netstat -ano | findstr :5173
netstat -ano | findstr :5000

# Kill the process (replace PID with the actual process ID)
taskkill /PID <PID> /F
```

### Fresh Install

To completely remove and reinstall:
```powershell
# Stop and remove containers
cd "C:\Program Files\Changepreneurship"
docker compose down -v

# Remove installation directory
Remove-Item -Recurse -Force "C:\Program Files\Changepreneurship"

# Run installation script again
```

## 🔐 Firewall & Antivirus

If you have issues:

1. **Windows Firewall**: May prompt to allow Docker - click **Allow**
2. **Antivirus**: May need to whitelist:
   - `C:\Program Files\Changepreneurship`
   - Docker Desktop
   - PowerShell scripts

## 📊 System Requirements

- **OS**: Windows 10/11 (64-bit)
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 5GB free space
- **Processor**: 64-bit processor with virtualization support

## 🔄 Uninstallation

To completely remove Changepreneurship:

```powershell
# 1. Stop and remove containers
cd "C:\Program Files\Changepreneurship"
docker compose down -v

# 2. Remove Docker images (optional)
docker image rm changepreneurship-backend changepreneurship-frontend

# 3. Remove installation directory
Remove-Item -Recurse -Force "C:\Program Files\Changepreneurship"
```

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. View container logs: `docker compose logs`
3. Check Docker Desktop for errors
4. Create an issue on GitHub with:
   - Error messages
   - Output from `docker compose ps`
   - Output from `docker compose logs`

## 🎉 Success!

Once everything is running, you should see:

```
═══════════════════════════════════════════════════════
  🎉 Changepreneurship Platform is running!
═══════════════════════════════════════════════════════

Services:
  Frontend:  http://localhost:5173
  Backend:   http://localhost:5000
  API Docs:  http://localhost:5000/api/health
```

Visit http://localhost:5173 in your browser to start using the platform!
