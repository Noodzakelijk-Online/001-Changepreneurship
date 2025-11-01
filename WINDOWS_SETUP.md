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

**IMPORTANT**: Before running the installation script for the first time, you must enable PowerShell script execution.

Open **PowerShell as Administrator** (right-click PowerShell → Run as Administrator) and run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

When prompted, type `Y` and press Enter.

> **What does this do?** This allows PowerShell to run scripts that you've downloaded or created. It's a one-time security setting.

## 📥 Installation

### Option 1: Download and Run

1. Download `install-changepreneurship.ps1` from the repository
2. Right-click the file → **Run with PowerShell**
3. If prompted for Administrator access, click **Yes**

### Option 2: Clone Repository First

If you already have the repository:

```powershell
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

### "Running scripts is disabled on this system"

Run this command as Administrator:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
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
