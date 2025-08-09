# File: /submission/application/README.md
```markdown
# QuickDocs Document Collection System

## Setup Instructions
1. Install Python 3.8+
2. Install dependencies: `pip install -r requirements.txt`
3. Initialize database:
   - Run `sqlite3 quickdocs.db < database/schema.sql`
   - Run `sqlite3 quickdocs.db < database/sample_data.sql`
4. Run the application: `python app.py`

## Technologies Used
- Python 3.8+
- Flask 2.0.1
- SQLite
- HTML/CSS

## Notes
- Gemini API keys required
- Screenshots are in the /screenshots directory
- The application runs on http://localhost:5000
