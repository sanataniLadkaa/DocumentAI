# File: /submission/database/schema.sql
```sql
-- Creating processes table
CREATE TABLE processes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Creating document_types table
CREATE TABLE document_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    required_fields JSON NOT NULL
);

-- Creating customers table
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Creating process_assignments table
CREATE TABLE process_assignments (
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
CREATE TABLE document_submissions (
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
