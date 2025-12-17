# Quick Start Guide

This guide will help you set up and run the Smart Expiry and Donation Management System locally.

## Prerequisites

- Python 3.8+ installed
- Node.js 16+ installed
- MySQL 8.0+ installed and running
- MongoDB 4.4+ installed and running

## Step 1: Setup MySQL Database

1. Start MySQL service
2. Login to MySQL:
   ```bash
   mysql -u root -p
   ```

3. Create database and import schema:
   ```bash
   mysql -u root -p < database/schema.sql
   ```

## Step 2: Setup Backend

1. Navigate to backend folder:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create `.env` file (copy from `.env.example`):
   ```bash
   copy .env.example .env  # Windows
   # cp .env.example .env  # Linux/Mac
   ```

6. Edit `.env` with your credentials:
   ```
   MYSQL_PASSWORD=your_mysql_password
   ```

7. Download TextBlob corpora (first time only):
   ```bash
   python -m textblob.download_corpora
   ```

8. Run backend:
   ```bash
   uvicorn app.main:app --reload
   ```

Backend will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs

## Step 3: Setup Frontend

1. Open a new terminal
2. Navigate to frontend folder:
   ```bash
   cd frontend
   ```

3. Install dependencies:
   ```bash
   npm install
   ```

4. Run frontend:
   ```bash
   npm run dev
   ```

Frontend will be available at: http://localhost:3000

## Step 4: Test the Application

1. Open browser to http://localhost:3000
2. You should see the Dashboard with sample data
3. Try adding a new item with NLP category prediction
4. Record a donation to see inventory updates
5. Run expiry check from Dashboard to see alerts

## Common Issues

### MySQL Connection Error
- Ensure MySQL service is running
- Check username/password in `.env`
- Verify database exists: `SHOW DATABASES;`

### MongoDB Connection Error
- Ensure MongoDB service is running
- Default connection: `mongodb://localhost:27017/`

### TextBlob Error
- Run: `python -m textblob.download_corpora`

### Port Already in Use
- Backend: Change port in `uvicorn` command: `--port 8001`
- Frontend: Change in `vite.config.js`

## Project Features to Test

1. **Dashboard** - View statistics and run expiry checks
2. **Add Item** - Use NLP to predict category from description
3. **Inventory** - View all items with expiry status
4. **Alerts** - View MySQL and MongoDB alerts
5. **Record Donation** - Create donation and see inventory update
6. **Donations** - View complete donation history

## Database Verification

Check data in MySQL:
```sql
USE expiry_donation_db;
SELECT * FROM Item;
SELECT * FROM Alert;
```

Check data in MongoDB:
```bash
mongosh
use expiry_donation_db
db.alerts.find().pretty()
```

## Next Steps

- Explore API documentation at http://localhost:8000/docs
- Check ERD in documentation
- Review database schema for normalization
- Test dual-database operations (MySQL + MongoDB)
- Experiment with NLP category predictions

Happy coding! 🚀
