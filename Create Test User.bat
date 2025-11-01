@echo off
:: Create Sarah Chen test user via API

echo Creating Sarah Chen test user...
echo.

curl -X POST http://localhost:5000/api/dashboard/complete-user/create -H "Content-Type: application/json"

echo.
echo.
echo If successful, you can now login with:
echo   Username: sarah_chen_founder
echo   Email:    sarah.chen@techvision.io
echo   Password: test123
echo.
pause
