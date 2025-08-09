-- # File: /submission/database/sample_data.sql
-- ```sql
-- -- Insert Processes
INSERT INTO processes (name, description, status) VALUES
('Home Loan Application', 'Complete application for home loan', 'active'),
('KYC Verification', 'Know Your Customer verification process', 'active');

-- Insert Document Types
INSERT INTO document_types (name, description, required_fields) VALUES
('PAN Card', 'Permanent Account Number card', '{"number": "text", "name": "text"}'),
('Salary Slip', 'Recent salary slip', '{"month": "text", "amount": "number"}'),
('Bank Statement', 'Bank statement for last 6 months', '{"account_number": "text", "balance": "number"}'),
('Aadhaar Card', 'Aadhaar identification card', '{"number": "text", "name": "text"}'),
('Address Proof', 'Proof of current address', '{"address": "text", "pincode": "text"}');

-- Insert Customers
INSERT INTO customers (name, email, phone) VALUES
('Amit Sharma', 'amit.sharma@email.com', '9876543210'),
('Priya Patel', 'priya.patel@email.com', '9876543211'),
('Rahul Singh', 'rahul.singh@email.com', '9876543212'),
('Neha Gupta', 'neha.gupta@email.com', '9876543213'),
('Vikram Rao', 'vikram.rao@email.com', '9876543214');

-- Insert Process Assignments
INSERT INTO process_assignments (customer_id, process_id, status, completion_percentage) VALUES
(1, 1, 'in-progress', 60),
(5, 2, 'completed', 100),
(2, 1, 'pending', 0),
(3, 1, 'in-progress', 30),
(4, 2, 'completed', 100);

-- Insert Document Submissions
INSERT INTO document_submissions (customer_id, process_id, document_type_id, file_url, ocr_data, validation_status) VALUES
(1, 1, 1, 'docs/pan_amit.pdf', '{"number": "ABCDE1234F", "name": "Amit Sharma"}', 'approved'),
(1, 1, 2, 'docs/salary_amit.pdf', '{"month": "July 2025", "amount": 75000}', 'pending'),
(5, 2, 4, 'docs/aadhaar_Vikram.pdf', '{"number": "123456789012", "name": "Vikram Rao"}', 'approved'),
(3, 1, 1, 'docs/pan_rahul.pdf', '{"number": "XYZAB9876C", "name": "Rahul Singh"}', 'pending'),
(4, 2, 1, 'docs/pan_neha.pdf', '{"number": "LMNOP5432K", "name": "Neha Gupta"}', 'approved'),
(4, 2, 4, 'docs/aadhaar_neha.pdf', '{"number": "987654321098", "name": "Neha Gupta"}', 'approved');
-- ```
