#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Changepreneurship Platform Installer for Windows
.DESCRIPTION
    Installs and starts the Changepreneurship platform from GitHub.
    Requires Docker Desktop to be installed and running.
.NOTES
    Before running this script for the first time, execute:
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$InstallPath = "C:\Program Files\Changepreneurship"
$RepoUrl = "https://github.com/Noodzakelijk-Online/001-Changepreneurship.git"
$FrontendUrl = "http://localhost:5173"

# Color output functions
function Write-Step {
    param([string]$Message)
    Write-Host "`n[$(Get-Date -Format 'HH:mm:ss')] " -NoNewline -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor White
}

function Write-Success {
    param([string]$Message)
    Write-Host "  ✓ " -NoNewline -ForegroundColor Green
    Write-Host $Message -ForegroundColor Gray
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "  ✗ " -NoNewline -ForegroundColor Red
    Write-Host $Message -ForegroundColor Red
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "  ⚠ " -NoNewline -ForegroundColor Yellow
    Write-Host $Message -ForegroundColor Yellow
}

# Check prerequisites
Write-Step "Checking prerequisites..."

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Error-Custom "This script must be run as Administrator"
    Write-Host "`nPlease right-click the script and select 'Run as Administrator'" -ForegroundColor Yellow
    pause
    exit 1
}
Write-Success "Running as Administrator"

# Check for Git
try {
    $gitVersion = git --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Git is installed: $gitVersion"
    } else {
        throw "Git not found"
    }
} catch {
    Write-Error-Custom "Git is not installed or not in PATH"
    Write-Host "`nPlease install Git from: https://git-scm.com/download/win" -ForegroundColor Yellow
    Start-Process "https://git-scm.com/download/win"
    pause
    exit 1
}

# Check for Docker
try {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker is installed: $dockerVersion"
    } else {
        throw "Docker not found"
    }
} catch {
    Write-Error-Custom "Docker is not installed or not running"
    Write-Host "`nPlease install Docker Desktop from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    Start-Process "https://www.docker.com/products/docker-desktop"
    pause
    exit 1
}

# Check if Docker daemon is running
try {
    docker ps >$null 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Docker daemon is not running"
        Write-Host "`nPlease start Docker Desktop and wait for it to be ready, then run this script again." -ForegroundColor Yellow
        pause
        exit 1
    }
    Write-Success "Docker daemon is running"
} catch {
    Write-Error-Custom "Cannot connect to Docker daemon"
    pause
    exit 1
}

# Check for Docker Compose
try {
    $composeVersion = docker compose version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker Compose is available: $composeVersion"
    } else {
        throw "Docker Compose not found"
    }
} catch {
    Write-Error-Custom "Docker Compose is not available (should be included with Docker Desktop)"
    pause
    exit 1
}

Write-Step "Creating installation directory..."
if (-not (Test-Path $InstallPath)) {
    New-Item -Path $InstallPath -ItemType Directory -Force | Out-Null
    Write-Success "Created directory: $InstallPath"
} else {
    Write-Success "Directory already exists: $InstallPath"
}

Write-Step "Cloning/updating repository..."
Set-Location $InstallPath

if (Test-Path ".git") {
    Write-Host "  Repository already exists, pulling latest changes..." -ForegroundColor Gray
    try {
        git fetch origin 2>&1 | Out-Null
        git reset --hard origin/main 2>&1 | Out-Null
        git pull origin main 2>&1 | Out-Null
        Write-Success "Repository updated to latest version"
    } catch {
        Write-Error-Custom "Failed to update repository: $_"
        Write-Warning-Custom "Continuing with existing files..."
    }
} else {
    Write-Host "  Cloning repository from GitHub..." -ForegroundColor Gray
    try {
        git clone $RepoUrl . 2>&1 | Out-Null
        Write-Success "Repository cloned successfully"
    } catch {
        Write-Error-Custom "Failed to clone repository: $_"
        pause
        exit 1
    }
}

Write-Step "Checking for existing containers..."
$existingContainers = docker compose ps -q 2>$null
if ($existingContainers) {
    Write-Warning-Custom "Stopping existing containers..."
    docker compose down 2>&1 | Out-Null
    Start-Sleep -Seconds 2
    Write-Success "Existing containers stopped"
}

Write-Step "Starting Docker containers..."
Write-Host "  This may take a few minutes on first run (downloading images)..." -ForegroundColor Gray

try {
    # Start containers in detached mode
    docker compose up -d --build 2>&1 | ForEach-Object {
        if ($_ -match "error|Error|ERROR") {
            Write-Host "  $_" -ForegroundColor Red
        } elseif ($_ -match "Building|built|Created|Starting|Started") {
            Write-Host "  $_" -ForegroundColor Gray
        }
    }
    
    if ($LASTEXITCODE -ne 0) {
        throw "Docker compose failed with exit code $LASTEXITCODE"
    }
    
    Write-Success "Docker containers started"
} catch {
    Write-Error-Custom "Failed to start containers: $_"
    Write-Host "`nContainer logs:" -ForegroundColor Yellow
    docker compose logs --tail=50
    pause
    exit 1
}

Write-Step "Waiting for services to be healthy..."
$maxWaitSeconds = 120
$waitInterval = 5
$elapsed = 0
$allHealthy = $false

while ($elapsed -lt $maxWaitSeconds) {
    Start-Sleep -Seconds $waitInterval
    $elapsed += $waitInterval
    
    # Check container health
    $containers = docker compose ps --format json | ConvertFrom-Json
    if (-not $containers) {
        Write-Warning-Custom "No containers found, waiting..."
        continue
    }
    
    # Ensure $containers is always an array
    if ($containers -isnot [array]) {
        $containers = @($containers)
    }
    
    $runningCount = 0
    $healthyCount = 0
    $totalCount = $containers.Count
    
    foreach ($container in $containers) {
        if ($container.State -eq "running") {
            $runningCount++
            # Check if Health property exists and is "healthy"
            if ($container.PSObject.Properties['Health'] -and $container.Health -eq "healthy") {
                $healthyCount++
            } elseif (-not $container.PSObject.Properties['Health']) {
                # No health check defined, count as healthy if running
                $healthyCount++
            }
        }
    }
    
    Write-Host "  [$elapsed / $maxWaitSeconds seconds] Running: $runningCount/$totalCount, Healthy: $healthyCount/$totalCount" -ForegroundColor Gray
    
    if ($healthyCount -eq $totalCount -and $runningCount -eq $totalCount) {
        $allHealthy = $true
        break
    }
}

if ($allHealthy) {
    Write-Success "All services are healthy"
} else {
    Write-Warning-Custom "Some services may not be fully ready yet (timeout reached)"
    Write-Host "  You can check status with: docker compose ps" -ForegroundColor Gray
    Write-Host "  View logs with: docker compose logs -f" -ForegroundColor Gray
}

# Additional wait for frontend to be fully ready
Write-Step "Verifying frontend accessibility..."
$frontendReady = $false
$frontendWait = 0
$maxFrontendWait = 30

while ($frontendWait -lt $maxFrontendWait) {
    try {
        $response = Invoke-WebRequest -Uri $FrontendUrl -Method Head -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $frontendReady = $true
            break
        }
    } catch {
        # Ignore errors, keep trying
    }
    Start-Sleep -Seconds 2
    $frontendWait += 2
    Write-Host "  Waiting for frontend... ($frontendWait / $maxFrontendWait seconds)" -ForegroundColor Gray
}

if ($frontendReady) {
    Write-Success "Frontend is accessible"
} else {
    Write-Warning-Custom "Frontend may still be starting up"
}

Write-Step "Opening browser..."
Start-Sleep -Seconds 2
Start-Process $FrontendUrl
Write-Success "Browser opened at $FrontendUrl"

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Green
Write-Host "  🎉 Changepreneurship Platform is running!" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Services:" -ForegroundColor White
Write-Host "  Frontend:  " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:5173" -ForegroundColor Cyan
Write-Host "  Backend:   " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:5000" -ForegroundColor Cyan
Write-Host "  API Docs:  " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:5000/api/health" -ForegroundColor Cyan

Write-Host ""
Write-Host "Useful commands:" -ForegroundColor White
Write-Host "  View logs:      " -NoNewline -ForegroundColor Gray
Write-Host "docker compose logs -f" -ForegroundColor Yellow
Write-Host "  Stop services:  " -NoNewline -ForegroundColor Gray
Write-Host "docker compose down" -ForegroundColor Yellow
Write-Host "  Restart:        " -NoNewline -ForegroundColor Gray
Write-Host "docker compose restart" -ForegroundColor Yellow
Write-Host "  Check status:   " -NoNewline -ForegroundColor Gray
Write-Host "docker compose ps" -ForegroundColor Yellow

Write-Host ""
Write-Host "Installation directory: " -NoNewline -ForegroundColor Gray
Write-Host $InstallPath -ForegroundColor White
Write-Host ""
