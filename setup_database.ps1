# Database Setup Script
# Run this script to initialize the MySQL database

Write-Host "=== Smart Expiry and Donation Management System - Database Setup ===" -ForegroundColor Cyan
Write-Host ""

# Prompt for MySQL password
$mysqlPassword = Read-Host "Enter your MySQL root password" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($mysqlPassword)
$password = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

Write-Host "Creating database and importing schema..." -ForegroundColor Yellow

# Run MySQL commands
$schemaPath = "database\schema.sql"
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p"$password" -e "source $schemaPath"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database created successfully!" -ForegroundColor Green
    
    # Update .env file with the password
    $envPath = "backend\.env"
    $envContent = Get-Content $envPath
    $envContent = $envContent -replace 'MYSQL_PASSWORD=.*', "MYSQL_PASSWORD=$password"
    $envContent | Set-Content $envPath
    
    Write-Host "✅ Backend .env file updated with your MySQL password" -ForegroundColor Green
} else {
    Write-Host "❌ Database setup failed. Please check your MySQL password." -ForegroundColor Red
}

Write-Host ""
Write-Host "Setup complete! You can now run the application." -ForegroundColor Cyan
