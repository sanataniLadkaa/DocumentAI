import sqlite3
import json

# Connect to (or create) the quickdocs.db database
conn = sqlite3.connect('quickdocs.db')
cursor = conn.cursor()

# Create tables (equivalent to schema.sql)
cursor.executescript('''
-- Creating processes table
CREATE TABLE IF NOT EXISTS processes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Creating document_types table
CREATE TABLE IF NOT EXISTS document_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    required_fields JSON NOT NULL
);

-- Creating customers table
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Creating process_assignments table
CREATE TABLE IF NOT EXISTS process_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    process_id INTEGER NOT NULL,
    assignment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    completion_percentage INTEGER DEFAULT 0,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (process_id) REFERENCES processes(id)
);

-- Creating document_submissions table
CREATE TABLE IF NOT EXISTS document_submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    process_id INTEGER NOT NULL,
    document_type_id INTEGER NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_url VARCHAR(255),
    ocr_data JSON,
    validation_status VARCHAR(20) DEFAULT 'pending',
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (process_id) REFERENCES processes(id),
    FOREIGN KEY (document_type_id) REFERENCES document_types(id)
);
''')

# Insert sample data (equivalent to sample_data.sql)
cursor.executescript('''
-- Insert Processes
INSERT OR IGNORE INTO processes (name, description, status) VALUES
('Home Loan Application', 'Complete application for home loan', 'active'),
('KYC Verification', 'Know Your Customer verification process', 'active');

-- Insert Document Types
INSERT OR IGNORE INTO document_types (name, description, required_fields) VALUES
('PAN Card', 'Permanent Account Number card', '{"number": "text", "name": "text"}'),
('Salary Slip', 'Recent salary slip', '{"month": "text", "amount": "number"}'),
('Bank Statement', 'Bank statement for last 6 months', '{"account_number": "text", "balance": "number"}'),
('Aadhaar Card', 'Aadhaar identification card', '{"number": "text", "name": "text"}'),
('Address Proof', 'Proof of current address', '{"address": "text", "pincode": "text"}');

-- Insert Customers
INSERT OR IGNORE INTO customers (name, email, phone, registration_date) VALUES
('Amit Sharma', 'amit.sharma@email.com', '9876543210', CURRENT_TIMESTAMP),
('Priya Patel', 'priya.patel@email.com', '9876543211', CURRENT_TIMESTAMP),
('Rahul Singh', 'rahul.singh@email.com', '9876543212', CURRENT_TIMESTAMP),
('Neha Gupta', 'neha.gupta@email.com', '9876543213', CURRENT_TIMESTAMP),
('Vikram Rao', 'vikram.rao@email.com', '9876543214', CURRENT_TIMESTAMP);

-- Insert Process Assignments
INSERT OR IGNORE INTO process_assignments (customer_id, process_id, assignment_date, status, completion_percentage) VALUES
(1, 1, CURRENT_TIMESTAMP, 'in-progress', 60),
(5, 2, CURRENT_TIMESTAMP, 'completed', 100),
(2, 1, CURRENT_TIMESTAMP, 'pending', 0),
(3, 1, CURRENT_TIMESTAMP, 'in-progress', 30),
(4, 2, CURRENT_TIMESTAMP, 'completed', 100);

-- Insert Document Submissions
INSERT OR IGNORE INTO document_submissions (customer_id, process_id, document_type_id, file_url, ocr_data, validation_status) VALUES
(1, 1, 1, 'docs/pan_amit.pdf', '{"number": "ABCDE1234F", "name": "Amit Sharma"}', 'approved'),
(1, 1, 2, 'docs/salary_amit.pdf', '{"month": "July 2025", "amount": 75000}', 'pending'),
(5, 2, 4, 'docs/aadhaar_vikram.pdf', '{"number": "123456789012", "name": "Vikram Rao"}', 'approved'),
(3, 1, 1, 'docs/pan_rahul.pdf', '{"number": "XYZAB9876C", "name": "Rahul Singh"}', 'pending'),
(4, 2, 1, 'docs/pan_neha.pdf', '{"number": "LMNOP5432K", "name": "Neha Gupta"}', 'approved'),
(4, 2, 4, 'docs/aadhaar_neha.pdf', '{"number": "987654321098", "name": "Neha Gupta"}', 'approved');
''')

# Commit changes and close the connection
conn.commit()
conn.close()

print("quickdocs.db has been created and populated successfully.")
