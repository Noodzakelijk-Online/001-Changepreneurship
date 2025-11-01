# Quick Start - Installation Instructions

## 🪟 Windows Users

### Before You Start - ONE TIME ONLY!

Open **PowerShell as Administrator** and run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Type `Y` and press Enter when prompted.

> ℹ️ This is a one-time security setting to allow script execution.

### Installation Steps

1. **Install Prerequisites**:
   - [Docker Desktop](https://www.docker.com/products/docker-desktop) - Install and start it
   - [Git for Windows](https://git-scm.com/download/win) - Install with defaults

2. **Download the installer**:
   - Download `install-changepreneurship.ps1` from this repository
   - Right-click the file → **Run with PowerShell**
   - Click **Yes** when asked for Administrator permission

3. **Wait for installation** (3-5 minutes on first run)

4. **Browser will open automatically** at http://localhost:5173

**That's it!** The script handles everything automatically.

---

### 📖 Full Documentation

For detailed setup, troubleshooting, and manual installation, see [WINDOWS_SETUP.md](WINDOWS_SETUP.md)

### 🔧 Quick Commands

After installation, open PowerShell in `C:\Program Files\Changepreneurship`:

```powershell
# View logs
docker compose logs -f

# Stop
docker compose down

# Restart
docker compose restart

# Update to latest
git pull origin main; docker compose up -d --build
```

---

## 🐧 Linux / 🍎 macOS Users

### Quick Start

```bash
# Clone repository
git clone https://github.com/Noodzakelijk-Online/001-Changepreneurship.git
cd 001-Changepreneurship

# Start services
docker compose up -d --build

# Open browser
open http://localhost:5173  # macOS
xdg-open http://localhost:5173  # Linux
```

### Prerequisites

- Docker & Docker Compose
- Git

For detailed setup, see [README.md](README.md)

---

## 🌐 Access Points

Once running:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health

---

## ❓ Need Help?

- Windows setup issues? → [WINDOWS_SETUP.md](WINDOWS_SETUP.md)
- General documentation → [README.md](README.md)
- Docker issues → Check Docker Desktop is running
- Port conflicts → See troubleshooting in WINDOWS_SETUP.md
