# Drug Dictionary Standalone Application

This is a standalone version of the drug dictionary functionality from the Pharma project.

## Project Structure

```
DrugDictionaryApp/
├── backend/
│   └── app/
│       ├── routers/
│       │   └── drug_dictionary.py
│       ├── __init__.py
│       ├── crud.py
│       ├── db.py
│       ├── main.py
│       └── schemas.py
├── frontend/
│   ├── drugs.html
│   ├── nav.js
│   └── style.css
├── .env
├── requirements.txt
└── run_app.bat
```

## Setup Instructions

1. Create the directory structure as shown above
2. Copy the backend files:
   - `db.py` - Database models and connection
   - `schemas.py` - Pydantic models
   - `crud.py` - Data access functions
   - `routers/drug_dictionary.py` - API endpoints for drug management
   - `main.py` - Main application file
3. Copy the frontend files:
   - `drugs.html` - Main UI for drug management
   - `nav.js` - Navigation component
   - `style.css` - Styling
4. Create the configuration files:
   - `.env` - Environment variables
   - `requirements.txt` - Python dependencies
   - `run_app.bat` - Run script

## Installation

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

1. Run the application:
   ```
   run_app.bat
   ```
   or
   ```
   cd backend
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Open your browser and go to `http://localhost:8000/drugs.html`

## API Endpoints

The drug dictionary API is available at:
- GET `/api/drugs/` - List all drugs
- POST `/api/drugs/` - Create a new drug
- GET `/api/drugs/{drug_id}` - Get a specific drug
- PUT `/api/drugs/{drug_id}` - Update a specific drug
- DELETE `/api/drugs/{drug_id}` - Delete a specific drug
- GET `/api/drugs/search?q={query}` - Search drugs
- POST `/api/drugs/bulk-import` - Import drugs from CSV/JSON
- GET `/api/drugs/export/csv` - Export drugs to CSV
- GET `/api/drugs/stats` - Get drug statistics

## Changes Made for Standalone Version

1. Updated database path in `.env` to use `drug_dictionary.db` instead of `malegaon_meds.db`
2. Simplified `requirements.txt` to only include necessary dependencies
3. Created a standalone `main.py` that only includes the drug dictionary functionality
4. Kept all frontend code as-is since it already works with the API endpoints

## Dependencies

- FastAPI - Web framework
- Uvicorn - ASGI server
- SQLAlchemy - Database ORM
- python-dotenv - Environment variable loading
- Pydantic - Data validation
- python-multipart - File upload support