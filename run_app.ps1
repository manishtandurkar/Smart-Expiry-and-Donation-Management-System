# Run Application Script
# This script starts both backend and frontend servers

Write-Host "=== Starting Smart Expiry and Donation Management System ===" -ForegroundColor Cyan
Write-Host ""

# Check if database is set up
if (!(Test-Path "backend\.env")) {
    Write-Host "❌ Please run setup_database.ps1 first!" -ForegroundColor Red
    exit
}

Write-Host "Starting Backend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Lab programs\DBMS\EL\backend'; & 'C:/Lab programs/DBMS/EL/.venv/Scripts/python.exe' -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 3

Write-Host "Starting Frontend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Lab programs\DBMS\EL\frontend'; npm run dev"

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "✅ Application started successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Access the application at:" -ForegroundColor Cyan
Write-Host "  📱 Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "  🔌 Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "  📚 API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C in each terminal window to stop the servers." -ForegroundColor Yellow
