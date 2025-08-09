# QuickDocs Document Collection System

## Setup Instructions
1. Install Python 3.8+
2. Install dependencies: `pip install -r requirements.txt`
3. Initialize database:
   - Run `sqlite3 quickdocs.db < database/schema.sql`
   - Run `sqlite3 quickdocs.db < database/sample_data.sql`
   - in case database stil not initialize run quickdocs.py as `python quickdocs.py`
4. Run the application: `python app.py`

## Technologies Used
- Python 3.8+
- Flask 2.0.1
- SQLite
- HTML/CSS
- Gemini key 

## Notes
- Gemini API keys required is requred in app.py , doc_verifer.py , query_interface.py
- Screenshots are in the /screenshots directory
- doc_verifier.py is used to verify the documents 
- The application runs on http://localhost:5000
