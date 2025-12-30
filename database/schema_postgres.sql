-- ============================================================================
-- Smart Expiry and Donation Management System - PostgreSQL Schema
-- Database Design in Third Normal Form (3NF)
-- ============================================================================

-- Note: Supabase already provides the database, no need to create it

-- ============================================================================
-- TABLE: User
-- Description: Stores user authentication info with role-based access
-- Roles: admin, donor, receiver
-- ============================================================================
CREATE TABLE "User" (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'donor', 'receiver')),
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(15),
    address TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_role ON "User"(role);
CREATE INDEX idx_user_username ON "User"(username);

-- ============================================================================
-- TABLE: Donor
-- Description: Stores information about donors who contribute items
-- Normalization: 3NF - No transitive dependencies, all attributes depend on PK
-- ============================================================================
CREATE TABLE Donor (
    donor_id SERIAL PRIMARY KEY,
    user_id INT,
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(15) NOT NULL UNIQUE,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_donor_user FOREIGN KEY (user_id) 
        REFERENCES "User"(user_id) 
        ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INDEX idx_donor_name ON Donor(name);

-- ============================================================================
-- TABLE: Item
-- Description: Inventory items with expiry tracking
-- Normalization: 3NF
-- ============================================================================
CREATE TABLE Item (
    item_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    expiry_date DATE NOT NULL,
    description TEXT,
    storage_condition VARCHAR(100),
    category VARCHAR(50),
    donor_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_item_donor FOREIGN KEY (donor_id) 
        REFERENCES Donor(donor_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    
    CONSTRAINT chk_quantity CHECK (quantity >= 0)
);

CREATE INDEX idx_item_expiry ON Item(expiry_date);
CREATE INDEX idx_item_category ON Item(category);
CREATE INDEX idx_item_donor ON Item(donor_id);
CREATE INDEX idx_item_name ON Item(name);

-- ============================================================================
-- TABLE: Receiver
-- Description: Organizations/individuals receiving donated items
-- Normalization: 3NF - Independent entity, no redundancy
-- ============================================================================
CREATE TABLE Receiver (
    receiver_id SERIAL PRIMARY KEY,
    user_id INT,
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(15) NOT NULL UNIQUE,
    address TEXT,
    region VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_receiver_user FOREIGN KEY (user_id) 
        REFERENCES "User"(user_id) 
        ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INDEX idx_receiver_name ON Receiver(name);
CREATE INDEX idx_receiver_region ON Receiver(region);

-- ============================================================================
-- TABLE: Donation
-- Description: Records of items donated to receivers
-- Normalization: 3NF
-- ============================================================================
CREATE TABLE Donation (
    donation_id SERIAL PRIMARY KEY,
    item_id INT NOT NULL,
    receiver_id INT NOT NULL,
    donor_id INT,
    quantity INT NOT NULL,
    donation_date DATE NOT NULL DEFAULT CURRENT_DATE,
    delivery_mode VARCHAR(50),
    delivered_by VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_donation_item FOREIGN KEY (item_id) 
        REFERENCES Item(item_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_donation_receiver FOREIGN KEY (receiver_id) 
        REFERENCES Receiver(receiver_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_donation_donor FOREIGN KEY (donor_id) 
        REFERENCES Donor(donor_id) 
        ON DELETE SET NULL ON UPDATE CASCADE,
    
    CONSTRAINT chk_donation_quantity CHECK (quantity > 0)
);

CREATE INDEX idx_donation_date ON Donation(donation_date);
CREATE INDEX idx_donation_item ON Donation(item_id);
CREATE INDEX idx_donation_receiver ON Donation(receiver_id);
CREATE INDEX idx_donation_donor ON Donation(donor_id);

-- ============================================================================
-- TABLE: Alert
-- Description: Expiry alerts for items approaching expiration
-- Normalization: 3NF
-- ============================================================================
CREATE TABLE Alert (
    alert_id SERIAL PRIMARY KEY,
    item_id INT NOT NULL,
    message TEXT NOT NULL,
    alert_date DATE NOT NULL DEFAULT CURRENT_DATE,
    severity VARCHAR(20) DEFAULT 'MEDIUM' CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    is_acknowledged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_alert_item FOREIGN KEY (item_id) 
        REFERENCES Item(item_id) 
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX idx_alert_date ON Alert(alert_date);
CREATE INDEX idx_alert_item ON Alert(item_id);
CREATE INDEX idx_alert_severity ON Alert(severity);
CREATE INDEX idx_alert_acknowledged ON Alert(is_acknowledged);

-- ============================================================================
-- TABLE: DonationRequest
-- Description: Stores donation requests from receivers pending admin approval
-- Status: pending, approved, rejected
-- ============================================================================
CREATE TABLE DonationRequest (
    request_id SERIAL PRIMARY KEY,
    receiver_id INT NOT NULL,
    item_id INT,
    item_name VARCHAR(100),
    quantity INT NOT NULL,
    request_type VARCHAR(20) NOT NULL DEFAULT 'existing' CHECK (request_type IN ('existing', 'new')),
    notes TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    admin_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_request_receiver FOREIGN KEY (receiver_id) 
        REFERENCES Receiver(receiver_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_request_item FOREIGN KEY (item_id) 
        REFERENCES Item(item_id) 
        ON DELETE SET NULL ON UPDATE CASCADE,
    
    CONSTRAINT chk_request_quantity CHECK (quantity > 0)
);

CREATE INDEX idx_request_status ON DonationRequest(status);
CREATE INDEX idx_request_receiver ON DonationRequest(receiver_id);
CREATE INDEX idx_request_date ON DonationRequest(created_at);

-- ============================================================================
-- TRIGGERS: Auto-update timestamps
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_updated_at BEFORE UPDATE ON "User" FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_donor_updated_at BEFORE UPDATE ON Donor FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_item_updated_at BEFORE UPDATE ON Item FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_receiver_updated_at BEFORE UPDATE ON Receiver FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_request_updated_at BEFORE UPDATE ON DonationRequest FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS: Simplified queries for common operations
-- ============================================================================

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
    (i.expiry_date - CURRENT_DATE) AS days_until_expiry,
    CASE 
        WHEN (i.expiry_date - CURRENT_DATE) < 0 THEN 'EXPIRED'
        WHEN (i.expiry_date - CURRENT_DATE) <= 7 THEN 'CRITICAL'
        WHEN (i.expiry_date - CURRENT_DATE) <= 30 THEN 'WARNING'
        ELSE 'SAFE'
    END AS expiry_status
FROM Item i
INNER JOIN Donor d ON i.donor_id = d.donor_id;

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
    (i.expiry_date - CURRENT_DATE) AS days_remaining
FROM Alert a
INNER JOIN Item i ON a.item_id = i.item_id
WHERE a.is_acknowledged = FALSE
ORDER BY a.severity DESC, a.alert_date DESC;

-- ============================================================================
-- STORED PROCEDURES: Business logic encapsulation
-- ============================================================================

CREATE OR REPLACE FUNCTION sp_record_donation(
    p_item_id INT,
    p_receiver_id INT,
    p_quantity INT,
    p_notes TEXT
)
RETURNS VOID AS $$
DECLARE
    v_current_quantity INT;
BEGIN
    -- Check current inventory
    SELECT quantity INTO v_current_quantity FROM Item WHERE item_id = p_item_id FOR UPDATE;
    
    IF v_current_quantity < p_quantity THEN
        RAISE EXCEPTION 'Insufficient inventory';
    END IF;
    
    -- Insert donation record
    INSERT INTO Donation (item_id, receiver_id, quantity, notes)
    VALUES (p_item_id, p_receiver_id, p_quantity, p_notes);
    
    -- Update inventory
    UPDATE Item SET quantity = quantity - p_quantity WHERE item_id = p_item_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION sp_generate_expiry_alerts(p_days_threshold INT)
RETURNS VOID AS $$
BEGIN
    INSERT INTO Alert (item_id, message, severity)
    SELECT 
        item_id,
        'Item "' || name || '" expires in ' || (expiry_date - CURRENT_DATE) || ' days',
        CASE 
            WHEN (expiry_date - CURRENT_DATE) <= 3 THEN 'CRITICAL'
            WHEN (expiry_date - CURRENT_DATE) <= 7 THEN 'HIGH'
            WHEN (expiry_date - CURRENT_DATE) <= 14 THEN 'MEDIUM'
            ELSE 'LOW'
        END::VARCHAR(20)
    FROM Item
    WHERE (expiry_date - CURRENT_DATE) <= p_days_threshold
      AND (expiry_date - CURRENT_DATE) >= 0
      AND quantity > 0
      AND NOT EXISTS (
          SELECT 1 FROM Alert 
          WHERE Alert.item_id = Item.item_id 
            AND Alert.alert_date = CURRENT_DATE
      );
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SAMPLE DATA: For testing and demonstration
-- ============================================================================

INSERT INTO "User" (username, password, role, name, contact) VALUES
('admin', 'admin', 'admin', 'System Admin', '0000000000');

INSERT INTO "User" (username, password, role, name, contact, address) VALUES
('greenvalleyfarm', 'greenvalleyfarm', 'donor', 'Green Valley Farm', '9876543210', '123 Farm Road, Rural District'),
('citymedicalstore', 'citymedicalstore', 'donor', 'City Medical Store', '9876543211', '456 Health Plaza, Urban Center'),
('fashionhub', 'fashionhub', 'donor', 'Fashion Hub', '9876543212', '789 Style Street, Shopping Mall'),
('communitycenter', 'communitycenter', 'donor', 'Community Center', '9876543213', '321 Community Lane, Downtown');

INSERT INTO "User" (username, password, role, name, contact, address) VALUES
('hopeorphanage', 'hopeorphanage', 'receiver', 'Hope Orphanage', '8765432101', '111 Care Street, North Zone'),
('seniorcitizensh', 'seniorcitizensh', 'receiver', 'Senior Citizens Home', '8765432102', '222 Elder Avenue, East Zone'),
('disasterrelief', 'disasterrelief', 'receiver', 'Disaster Relief Camp', '8765432103', '333 Emergency Road, South Zone'),
('homelessshelter', 'homelessshelter', 'receiver', 'Homeless Shelter', '8765432104', '444 Support Boulevard, West Zone');

INSERT INTO Donor (user_id, name, contact, address) VALUES
(2, 'Green Valley Farm', '9876543210', '123 Farm Road, Rural District'),
(3, 'City Medical Store', '9876543211', '456 Health Plaza, Urban Center'),
(4, 'Fashion Hub', '9876543212', '789 Style Street, Shopping Mall'),
(5, 'Community Center', '9876543213', '321 Community Lane, Downtown');

INSERT INTO Receiver (user_id, name, contact, address, region) VALUES
(6, 'Hope Orphanage', '8765432101', '111 Care Street, North Zone', 'North Region'),
(7, 'Senior Citizens Home', '8765432102', '222 Elder Avenue, East Zone', 'East Region'),
(8, 'Disaster Relief Camp', '8765432103', '333 Emergency Road, South Zone', 'South Region'),
(9, 'Homeless Shelter', '8765432104', '444 Support Boulevard, West Zone', 'West Region');

INSERT INTO Item (name, quantity, expiry_date, description, storage_condition, category, donor_id) VALUES
('Rice Bags', 100, CURRENT_DATE + INTERVAL '90 days', 'Premium quality basmati rice', 'Cool and dry place', 'Food', 1),
('Wheat Flour', 50, CURRENT_DATE + INTERVAL '60 days', 'Whole wheat flour', 'Cool and dry place', 'Food', 1),
('Canned Beans', 200, CURRENT_DATE + INTERVAL '180 days', 'Protein-rich canned beans', 'Room temperature', 'Food', 1),
('Milk Powder', 30, CURRENT_DATE + INTERVAL '5 days', 'Full cream milk powder', 'Refrigerated', 'Food', 1),
('Paracetamol Tablets', 500, CURRENT_DATE + INTERVAL '120 days', '500mg tablets for fever', 'Store below 25°C', 'Medicine', 2),
('Antibiotic Syrup', 100, CURRENT_DATE + INTERVAL '10 days', 'Amoxicillin suspension', 'Refrigerate after opening', 'Medicine', 2),
('Bandages', 300, CURRENT_DATE + INTERVAL '365 days', 'Sterile cotton bandages', 'Dry place', 'Medicine', 2),
('Winter Jackets', 75, CURRENT_DATE + INTERVAL '730 days', 'Warm winter jackets for adults', 'Dry storage', 'Clothing', 3),
('Children Shirts', 120, CURRENT_DATE + INTERVAL '730 days', 'Cotton shirts for children', 'Dry storage', 'Clothing', 3),
('Hand Sanitizer', 200, CURRENT_DATE + INTERVAL '8 days', 'Alcohol-based sanitizer', 'Cool place', 'Hygiene', 4),
('Soap Bars', 400, CURRENT_DATE + INTERVAL '400 days', 'Antibacterial soap bars', 'Dry place', 'Hygiene', 4);

-- ============================================================================
-- DATABASE STATISTICS
-- ============================================================================
SELECT 
    'Database Created Successfully' AS Status,
    CURRENT_DATABASE() AS Database_Name,
    (SELECT COUNT(*) FROM Donor) AS Donors,
    (SELECT COUNT(*) FROM Receiver) AS Receivers,
    (SELECT COUNT(*) FROM Item) AS Items,
    (SELECT COUNT(*) FROM Donation) AS Donations,
    (SELECT COUNT(*) FROM Alert) AS Alerts;
