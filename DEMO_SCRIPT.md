# Project Demo Script

**Smart Expiry and Donation Management System**
*A Database-Centric Full-Stack Application*

---

## 🎯 INTRODUCTION (2 minutes)

### Project Overview
*"Good day! I'm presenting the Smart Expiry and Donation Management System - a database-focused full-stack application designed to help organizations manage inventory expiry and track donations efficiently."*

### Problem Statement
*"Many NGOs, food banks, and disaster relief organizations struggle with:*
- *Expired inventory going to waste*
- *Manual tracking of donations*
- *Inefficient category classification*
- *Poor visibility into expiring items"*

### Solution
*"Our system provides:*
- *Automated expiry tracking with alerts*
- *Database-driven donation management*
- *AI-powered category prediction*
- *Dual-database architecture (SQL + NoSQL)*
- *Real-time inventory updates"*

---

## 🏗️ DATABASE DESIGN (5 minutes)

### ERD Demonstration
*"Let me show you the database design - the core of this project."*

**Show: ERD_DOCUMENTATION.md or draw on whiteboard**

### Entities (6 tables)
1. **Donor** - Who donates items
2. **Category** - Classification (Food, Medicine, etc.)
3. **Item** - Inventory with expiry tracking
4. **Receiver** - Who receives donations
5. **Donation** - Transaction records
6. **Alert** - Expiry notifications

### Relationships
*"All relationships are One-to-Many:*
- *1 Donor → Many Items*
- *1 Category → Many Items*
- *1 Item → Many Alerts*
- *1 Item → Many Donations*
- *1 Receiver → Many Donations"*

### Normalization (3NF)
*"The design follows Third Normal Form:*
- **1NF**: All attributes are atomic, no repeating groups*
- **2NF**: No partial dependencies*
- **3NF**: No transitive dependencies*

*Example: Category name isn't stored in Item table - that would create redundancy. Instead, we use category_id foreign key."*

### Foreign Keys & Constraints
*"Referential integrity is enforced through:*
- *Foreign key constraints*
- *ON DELETE CASCADE for alerts (delete with item)*
- *ON DELETE RESTRICT for donations (preserve history)*
- *CHECK constraints for valid data (quantity >= 0)"*

---

## 🔄 DUAL DATABASE ARCHITECTURE (3 minutes)

### Why Two Databases?

#### MySQL (Primary)
*"MySQL handles:*
- *Structured, relational data*
- *ACID transactions (donations)*
- *Complex JOINs*
- *Referential integrity"*

#### MongoDB (Secondary)
*"MongoDB handles:*
- *High-frequency alert logs*
- *Semi-structured data*
- *Fast writes*
- *Analytics queries"*

### Data Flow
```
Item expires → Alert created in MySQL → Same alert logged to MongoDB
                     ↓                              ↓
              Transactional record          Analytics/Reporting
```

*"This demonstrates when to use SQL vs NoSQL - a key DBMS concept."*

---

## 💻 LIVE DEMONSTRATION (10 minutes)

### 1. Dashboard (1 min)
**Action:** Open http://localhost:3000

*"The dashboard shows:*
- *8 key metrics from aggregated database queries*
- *Current status at a glance*
- *Expiry check trigger button"*

**Show:** Statistics cards, color coding

### 2. Add Item with NLP (3 min)
**Action:** Navigate to Add Item

*"Watch this - I'll demonstrate the NLP integration."*

**Enter:**
- Name: "Aspirin Tablets"
- Quantity: 100
- Expiry Date: [30 days from now]
- Description: "Pain relief medicine with 500mg tablets for fever and headache"

**Click:** "Predict Category (NLP)"

*"The system analyzes the description using TextBlob and keyword matching. It identified 'medicine', 'tablets', 'fever' - and correctly predicted Medicine category with high confidence!"*

**Complete:** Fill storage condition, select donor, submit

*"The item is now in our database. Notice how the predicted category was auto-selected."*

### 3. Inventory View (1 min)
**Action:** Navigate to Inventory

*"Here's our complete inventory:*
- *Real-time data from MySQL*
- *Calculated expiry status (SAFE/WARNING/CRITICAL/EXPIRED)*
- *Color-coded for quick identification*
- *Shows relationships: Category and Donor names via JOIN"*

### 4. Expiry Check & Alerts (3 min)
**Action:** Go back to Dashboard, click "Run Expiry Check"

*"This triggers the expiry checking algorithm:*

1. *Queries items expiring within 30 days*
2. *Calculates severity:*
   - *≤3 days = CRITICAL*
   - *≤7 days = HIGH*
   - *≤14 days = MEDIUM*
   - *>14 days = LOW*
3. *Creates alerts in MySQL*
4. *Logs to MongoDB simultaneously*
5. *Prevents duplicate alerts for same day"*

**Navigate:** Alerts page

*"Toggle between MySQL and MongoDB views:*
- *MySQL: Relational structure with JOINs*
- *MongoDB: Denormalized documents with embedded data*
- *Both show same alerts, different purposes"*

**Show MongoDB data structure:**
```json
{
  "item_name": "Milk Powder",
  "severity": "CRITICAL",
  "days_until_expiry": 5,
  "category_name": "Food",
  "timestamp": "2025-12-17T10:30:00Z"
}
```

### 5. Record Donation (2 min)
**Action:** Navigate to Record Donation

*"This demonstrates transactional database operations."*

**Select:**
- Item: "Rice Bags" (Available: 100)
- Receiver: "Hope Orphanage"
- Quantity: 25

**Submit**

*"Behind the scenes, this transaction:*
1. *Validates inventory availability*
2. *Creates donation record*
3. *Updates item quantity (100 → 75)*
4. *All in a single ACID transaction*

*If anything fails, everything rolls back - ensuring data consistency."*

**Navigate:** Donations page

*"Complete audit trail with:*
- *Donation history*
- *Item details via JOIN*
- *Receiver information*
- *Preserved even if item is deleted"*

---

## 🎓 DBMS CONCEPTS DEMONSTRATED (5 minutes)

### 1. Normalization
*"Third Normal Form eliminates:*
- *Data redundancy*
- *Update anomalies*
- *Insert/delete anomalies"*

**Example on screen:**
```sql
-- Bad (Not 3NF)
Item: id, name, category_name, donor_name

-- Good (3NF)
Item: id, name, category_id, donor_id
Category: id, name
Donor: id, name
```

### 2. Relationships & Foreign Keys
**Show schema.sql:**
```sql
CONSTRAINT fk_item_category FOREIGN KEY (category_id) 
    REFERENCES Category(category_id) 
    ON DELETE RESTRICT;
```

*"Foreign keys enforce referential integrity at database level, not application level."*

### 3. Transactions (ACID)
**Show crud.py - create_donation function:**
```python
# All or nothing - atomicity
db_donation = models.Donation(...)
db.add(db_donation)
item.quantity -= donation.quantity
db.commit()  # Single transaction
```

### 4. Views
**Show in MySQL:**
```sql
SELECT * FROM vw_item_details;
```

*"Views simplify complex queries:*
- *Pre-joined data*
- *Calculated fields*
- *Security (hide sensitive columns)"*

### 5. Stored Procedures
**Show schema.sql:**
```sql
CALL sp_record_donation(1, 1, 10, 'Emergency relief');
```

*"Encapsulates business logic in database - better performance, consistency."*

### 6. Indexes
**Show:**
```sql
SHOW INDEX FROM Item;
```

*"11 indexes created for:*
- *Foreign keys (JOIN performance)*
- *Frequently queried columns (expiry_date)*
- *Significant speedup on large datasets"*

### 7. SQL + NoSQL Integration
*"Hybrid architecture combines:*
- *SQL strengths: ACID, JOINs, constraints*
- *NoSQL strengths: scalability, flexibility, speed*

*Real-world applications often use both!"*

### 8. Data Integrity
**Show constraints in schema:**
- CHECK constraints: `quantity >= 0`
- UNIQUE constraints: `contact` numbers
- NOT NULL: Required fields
- ENUM: Limited value sets

---

## 🔧 TECHNICAL STACK (2 minutes)

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for MySQL
- **PyMongo**: MongoDB driver
- **TextBlob**: NLP library
- **Pydantic**: Data validation

### Frontend
- **React**: UI library
- **React Router**: Navigation
- **Axios**: HTTP client
- **Vite**: Build tool

### Databases
- **MySQL 8.0**: Relational database
- **MongoDB 4.4**: Document database

### Deployment
- **Railway**: MySQL hosting
- **MongoDB Atlas**: MongoDB hosting
- **Render**: Backend API hosting
- **Vercel**: Frontend hosting

---

## 📊 CODE WALKTHROUGH (3 minutes)

### 1. Models (ORM)
**Show models.py - Item model:**
```python
class Item(Base):
    item_id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('Category.category_id'))
    
    # Relationships
    category = relationship("Category")
    
    @property
    def days_until_expiry(self):
        return (self.expiry_date - date.today()).days
```

### 2. NLP Integration
**Show nlp.py - predict_category:**
```python
def predict_category(description, categories):
    # Keyword matching
    scores = calculate_scores(description)
    predicted = max(scores, key=scores.get)
    confidence = calculate_confidence(scores[predicted])
    return predicted, confidence
```

### 3. Dual Database Writes
**Show tasks.py - create_mongo_alert:**
```python
# MySQL Alert
alert = models.Alert(item_id=item.item_id, ...)
db.add(alert)
db.commit()

# MongoDB Alert (same data)
mongo_db.alerts.insert_one({
    'alert_id': alert.alert_id,
    'item_id': item.item_id,
    ...
})
```

---

## 🚀 INNOVATION & UNIQUENESS (2 minutes)

### What Makes This Special?

1. **Database-First Approach**
   - Not just a CRUD app with a database
   - Database design drives the entire application
   - Demonstrates advanced DBMS concepts

2. **Dual-Database Architecture**
   - Real-world hybrid solution
   - SQL + NoSQL working together
   - Demonstrates when to use each

3. **AI Integration**
   - NLP adds practical innovation
   - Reduces manual data entry
   - Demonstrates real-world ML application

4. **Transaction Management**
   - ACID properties in action
   - Data consistency guaranteed
   - Production-grade reliability

5. **Comprehensive Design**
   - ERD → Schema → API → UI
   - Complete end-to-end solution
   - Deployment-ready

---

## 📈 PERFORMANCE & SCALABILITY (1 minute)

### Optimizations
- **Indexes**: 11 in MySQL, 3 in MongoDB
- **Connection Pooling**: Reuse database connections
- **Views**: Pre-computed complex queries
- **Lazy Loading**: Only fetch needed data
- **Caching**: Browser-side API caching

### Scalability
- **Horizontal**: MongoDB sharding
- **Vertical**: Upgrade database servers
- **Read Replicas**: MySQL read scaling
- **CDN**: Static asset delivery

---

## 🎯 LEARNING OUTCOMES (1 minute)

*"Through this project, I gained deep understanding of:*

1. *Database design and normalization theory*
2. *Implementing complex relationships with foreign keys*
3. *Transaction management and ACID properties*
4. *SQL query optimization with indexes*
5. *Hybrid SQL + NoSQL architecture*
6. *Building production-ready full-stack applications*
7. *Integrating AI/ML into practical applications*
8. *Real-world software engineering practices"*

---

## 🔮 FUTURE ENHANCEMENTS (1 minute)

### Possible Additions
1. **User Authentication**: Role-based access control
2. **Real-time Notifications**: Email/SMS for critical alerts
3. **Advanced Analytics**: Dashboard with charts
4. **Barcode Scanning**: Mobile app integration
5. **Scheduled Jobs**: Automatic daily expiry checks
6. **Reporting**: PDF exports of donations
7. **Multi-tenancy**: Support multiple organizations
8. **API Rate Limiting**: Production security

---

## ❓ Q&A PREPARATION

### Expected Questions & Answers

**Q: Why use both MySQL and MongoDB?**
*A: MySQL excels at structured data with relationships and transactions. MongoDB excels at high-frequency writes and flexible schemas. For alerts, we want both transactional integrity (MySQL) and fast analytics (MongoDB).*

**Q: How does NLP prediction work?**
*A: It uses keyword matching - analyzing the description for category-specific terms. For example, "tablet", "medicine", "fever" → Medicine category. More advanced ML models could be added later.*

**Q: What if donation quantity exceeds available stock?**
*A: The application validates before creating the donation. If insufficient, it raises an error and the transaction is rolled back. This is ACID atomicity in action.*

**Q: How is 3NF maintained?**
*A: Every table depends only on primary key, no transitive dependencies. For example, category_name isn't in Item table - it's retrieved via JOIN when needed.*

**Q: Can this scale to thousands of items?**
*A: Yes! Indexes, connection pooling, and database optimization make it scalable. For very large datasets, we could add read replicas and caching.*

---

## ✅ CONCLUSION (1 minute)

*"In summary:*

- ✅ *Complete 3NF database design*
- ✅ *6 normalized tables with 5 relationships*
- ✅ *SQL + NoSQL hybrid architecture*
- ✅ *NLP-powered category prediction*
- ✅ *ACID transactions for data integrity*
- ✅ *Production-ready full-stack application*
- ✅ *Comprehensive documentation*
- ✅ *Deployment-ready configuration*

*This project demonstrates not just theoretical knowledge of DBMS, but practical implementation of database-driven applications with real-world considerations."*

**Thank you! Questions?**

---

## 🎬 DEMO CHECKLIST

Before presenting:
- [ ] MySQL running with sample data
- [ ] MongoDB running
- [ ] Backend API running (port 8000)
- [ ] Frontend running (port 3000)
- [ ] Browser open to http://localhost:3000
- [ ] Code editor open to show key files
- [ ] ERD diagram ready to display
- [ ] Database client open (MySQL Workbench/MongoDB Compass)
- [ ] Backup plan if live demo fails (screenshots/video)

Good luck! 🎉
