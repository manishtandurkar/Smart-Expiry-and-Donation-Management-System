# Smart Expiry and Donation Management System

A **DBMS-centric** full-stack application demonstrating database design, normalization, SQL + NoSQL integration, and data-driven operations.

## 🎯 Project Focus

This is a **DATABASE-FOCUSED** project emphasizing:
- Entity-Relationship Design (ERD)
- 3rd Normal Form (3NF) normalization
- Foreign keys and referential integrity
- SQL (MySQL) + NoSQL (MongoDB) integration
- Database-driven business logic
- NLP-enhanced data entry

## 📊 Database Architecture

### MySQL (Primary Database - 3NF)

**Entities:**
1. **Donor** - donor_id (PK), name, contact, address
2. **Category** - category_id (PK), category_name
3. **Item** - item_id (PK), name, quantity, expiry_date, description, storage_condition, category_id (FK), donor_id (FK)
4. **Receiver** - receiver_id (PK), name, contact, address
5. **Donation** - donation_id (PK), item_id (FK), receiver_id (FK), quantity, donation_date
6. **Alert** - alert_id (PK), item_id (FK), message, alert_date

**Relationships:**
- Donor 1–M Item
- Category 1–M Item
- Item 1–M Alert
- Item 1–M Donation
- Receiver 1–M Donation

### MongoDB (Alert Logs)

**Collection:** `alerts`
- Stores alert documents with references to MySQL item_id
- High-frequency, semi-structured alert data
- Complements MySQL for analytics and logging

## 🏗️ Tech Stack

### Backend
- **Python FastAPI** - RESTful API server
- **SQLAlchemy** - MySQL ORM
- **PyMongo** - MongoDB driver
- **TextBlob** - NLP for category prediction
- **APScheduler** - Background expiry checks

### Frontend
- **React** - UI framework
- **Axios** - HTTP client
- **React Router** - Navigation

### Databases
- **MySQL 8.0+** - Relational data
- **MongoDB** - Document store for logs

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- MySQL 8.0+
- MongoDB 4.4+

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

Create `.env` file in backend directory:
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=expiry_donation_db

MONGO_URI=mongodb://localhost:27017/
MONGO_DATABASE=expiry_donation_db
```

Initialize database:
```bash
mysql -u root -p < ../database/schema.sql
python -m app.init_db  # Create sample data
```

Run backend:
```bash
uvicorn app.main:app --reload
```

API Documentation: http://localhost:8000/docs

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

Application: http://localhost:3000

## 📋 Features

### Core Database Features
1. **Inventory Management** - Add/update/view items with expiry tracking
2. **Donation Tracking** - Record donations, update inventory automatically
3. **Expiry Alerts** - Daily checks for near-expiry items
4. **Dual Database Logging** - MySQL for transactional data, MongoDB for alert logs
5. **NLP Category Prediction** - Auto-suggest categories based on item description

### API Endpoints

**Donors**
- `GET /api/donors` - List all donors
- `POST /api/donors` - Add new donor
- `GET /api/donors/{id}` - Get donor details

**Categories**
- `GET /api/categories` - List all categories
- `POST /api/categories` - Add new category

**Items**
- `GET /api/items` - List all items
- `POST /api/items` - Add new item (with NLP prediction)
- `PUT /api/items/{id}` - Update item
- `GET /api/items/expiring` - Get items expiring soon

**Receivers**
- `GET /api/receivers` - List all receivers
- `POST /api/receivers` - Add new receiver

**Donations**
- `GET /api/donations` - List all donations
- `POST /api/donations` - Record donation (updates inventory)

**Alerts**
- `GET /api/alerts` - Get alerts from MySQL
- `GET /api/alerts/mongo` - Get alerts from MongoDB
- `POST /api/alerts/check` - Manually trigger expiry check

**Analytics**
- `GET /api/stats` - Dashboard statistics

## 🎓 DBMS Concepts Demonstrated

1. **Normalization (3NF)**
   - No transitive dependencies
   - Atomic values
   - Primary and foreign keys

2. **Referential Integrity**
   - ON DELETE CASCADE for dependent records
   - Foreign key constraints

3. **SQL + NoSQL Integration**
   - MySQL for structured, transactional data
   - MongoDB for semi-structured logs
   - Dual writes for alerts

4. **Database-Driven Logic**
   - Expiry checking with date calculations
   - Inventory updates through triggers/application logic
   - Transaction management for donations

5. **Complex Queries**
   - JOINs across multiple tables
   - Aggregate functions
   - Date-based filtering

## 🌐 Deployment

### Railway (MySQL)
1. Create new project on Railway
2. Add MySQL service
3. Update `.env` with Railway credentials

### MongoDB Atlas
1. Create cluster on MongoDB Atlas
2. Whitelist IP addresses
3. Update `MONGO_URI` in `.env`

### Render (Backend)
1. Create new Web Service
2. Connect GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables

### Vercel (Frontend)
1. Connect GitHub repository
2. Set framework preset: React
3. Update API URLs to Render backend URL
4. Deploy

## 📁 Project Structure

```
EL/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application
│   │   ├── config.py               # Configuration
│   │   ├── database.py             # DB connections
│   │   ├── models.py               # SQLAlchemy models
│   │   ├── schemas.py              # Pydantic schemas
│   │   ├── crud.py                 # Database operations
│   │   ├── nlp.py                  # NLP category prediction
│   │   ├── tasks.py                # Background tasks
│   │   └── routers/
│   │       ├── donors.py
│   │       ├── categories.py
│   │       ├── items.py
│   │       ├── receivers.py
│   │       ├── donations.py
│   │       └── alerts.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── AddItem.jsx
│   │   │   ├── Inventory.jsx
│   │   │   ├── Alerts.jsx
│   │   │   ├── RecordDonation.jsx
│   │   │   └── Donations.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── index.jsx
│   └── package.json
├── database/
│   ├── schema.sql                  # MySQL schema (3NF)
│   └── ERD.png                     # Entity-Relationship Diagram
└── README.md
```

## 👥 Authors

Developed as a DBMS course project demonstrating database-centric application design.

## 📄 License

MIT License - Educational Project
