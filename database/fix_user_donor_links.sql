-- Fix User-Donor-Receiver Links
-- This script ensures proper relationships between users and their donor/receiver records

-- First, let's check current state
SELECT 'Current User Table:' as info;
SELECT user_id, username, role, name FROM "User" ORDER BY user_id;

SELECT 'Current Donor Table:' as info;
SELECT donor_id, user_id, name FROM Donor ORDER BY donor_id;

SELECT 'Current Receiver Table:' as info;
SELECT receiver_id, user_id, name FROM Receiver ORDER BY receiver_id;

-- Delete existing donor and receiver records (but keep Users)
DELETE FROM Item;
DELETE FROM Donation;
DELETE FROM Donor;
DELETE FROM Receiver;

-- Now re-insert Donor records with correct user_ids
-- Check what user_ids exist for donors
INSERT INTO Donor (user_id, name, contact, address) 
SELECT user_id, name, contact, address
FROM "User"
WHERE role = 'donor'
ORDER BY user_id;

-- Re-insert Receiver records with correct user_ids
INSERT INTO Receiver (user_id, name, contact, address, region) 
SELECT user_id, name, contact, address, 
    CASE 
        WHEN name LIKE '%North%' OR name LIKE '%Hope%' THEN 'North Region'
        WHEN name LIKE '%East%' OR name LIKE '%Senior%' THEN 'East Region'
        WHEN name LIKE '%South%' OR name LIKE '%Disaster%' THEN 'South Region'
        WHEN name LIKE '%West%' OR name LIKE '%Homeless%' THEN 'West Region'
        ELSE 'Central Region'
    END as region
FROM "User"
WHERE role = 'receiver'
ORDER BY user_id;

-- Verify the links are correct
SELECT 'Verification - Users with Donors:' as info;
SELECT u.user_id, u.username, u.role, d.donor_id, d.name as donor_name
FROM "User" u
LEFT JOIN Donor d ON u.user_id = d.user_id
WHERE u.role = 'donor'
ORDER BY u.user_id;

SELECT 'Verification - Users with Receivers:' as info;
SELECT u.user_id, u.username, u.role, r.receiver_id, r.name as receiver_name
FROM "User" u
LEFT JOIN Receiver r ON u.user_id = r.user_id
WHERE u.role = 'receiver'
ORDER BY u.user_id;

-- Add some sample items back (using the new donor_ids)
INSERT INTO Item (name, quantity, expiry_date, description, storage_condition, category, donor_id) 
SELECT 'Rice Bags', 100, CURRENT_DATE + INTERVAL '90 days', 'Premium quality basmati rice', 'Cool and dry place', 'Food', donor_id
FROM Donor LIMIT 1;

INSERT INTO Item (name, quantity, expiry_date, description, storage_condition, category, donor_id) 
SELECT 'Paracetamol Tablets', 500, CURRENT_DATE + INTERVAL '120 days', '500mg tablets for fever', 'Store below 25°C', 'Medicine', donor_id
FROM Donor OFFSET 1 LIMIT 1;

SELECT 'Sample Items Added:' as info;
SELECT i.item_id, i.name, i.donor_id, d.name as donor_name
FROM Item i
JOIN Donor d ON i.donor_id = d.donor_id;
