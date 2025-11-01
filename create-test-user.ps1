# Quick Seed Script for Windows

Write-Host "Creating Sarah Chen test user..." -ForegroundColor Cyan

$response = Invoke-RestMethod -Uri "http://localhost:5000/api/dashboard/complete-user/create" -Method POST -ContentType "application/json"

if ($response.success) {
    Write-Host ""
    Write-Host "✓ Sarah Chen test user created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Login Credentials:" -ForegroundColor Yellow
    Write-Host "  Username: sarah_chen_founder" -ForegroundColor White
    Write-Host "  Email:    sarah.chen@techvision.io" -ForegroundColor White
    Write-Host "  Password: test123" -ForegroundColor White
    Write-Host "  User ID:  $($response.user_id)" -ForegroundColor White
    Write-Host ""
    Write-Host "Completion: $($response.completion)" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "✗ Failed to create user: $($response.error)" -ForegroundColor Red
}
