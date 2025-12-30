-- Quick fix: Ensure greenvalleyfarm has a donor record

-- First check the user_id for greenvalleyfarm
SELECT user_id, username, role FROM "User" WHERE username = 'greenvalleyfarm';

-- Check if donor already exists
SELECT u.user_id, u.username, d.donor_id, d.name
FROM "User" u
LEFT JOIN Donor d ON u.user_id = d.user_id
WHERE u.username = 'greenvalleyfarm';

-- If donor doesn't exist, create it (this will error if already exists - that's OK)
INSERT INTO Donor (user_id, name, contact, address)
SELECT user_id, name, contact, address
FROM "User"
WHERE username = 'greenvalleyfarm'
AND NOT EXISTS (SELECT 1 FROM Donor WHERE user_id IN (SELECT user_id FROM "User" WHERE username = 'greenvalleyfarm'));

-- Final verification
SELECT u.user_id, u.username, d.donor_id, d.name
FROM "User" u
LEFT JOIN Donor d ON u.user_id = d.user_id
WHERE u.username = 'greenvalleyfarm';
