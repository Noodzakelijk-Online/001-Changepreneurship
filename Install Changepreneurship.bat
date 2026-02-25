@echo off
setlocal enabledelayedexpansion
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
set "INSTALL_PATH=C:\Changepreneurship"
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

:: Check for .env configuration file
if not exist ".env" (
    echo.
    echo ========================================
    echo   Configuration File Required
    echo ========================================
    echo.
    echo Before starting, you need a .env file with the API key.
    echo.
    echo Contact the project owner to get the .env file, then:
    echo   1. Place the .env file in this folder: %INSTALL_PATH%
    echo   2. Run this installer again
    echo.
    echo Or create it manually - open Notepad, paste this content,
    echo save as ".env" (not ".env.txt"!) in %INSTALL_PATH%:
    echo.
    echo   DATABASE_URL=postgresql://admin:admin@postgres:5432/changepreneurship
    echo   REDIS_URL=redis://:changepreneurship123@redis:6379/0
    echo   SECRET_KEY=changepreneurship-production-secret-key
    echo   USE_LLM=true
    echo   LLM_PROVIDER=groq
    echo   LLM_MODEL=llama-3.3-70b-versatile
    echo   GROQ_API_KEY=^<key from project owner^>
    echo.
    pause
    exit /b 1
) else (
    echo [OK] Configuration file found
)

:: Start Docker containers
echo.
echo Starting Docker containers...
echo This may take a few minutes on first run (downloading images)...
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
set "FRONTEND_URL=http://localhost"
set /a count=0
:CheckFrontend
set /a count+=1
if %count% gtr 20 goto FrontendTimeout

powershell -Command "try { $response = Invoke-WebRequest -Uri '%FRONTEND_URL%' -Method Head -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; exit 0 } catch { exit 1 }"
if %errorLevel% equ 0 goto FrontendReady

echo   Waiting... (%count%/20)
timeout /t 3 /nobreak >nul
goto CheckFrontend

:FrontendTimeout
echo [WARNING] Frontend may still be starting up (check docker compose logs)
goto OpenBrowser

:FrontendReady
echo [OK] Frontend is ready at %FRONTEND_URL%

:OpenBrowser
echo.
echo Opening browser...
start %FRONTEND_URL%

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Services:
echo   Frontend:  http://localhost
echo   Backend:   http://localhost:5000
echo   API:       http://localhost:5000/health
echo.
echo Demo Account (100%% all assessments completed):
echo   Email:     sarah.chen@techstartup.com
echo   Password:  Test1234!
echo.
echo Useful commands (run from %INSTALL_PATH%):
echo   docker compose logs -f      - View live logs
echo   docker compose down         - Stop platform
echo   docker compose up -d        - Start platform again
echo   docker compose ps           - Check container status
echo.
pause
