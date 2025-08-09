from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import re
import google.generativeai as genai
from flask import Blueprint


def get_db():
    conn = sqlite3.connect('quickdocs.db')
    conn.row_factory = sqlite3.Row
    return conn

# Configure Gemini API
genai.configure(api_key="AIzaSyAjlYcvvzj2DYXEYNunOzRL-G01WUMOqsc")

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



@query_interface.route('/query_interface', methods=['GET', 'POST'])
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
