# Entity-Relationship Diagram (ERD)

## Database Design - Third Normal Form (3NF)

This document describes the database design for the Smart Expiry and Donation Management System.

## Entities and Attributes

### 1. Donor
**Purpose:** Stores information about donors who contribute items

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| donor_id | INT | PK, AUTO_INCREMENT | Unique identifier |
| name | VARCHAR(100) | NOT NULL | Donor's name |
| contact | VARCHAR(15) | NOT NULL, UNIQUE | Contact number |
| address | TEXT | | Physical address |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | ON UPDATE | Last modification time |

### 2. Category
**Purpose:** Classification of items into categories

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| category_id | INT | PK, AUTO_INCREMENT | Unique identifier |
| category_name | VARCHAR(50) | NOT NULL, UNIQUE | Category name |
| description | TEXT | | Category description |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |

**Sample Categories:** Food, Medicine, Clothing, Hygiene, Stationery

### 3. Item
**Purpose:** Inventory items with expiry tracking

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| item_id | INT | PK, AUTO_INCREMENT | Unique identifier |
| name | VARCHAR(100) | NOT NULL | Item name |
| quantity | INT | NOT NULL, CHECK (≥0) | Available quantity |
| expiry_date | DATE | NOT NULL | Expiration date |
| description | TEXT | | Item description (for NLP) |
| storage_condition | VARCHAR(100) | | Storage requirements |
| category_id | INT | FK → Category(category_id) | Item category |
| donor_id | INT | FK → Donor(donor_id) | Item donor |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | ON UPDATE | Last modification time |

**Constraints:**
- quantity >= 0
- expiry_date >= created_at

### 4. Receiver
**Purpose:** Organizations/individuals receiving donations

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| receiver_id | INT | PK, AUTO_INCREMENT | Unique identifier |
| name | VARCHAR(100) | NOT NULL | Receiver's name |
| contact | VARCHAR(15) | NOT NULL, UNIQUE | Contact number |
| address | TEXT | | Physical address |
| organization_type | VARCHAR(50) | | Type (NGO, Government, etc.) |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | ON UPDATE | Last modification time |

### 5. Donation
**Purpose:** Records of items donated to receivers

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| donation_id | INT | PK, AUTO_INCREMENT | Unique identifier |
| item_id | INT | FK → Item(item_id) | Donated item |
| receiver_id | INT | FK → Receiver(receiver_id) | Donation recipient |
| quantity | INT | NOT NULL, CHECK (>0) | Donated quantity |
| donation_date | DATE | NOT NULL, DEFAULT TODAY | Date of donation |
| notes | TEXT | | Additional notes |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |

**Constraints:**
- quantity > 0
- quantity <= item's available quantity (enforced in application)

### 6. Alert
**Purpose:** Expiry alerts for items approaching expiration

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| alert_id | INT | PK, AUTO_INCREMENT | Unique identifier |
| item_id | INT | FK → Item(item_id) | Item being alerted |
| message | TEXT | NOT NULL | Alert message |
| alert_date | DATE | NOT NULL, DEFAULT TODAY | Alert creation date |
| severity | ENUM | LOW/MEDIUM/HIGH/CRITICAL | Alert severity level |
| is_acknowledged | BOOLEAN | DEFAULT FALSE | Acknowledgment status |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |

## Relationships

### One-to-Many (1:M)

1. **Donor → Item** (1:M)
   - One donor can donate multiple items
   - Each item has exactly one donor
   - FK: Item.donor_id → Donor.donor_id
   - ON DELETE: RESTRICT (cannot delete donor with items)

2. **Category → Item** (1:M)
   - One category can have multiple items
   - Each item belongs to exactly one category
   - FK: Item.category_id → Category.category_id
   - ON DELETE: RESTRICT (cannot delete category with items)

3. **Item → Alert** (1:M)
   - One item can have multiple alerts
   - Each alert is for exactly one item
   - FK: Alert.item_id → Item.item_id
   - ON DELETE: CASCADE (delete alerts when item is deleted)

4. **Item → Donation** (1:M)
   - One item can be donated multiple times
   - Each donation record is for exactly one item
   - FK: Donation.item_id → Item.item_id
   - ON DELETE: RESTRICT (maintain donation history)

5. **Receiver → Donation** (1:M)
   - One receiver can receive multiple donations
   - Each donation goes to exactly one receiver
   - FK: Donation.receiver_id → Receiver.receiver_id
   - ON DELETE: RESTRICT (maintain donation history)

## Normalization Analysis

### First Normal Form (1NF)
✓ All attributes contain atomic values
✓ No repeating groups
✓ Each table has a primary key

### Second Normal Form (2NF)
✓ Meets 1NF requirements
✓ No partial dependencies (all non-key attributes depend on entire primary key)
✓ All tables have single-column primary keys

### Third Normal Form (3NF)
✓ Meets 2NF requirements
✓ No transitive dependencies
✓ All non-key attributes depend only on the primary key

**Example:** In Item table, category_name is not stored directly (would be transitive dependency). Instead, category_id references Category table.

## Database Integrity

### Referential Integrity
- All foreign key constraints enforced
- CASCADE for dependent data (Alert when Item deleted)
- RESTRICT for historical data (Donation records preserved)

### Domain Integrity
- CHECK constraints for valid ranges (quantity >= 0)
- NOT NULL constraints for required fields
- UNIQUE constraints for identifiers (contact numbers)
- ENUM constraints for limited values (severity levels)

### Entity Integrity
- Primary keys in all tables
- Auto-increment for automatic ID generation
- No null primary keys

## MongoDB Integration

### alerts Collection
**Purpose:** Denormalized alert logs for analytics

```json
{
  "_id": ObjectId,
  "alert_id": 123,
  "item_id": 45,
  "item_name": "Rice Bags",
  "message": "Item expires in 5 days",
  "alert_date": "2025-12-17",
  "severity": "HIGH",
  "days_until_expiry": 5,
  "quantity": 100,
  "category_id": 1,
  "category_name": "Food",
  "donor_id": 1,
  "donor_name": "Green Valley Farm",
  "expiry_date": "2025-12-22",
  "timestamp": ISODate("2025-12-17T10:30:00Z"),
  "is_acknowledged": false
}
```

**Why MongoDB?**
- High-frequency writes (alert generation)
- Semi-structured data (varying alert metadata)
- Fast querying with indexes
- Analytics and reporting
- Demonstrates SQL + NoSQL integration

## Indexes

### MySQL Indexes
```sql
-- Performance optimization
CREATE INDEX idx_item_expiry ON Item(expiry_date);
CREATE INDEX idx_item_category ON Item(category_id);
CREATE INDEX idx_item_donor ON Item(donor_id);
CREATE INDEX idx_alert_date ON Alert(alert_date);
CREATE INDEX idx_alert_item ON Alert(item_id);
CREATE INDEX idx_donation_date ON Donation(donation_date);
```

### MongoDB Indexes
```javascript
db.alerts.createIndex({ item_id: 1 });
db.alerts.createIndex({ alert_date: -1 });
db.alerts.createIndex({ severity: 1 });
```

## Views

### vw_item_details
Combines Item, Category, and Donor information with calculated expiry status

### vw_donation_details
Complete donation history with all related information

### vw_active_alerts
Current unacknowledged alerts with item details

## Stored Procedures

### sp_record_donation
- Validates inventory availability
- Creates donation record
- Updates item quantity
- Implements transaction (ACID properties)

### sp_generate_expiry_alerts
- Finds expiring items
- Calculates severity based on days remaining
- Prevents duplicate alerts for same day
- Bulk insert alerts

## DBMS Concepts Demonstrated

1. **Normalization** - 3NF design eliminates redundancy
2. **Referential Integrity** - Foreign key constraints
3. **Transactions** - ACID properties in donations
4. **Indexing** - Performance optimization
5. **Views** - Simplified complex queries
6. **Stored Procedures** - Business logic encapsulation
7. **Triggers** - Automatic timestamp updates
8. **Hybrid Database** - SQL + NoSQL integration
9. **Data Validation** - CHECK constraints
10. **Denormalization** - MongoDB for performance

---

**Visual ERD:** To visualize this design, use tools like MySQL Workbench, dbdiagram.io, or draw.io with the relationships described above.
