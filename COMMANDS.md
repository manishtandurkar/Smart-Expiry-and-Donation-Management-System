# Quick Command Reference

## One-Time Setup

### 1. Database Setup
```bash
# Start MySQL service (Windows)
net start MySQL80

# Import schema
mysql -u root -p < database/schema.sql

# Verify database
mysql -u root -p
> USE expiry_donation_db;
> SHOW TABLES;
> SELECT COUNT(*) FROM Item;
> exit;
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m textblob.download_corpora
copy .env.example .env
# Edit .env with your MySQL password
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

## Daily Development Commands

### Terminal 1: Backend
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```
Backend runs on: http://localhost:8000
API Docs: http://localhost:8000/docs

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```
Frontend runs on: http://localhost:3000

### Terminal 3: MongoDB (if not running as service)
```bash
mongod --dbpath C:\data\db
```

## Testing Commands

### Test Backend API
```bash
# Get all items
curl http://localhost:8000/api/items

# Get categories
curl http://localhost:8000/api/categories

# Get dashboard stats
curl http://localhost:8000/api/stats

# Trigger expiry check
curl -X POST http://localhost:8000/api/alerts/check
```

### Test Database
```bash
# MySQL
mysql -u root -p expiry_donation_db
> SELECT * FROM Item WHERE DATEDIFF(expiry_date, CURDATE()) <= 7;
> SELECT * FROM vw_item_details;
> CALL sp_generate_expiry_alerts(30);

# MongoDB
mongosh
> use expiry_donation_db
> db.alerts.find().pretty()
> db.alerts.countDocuments()
```

## Build for Production

### Backend
```bash
cd backend
pip freeze > requirements.txt
# Deploy to Render
```

### Frontend
```bash
cd frontend
npm run build
# Deploy dist/ to Vercel
```

## Troubleshooting

### Backend not starting
```bash
# Check Python version
python --version  # Should be 3.8+

# Check if port 8000 is in use
netstat -ano | findstr :8000

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend not starting
```bash
# Check Node version
node --version  # Should be 16+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check if port 3000 is in use
netstat -ano | findstr :3000
```

### Database connection issues
```bash
# Test MySQL connection
mysql -u root -p -e "SHOW DATABASES;"

# Test MongoDB connection
mongosh --eval "db.version()"

# Check .env file exists and has correct values
cat backend/.env
```

## Useful VS Code Tasks

Create `.vscode/tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Backend",
      "type": "shell",
      "command": "cd backend && venv\\Scripts\\activate && uvicorn app.main:app --reload",
      "problemMatcher": []
    },
    {
      "label": "Start Frontend",
      "type": "shell",
      "command": "cd frontend && npm run dev",
      "problemMatcher": []
    }
  ]
}
```

## Database Backup

```bash
# Backup MySQL
mysqldump -u root -p expiry_donation_db > backup_$(date +%Y%m%d).sql

# Backup MongoDB
mongodump --db=expiry_donation_db --out=mongo_backup_$(date +%Y%m%d)

# Restore MySQL
mysql -u root -p expiry_donation_db < backup_20251217.sql

# Restore MongoDB
mongorestore --db=expiry_donation_db mongo_backup_20251217/expiry_donation_db
```

## Performance Testing

```bash
# Install Apache Bench (or use Postman)
# Test API performance
ab -n 1000 -c 10 http://localhost:8000/api/items

# Monitor database queries
mysql -u root -p
> SET GLOBAL general_log = 'ON';
> SHOW VARIABLES LIKE 'general_log%';
```

## Clean Reset

```bash
# Reset database
mysql -u root -p
> DROP DATABASE IF EXISTS expiry_donation_db;
> exit;
mysql -u root -p < database/schema.sql

# Reset MongoDB
mongosh
> use expiry_donation_db
> db.alerts.deleteMany({})

# Reset backend cache
cd backend
rm -rf __pycache__ app/__pycache__ app/routers/__pycache__

# Reset frontend cache
cd frontend
rm -rf node_modules/.vite dist
```

---

**Quick Start (After Setup):**
1. Open 2 terminals
2. Terminal 1: `cd backend && venv\Scripts\activate && uvicorn app.main:app --reload`
3. Terminal 2: `cd frontend && npm run dev`
4. Open browser: http://localhost:3000
5. Enjoy! 🎉
