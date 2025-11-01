@echo off
:: Changepreneurship Platform Installer
:: Double-click this file to install and start the platform

title Changepreneurship Installer

:: Check if running as Administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo ========================================
    echo   Administrator Rights Required
    echo ========================================
    echo.
    echo This installer needs Administrator access.
    echo.
    echo Right-click this file and select:
    echo "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Changepreneurship Platform Installer
echo ========================================
echo.

:: Set installation path
set "INSTALL_PATH=C:\Program Files\Changepreneurship"
set "REPO_URL=https://github.com/Noodzakelijk-Online/001-Changepreneurship.git"

:: Check for Git
git --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Git is not installed.
    echo.
    echo Please install Git from: https://git-scm.com/download/win
    echo.
    start https://git-scm.com/download/win
    pause
    exit /b 1
)

:: Check for Docker
docker --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Docker is not installed.
    echo.
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    echo.
    start https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

:: Check if Docker is running
docker ps >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Docker is not running.
    echo.
    echo Please start Docker Desktop and wait for it to be ready.
    echo Then run this installer again.
    echo.
    pause
    exit /b 1
)

echo [OK] Prerequisites check passed
echo.

:: Create installation directory
echo Creating installation directory...
if not exist "%INSTALL_PATH%" (
    mkdir "%INSTALL_PATH%"
)

:: Navigate to installation directory
cd /d "%INSTALL_PATH%"

:: Clone or update repository
if exist ".git" (
    echo Updating repository...
    git fetch origin >nul 2>&1
    git reset --hard origin/main >nul 2>&1
    git pull origin main
) else (
    echo Cloning repository from GitHub...
    git clone %REPO_URL% .
)

if %errorLevel% neq 0 (
    echo.
    echo [ERROR] Failed to clone/update repository
    echo.
    pause
    exit /b 1
)

echo [OK] Repository ready
echo.

:: Stop existing containers
echo Checking for existing containers...
docker compose ps -q >nul 2>&1
if %errorLevel% equ 0 (
    echo Stopping existing containers...
    docker compose down >nul 2>&1
)

:: Start Docker containers
echo.
echo Starting Docker containers...
echo This may take a few minutes on first run...
echo.

docker compose up -d --build

if %errorLevel% neq 0 (
    echo.
    echo [ERROR] Failed to start containers
    echo.
    echo Run this command to see logs:
    echo   cd "%INSTALL_PATH%" ^&^& docker compose logs
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Containers started
echo.

:: Wait for services
echo Waiting for services to be ready...
timeout /t 10 /nobreak >nul

:: Check if frontend is accessible
echo Checking frontend accessibility...
set "FRONTEND_URL=http://localhost:5173"
set /a count=0
:CheckFrontend
set /a count+=1
if %count% gtr 15 goto FrontendTimeout

powershell -Command "try { $response = Invoke-WebRequest -Uri '%FRONTEND_URL%' -Method Head -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; exit 0 } catch { exit 1 }"
if %errorLevel% equ 0 goto FrontendReady

timeout /t 2 /nobreak >nul
goto CheckFrontend

:FrontendTimeout
echo [WARNING] Frontend may still be starting up
goto OpenBrowser

:FrontendReady
echo [OK] Frontend is ready

:OpenBrowser
echo.
echo Creating test user...
echo.

:: Create Sarah Chen test user via API
powershell -Command "try { $response = Invoke-RestMethod -Uri 'http://localhost:5000/api/dashboard/complete-user/create' -Method POST -ContentType 'application/json' -TimeoutSec 10; if ($response.success) { Write-Host '[OK] Test user created: sarah_chen_founder' -ForegroundColor Green } else { Write-Host '[INFO] Test user may already exist' -ForegroundColor Yellow } } catch { Write-Host '[INFO] Could not create test user (will be available after restart)' -ForegroundColor Yellow }"

echo.
echo Opening browser...
start %FRONTEND_URL%

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Services:
echo   Frontend:  http://localhost:5173
echo   Backend:   http://localhost:5000
echo   API:       http://localhost:5000/api/health
echo.
echo Test User (Demo Account):
echo   Username:  sarah_chen_founder
echo   Password:  test123
echo   (100%% completion across all assessments)
echo.
echo Useful commands (run from %INSTALL_PATH%):
echo   docker compose logs -f      - View logs
echo   docker compose down         - Stop services
echo   docker compose restart      - Restart services
echo   docker compose ps           - Check status
echo.
pause
