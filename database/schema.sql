-- ============================================================================
-- Smart Expiry and Donation Management System - MySQL Schema
-- Database Design in Third Normal Form (3NF)
-- ============================================================================

DROP DATABASE IF EXISTS expiry_donation_db;
CREATE DATABASE expiry_donation_db;
USE expiry_donation_db;

-- ============================================================================
-- TABLE: Donor
-- Description: Stores information about donors who contribute items
-- Normalization: 3NF - No transitive dependencies, all attributes depend on PK
-- ============================================================================
CREATE TABLE Donor (
    donor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(15) NOT NULL,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_contact (contact),
    INDEX idx_donor_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE: Item
-- Description: Inventory items with expiry tracking
-- Normalization: 3NF
--   - donor_id FK references Donor (1-M relationship)
--   - category stored as attribute (as per ER diagram)
--   - All non-key attributes depend solely on item_id
-- ============================================================================
CREATE TABLE Item (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    expiry_date DATE NOT NULL,
    description TEXT,
    storage_condition VARCHAR(100),
    category VARCHAR(50),
    donor_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    CONSTRAINT fk_item_donor FOREIGN KEY (donor_id) 
        REFERENCES Donor(donor_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    
    -- Business Constraints
    CONSTRAINT chk_quantity CHECK (quantity >= 0),
    
    -- Indexes for Performance
    INDEX idx_item_expiry (expiry_date),
    INDEX idx_item_category (category),
    INDEX idx_item_donor (donor_id),
    INDEX idx_item_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE: Receiver
-- Description: Organizations/individuals receiving donated items
-- Normalization: 3NF - Independent entity, no redundancy
-- ============================================================================
CREATE TABLE Receiver (
    receiver_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(15) NOT NULL,
    address TEXT,
    region VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_receiver_contact (contact),
    INDEX idx_receiver_name (name),
    INDEX idx_receiver_region (region)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE: Donation
-- Description: Records of items donated to receivers
-- Normalization: 3NF
--   - item_id FK references Item (M-N relationship via junction table)
--   - receiver_id FK references Receiver (1-M relationship)
--   - donor_id FK references Donor (N-N relationship for approvals)
-- ============================================================================
CREATE TABLE Donation (
    donation_id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    receiver_id INT NOT NULL,
    donor_id INT,
    quantity INT NOT NULL,
    donation_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    delivery_mode VARCHAR(50),
    delivered_by VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    CONSTRAINT fk_donation_item FOREIGN KEY (item_id) 
        REFERENCES Item(item_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_donation_receiver FOREIGN KEY (receiver_id) 
        REFERENCES Receiver(receiver_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_donation_donor FOREIGN KEY (donor_id) 
        REFERENCES Donor(donor_id) 
        ON DELETE SET NULL ON UPDATE CASCADE,
    
    -- Business Constraints
    CONSTRAINT chk_donation_quantity CHECK (quantity > 0),
    
    -- Indexes for Performance
    INDEX idx_donation_date (donation_date),
    INDEX idx_donation_item (item_id),
    INDEX idx_donation_receiver (receiver_id),
    INDEX idx_donation_donor (donor_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE: Alert
-- Description: Expiry alerts for items approaching expiration
-- Normalization: 3NF
--   - item_id FK references Item (1-M relationship)
--   - Stores alert metadata in relational format
-- ============================================================================
CREATE TABLE Alert (
    alert_id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    message TEXT NOT NULL,
    alert_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    severity ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') DEFAULT 'MEDIUM',
    is_acknowledged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    CONSTRAINT fk_alert_item FOREIGN KEY (item_id) 
        REFERENCES Item(item_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    
    -- Indexes for Performance
    INDEX idx_alert_date (alert_date),
    INDEX idx_alert_item (item_id),
    INDEX idx_alert_severity (severity),
    INDEX idx_alert_acknowledged (is_acknowledged)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- VIEWS: Simplified queries for common operations
-- ============================================================================

-- View: Item details with category and donor information
CREATE VIEW vw_item_details AS
SELECT 
    i.item_id,
    i.name AS item_name,
    i.quantity,
    i.expiry_date,
    i.description,
    i.storage_condition,
    i.category AS category_name,
    d.name AS donor_name,
    d.contact AS donor_contact,
    DATEDIFF(i.expiry_date, CURDATE()) AS days_until_expiry,
    CASE 
        WHEN DATEDIFF(i.expiry_date, CURDATE()) < 0 THEN 'EXPIRED'
        WHEN DATEDIFF(i.expiry_date, CURDATE()) <= 7 THEN 'CRITICAL'
        WHEN DATEDIFF(i.expiry_date, CURDATE()) <= 30 THEN 'WARNING'
        ELSE 'SAFE'
    END AS expiry_status
FROM Item i
INNER JOIN Donor d ON i.donor_id = d.donor_id;

-- View: Donation history with full details
CREATE VIEW vw_donation_details AS
SELECT 
    don.donation_id,
    don.donation_date,
    don.quantity AS donated_quantity,
    don.delivery_mode,
    don.delivered_by,
    i.name AS item_name,
    i.category AS category_name,
    r.name AS receiver_name,
    r.region,
    d.name AS donor_name,
    approver.name AS approved_by_donor,
    don.notes
FROM Donation don
INNER JOIN Item i ON don.item_id = i.item_id
INNER JOIN Receiver r ON don.receiver_id = r.receiver_id
INNER JOIN Donor d ON i.donor_id = d.donor_id
LEFT JOIN Donor approver ON don.donor_id = approver.donor_id;

-- View: Active alerts with item details
CREATE VIEW vw_active_alerts AS
SELECT 
    a.alert_id,
    a.message,
    a.alert_date,
    a.severity,
    i.name AS item_name,
    i.quantity,
    i.expiry_date,
    i.category AS category_name,
    DATEDIFF(i.expiry_date, CURDATE()) AS days_remaining
FROM Alert a
INNER JOIN Item i ON a.item_id = i.item_id
WHERE a.is_acknowledged = FALSE
ORDER BY a.severity DESC, a.alert_date DESC;

-- ============================================================================
-- STORED PROCEDURES: Business logic encapsulation
-- ============================================================================

-- Procedure: Record donation and update inventory
DELIMITER //
CREATE PROCEDURE sp_record_donation(
    IN p_item_id INT,
    IN p_receiver_id INT,
    IN p_quantity INT,
    IN p_notes TEXT
)
BEGIN
    DECLARE v_current_quantity INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Donation recording failed';
    END;
    
    START TRANSACTION;
    
    -- Check current inventory
    SELECT quantity INTO v_current_quantity FROM Item WHERE item_id = p_item_id FOR UPDATE;
    
    IF v_current_quantity < p_quantity THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient inventory';
    END IF;
    
    -- Insert donation record
    INSERT INTO Donation (item_id, receiver_id, quantity, notes)
    VALUES (p_item_id, p_receiver_id, p_quantity, p_notes);
    
    -- Update inventory
    UPDATE Item SET quantity = quantity - p_quantity WHERE item_id = p_item_id;
    
    COMMIT;
END //
DELIMITER ;

-- Procedure: Generate expiry alerts
DELIMITER //
CREATE PROCEDURE sp_generate_expiry_alerts(IN p_days_threshold INT)
BEGIN
    INSERT INTO Alert (item_id, message, severity)
    SELECT 
        item_id,
        CONCAT('Item "', name, '" expires in ', DATEDIFF(expiry_date, CURDATE()), ' days'),
        CASE 
            WHEN DATEDIFF(expiry_date, CURDATE()) <= 3 THEN 'CRITICAL'
            WHEN DATEDIFF(expiry_date, CURDATE()) <= 7 THEN 'HIGH'
            WHEN DATEDIFF(expiry_date, CURDATE()) <= 14 THEN 'MEDIUM'
            ELSE 'LOW'
        END
    FROM Item
    WHERE DATEDIFF(expiry_date, CURDATE()) <= p_days_threshold
      AND DATEDIFF(expiry_date, CURDATE()) >= 0
      AND quantity > 0
      AND NOT EXISTS (
          SELECT 1 FROM Alert 
          WHERE Alert.item_id = Item.item_id 
            AND Alert.alert_date = CURDATE()
      );
END //
DELIMITER ;

-- ============================================================================
-- SAMPLE DATA: For testing and demonstration
-- ============================================================================

-- Insert Donors
INSERT INTO Donor (name, contact, address) VALUES
('Green Valley Farm', '9876543210', '123 Farm Road, Rural District'),
('City Medical Store', '9876543211', '456 Health Plaza, Urban Center'),
('Fashion Hub', '9876543212', '789 Style Street, Shopping Mall'),
('Community Center', '9876543213', '321 Community Lane, Downtown');

-- Insert Receivers
INSERT INTO Receiver (name, contact, address, region) VALUES
('Hope Orphanage', '8765432101', '111 Care Street, North Zone', 'North Region'),
('Senior Citizens Home', '8765432102', '222 Elder Avenue, East Zone', 'East Region'),
('Disaster Relief Camp', '8765432103', '333 Emergency Road, South Zone', 'South Region'),
('Homeless Shelter', '8765432104', '444 Support Boulevard, West Zone', 'West Region');

-- Insert Items
INSERT INTO Item (name, quantity, expiry_date, description, storage_condition, category, donor_id) VALUES
-- Food items
('Rice Bags', 100, DATE_ADD(CURDATE(), INTERVAL 90 DAY), 'Premium quality basmati rice', 'Cool and dry place', 'Food', 1),
('Wheat Flour', 50, DATE_ADD(CURDATE(), INTERVAL 60 DAY), 'Whole wheat flour', 'Cool and dry place', 'Food', 1),
('Canned Beans', 200, DATE_ADD(CURDATE(), INTERVAL 180 DAY), 'Protein-rich canned beans', 'Room temperature', 'Food', 1),
('Milk Powder', 30, DATE_ADD(CURDATE(), INTERVAL 5 DAY), 'Full cream milk powder', 'Refrigerated', 'Food', 1),

-- Medicine items
('Paracetamol Tablets', 500, DATE_ADD(CURDATE(), INTERVAL 120 DAY), '500mg tablets for fever', 'Store below 25°C', 'Medicine', 2),
('Antibiotic Syrup', 100, DATE_ADD(CURDATE(), INTERVAL 10 DAY), 'Amoxicillin suspension', 'Refrigerate after opening', 'Medicine', 2),
('Bandages', 300, DATE_ADD(CURDATE(), INTERVAL 365 DAY), 'Sterile cotton bandages', 'Dry place', 'Medicine', 2),

-- Clothing items
('Winter Jackets', 75, DATE_ADD(CURDATE(), INTERVAL 730 DAY), 'Warm winter jackets for adults', 'Dry storage', 'Clothing', 3),
('Children Shirts', 120, DATE_ADD(CURDATE(), INTERVAL 730 DAY), 'Cotton shirts for children', 'Dry storage', 'Clothing', 3),

-- Hygiene items
('Hand Sanitizer', 200, DATE_ADD(CURDATE(), INTERVAL 8 DAY), 'Alcohol-based sanitizer', 'Cool place', 'Hygiene', 4),
('Soap Bars', 400, DATE_ADD(CURDATE(), INTERVAL 400 DAY), 'Antibacterial soap bars', 'Dry place', 'Hygiene', 4);

-- ============================================================================
-- DATABASE STATISTICS
-- ============================================================================
SELECT 
    'Database Created Successfully' AS Status,
    DATABASE() AS Database_Name,
    (SELECT COUNT(*) FROM Donor) AS Donors,
    (SELECT COUNT(*) FROM Receiver) AS Receivers,
    (SELECT COUNT(*) FROM Item) AS Items,
    (SELECT COUNT(*) FROM Donation) AS Donations,
    (SELECT COUNT(*) FROM Alert) AS Alerts;
