
# File: /submission/application/app.py
from flask import Flask, render_template, request, redirect, url_for , jsonify , flash
import sqlite3
import json
import os
import re
import google.generativeai as genai
import sys
from doc_verifer import process_document  # Import the document processing function


app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('quickdocs.db')
    conn.row_factory = sqlite3.Row
    return conn


# Configure Gemini API
genai.configure(api_key="Gemini key")

def generate_answer_gemini(context_chunks, query):
    context = "\n".join(context_chunks)
    prompt = f"""
You are an expert SQL generator. Convert the user's natural language question into an SQL query
based ONLY on the database schema provided in the context.

Return ONLY the SQL query without any explanation or formatting.

Context:
{context}

Question:
{query}

SQL:
"""
    model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
    response = model.generate_content(prompt)
    return response.text.strip()

def natural_language_to_sql(query):
    query_lower = query.lower().strip()
    
    try:
        # --- Regex patterns for known queries ---
        if re.match(r"show all customers", query_lower):
            return "SELECT * FROM customers", []

        if re.match(r"list all pending processes", query_lower):
            return "SELECT p.* FROM processes p JOIN process_assignments pa ON p.id = pa.process_id WHERE pa.status = 'pending'", []

        match = re.match(r"how many documents has (.+) submitted", query_lower)
        if match:
            customer_name = match.group(1).strip()
            return ("SELECT COUNT(*) as count FROM document_submissions ds JOIN customers c ON ds.customer_id = c.id WHERE c.name = ?", 
                   [customer_name])

        if re.match(r"which process has the most documents", query_lower):
            return ("SELECT p.name, COUNT(ds.id) as doc_count FROM processes p LEFT JOIN document_submissions ds ON p.id = ds.process_id GROUP BY p.id ORDER BY doc_count DESC LIMIT 1", [])

        match = re.match(r"which customers are assigned to (.+)", query_lower)
        if match:
            process_name = match.group(1).strip()
            return ("SELECT c.name FROM customers c JOIN process_assignments pa ON c.id = pa.customer_id JOIN processes p ON pa.process_id = p.id WHERE p.name = ?", 
                   [process_name])

        if re.match(r"list all document types", query_lower):
            return "SELECT * FROM document_types", []

        match = re.match(r"show documents submitted for (.+)", query_lower)
        if match:
            process_name = match.group(1).strip()
            return ("SELECT ds.id, ds.file_url, ds.ocr_data, dt.name AS document_type FROM document_submissions ds JOIN document_types dt ON ds.document_type_id = dt.id JOIN processes p ON ds.process_id = p.id WHERE p.name = ?", 
                   [process_name])

        if re.match(r"which customer has submitted the most documents", query_lower):
            return ("SELECT c.name, COUNT(ds.id) as doc_count FROM customers c LEFT JOIN document_submissions ds ON c.id = ds.customer_id GROUP BY c.id ORDER BY doc_count DESC LIMIT 1", [])

        match = re.match(r"show processes assigned to (.+)", query_lower)
        if match:
            customer_name = match.group(1).strip()
            return ("SELECT p.name, p.description, p.status FROM processes p JOIN process_assignments pa ON p.id = pa.process_id JOIN customers c ON pa.customer_id = c.id WHERE c.name = ?", 
                   [customer_name])

        match = re.match(r"how many customers are assigned to (.+)", query_lower)
        if match:
            process_name = match.group(1).strip()
            return ("SELECT COUNT(c.id) as count FROM customers c JOIN process_assignments pa ON c.id = pa.customer_id JOIN processes p ON pa.process_id = p.id WHERE p.name = ?", 
                   [process_name])

        if re.match(r"show all completed processes", query_lower):
            return "SELECT p.* FROM processes p JOIN process_assignments pa ON p.id = pa.process_id WHERE pa.status = 'completed'", []

        match = re.match(r"list documents of type (.+)", query_lower)
        if match:
            document_type = match.group(1).strip()
            return ("SELECT ds.id, ds.file_url, ds.ocr_data, c.name AS customer_name FROM document_submissions ds JOIN document_types dt ON ds.document_type_id = dt.id JOIN customers c ON ds.customer_id = c.id WHERE dt.name = ?", 
                   [document_type])

        if re.match(r"which customers have not submitted any documents", query_lower):
            return "SELECT c.name FROM customers c LEFT JOIN document_submissions ds ON c.id = ds.customer_id WHERE ds.id IS NULL", []

        match = re.match(r"show details of customer (.+)", query_lower)
        if match:
            customer_name = match.group(1).strip()
            return "SELECT * FROM customers WHERE name = ?", [customer_name]

        match = re.match(r"how many documents are submitted for (.+)", query_lower)
        if match:
            document_type = match.group(1).strip()
            return ("SELECT COUNT(ds.id) as count FROM document_submissions ds JOIN document_types dt ON ds.document_type_id = dt.id WHERE dt.name = ?", 
                   [document_type])

        # --- Fallback to Gemini if no match ---
        context_chunks = [
            "Tables and Columns:",
            "customers(id, name, email, phone)",
            "processes(id, name, description, status)",
            "process_assignments(id, customer_id, process_id, status)",
            "document_submissions(id, customer_id, process_id, document_type_id, file_url, ocr_data)",
            "document_types(id, name)",
            "Relationships:",
            "customers.id = process_assignments.customer_id",
            "processes.id = process_assignments.process_id",
            "document_submissions.customer_id = customers.id",
            "document_submissions.process_id = processes.id",
            "document_submissions.document_type_id = document_types.id"
        ]
        sql_query = generate_answer_gemini(context_chunks, query)
        return sql_query, []

    except Exception as e:
        return None, f"Error processing query: {str(e)}"





@app.route('/')
def index():
    return redirect(url_for('customer_registration'))

@app.route('/customer_registration', methods=['GET', 'POST'])
def customer_registration():
    db = get_db()
    if request.method == 'POST':
        if 'add_customer' in request.form:
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            db.execute('INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)', 
                      (name, email, phone))
            db.commit()
        elif 'assign_process' in request.form:
            customer_id = request.form['customer_id']
            process_id = request.form['process_id']
            db.execute('INSERT INTO process_assignments (customer_id, process_id) VALUES (?, ?)',
                      (customer_id, process_id))
            db.commit()
    customers = db.execute('SELECT * FROM customers').fetchall()
    processes = db.execute('SELECT * FROM processes').fetchall()
    db.close()
    return render_template('customer_registration.html', customers=customers, processes=processes)

@app.route('/extract_ocr', methods=['POST'])
def extract_ocr():
    data = request.get_json()
    file_url = data.get("file_url")
    doc_type = data.get("doc_type")

    try:
        result = process_document(file_url, doc_type)  # your Gemini OCR function
        return jsonify(result["gemini_extracted_fields"])
    except Exception as e:
        return jsonify({"error": str(e)}), 500





@app.route('/document_submission', methods=['GET', 'POST'])
def document_submission():
    db = get_db()
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        process_id = request.form['process_id']
        document_type_id = request.form['document_type_id']
        file_url = request.form['file_url']
        ocr_data = request.form['ocr_data']
        db.execute('INSERT INTO document_submissions (customer_id, process_id, document_type_id, file_url, ocr_data) VALUES (?, ?, ?, ?, ?)',
                  (customer_id, process_id, document_type_id, file_url, ocr_data))
        db.commit()
    customers = db.execute('SELECT * FROM customers').fetchall()
    processes = db.execute('SELECT * FROM processes').fetchall()
    document_types = db.execute('SELECT * FROM document_types').fetchall()
    db.close()
    return render_template('document_submission.html', customers=customers, processes=processes, document_types=document_types)

@app.route('/status_dashboard')
def status_dashboard():
    db = get_db()
    assignments = db.execute('''
        SELECT pa.id, c.name as customer_name, p.name as process_name, pa.status, 
               pa.completion_percentage, pa.assignment_date,
               COUNT(ds.id) as submitted_docs,
               (SELECT COUNT(*) FROM document_types dt WHERE dt.id IN
                   (SELECT document_type_id FROM document_submissions ds2
                    WHERE ds2.process_id = p.id)) as required_docs,
               (SELECT GROUP_CONCAT(dt.name) 
                FROM document_submissions ds
                JOIN document_types dt ON ds.document_type_id = dt.id
                WHERE ds.process_id = p.id AND ds.customer_id = c.id) as submitted_document_types
        FROM process_assignments pa
        JOIN customers c ON pa.customer_id = c.id
        JOIN processes p ON pa.process_id = p.id
        LEFT JOIN document_submissions ds ON ds.process_id = p.id AND ds.customer_id = c.id
        GROUP BY pa.id
    ''').fetchall()
    
    # Process the assignments to update status and completion percentage
    processed_assignments = []
    for assignment in assignments:
        assignment_dict = dict(assignment)
        
        # Get required documents count based on process type
        required_docs = 3 if assignment_dict['process_name'].lower() == 'home loan' else 2
        submitted_docs = min(assignment_dict['submitted_docs'], required_docs)  # Cap at required number
        
        # Calculate status and completion percentage
        if submitted_docs == 0:
            status = 'pending'
            completion_percentage = 0
        elif submitted_docs < required_docs:
            status = 'in-progress'
            completion_percentage = (submitted_docs / required_docs) * 100
        else:
            status = 'completed'
            completion_percentage = 100
            
        assignment_dict['status'] = status
        assignment_dict['completion_percentage'] = completion_percentage
        assignment_dict['submitted_docs'] = submitted_docs
        assignment_dict['required_docs'] = required_docs
        # Handle null submitted_document_types
        assignment_dict['submitted_document_types'] = assignment_dict['submitted_document_types'] or 'None'
        
        processed_assignments.append(assignment_dict)
    
    return render_template('status_dashboard.html', assignments=processed_assignments)



@app.route('/query_interface', methods=['GET', 'POST'])
def query_interface():
    query = ""
    sql = ""
    results = []
    columns = []
    error = None
    
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        sql, params = natural_language_to_sql(query)
        if isinstance(params, str):  # Error case
            error = params
        else:
            db = get_db()
            try:
                cursor = db.execute(sql, params)
                results = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
            except Exception as e:
                error = f"Database error: {str(e)}"
            finally:
                db.close()
    
    return render_template('query_interface.html', query=query, sql=sql, results=results, columns=columns, error=error)


if __name__ == '__main__':
    app.run(debug=True)
