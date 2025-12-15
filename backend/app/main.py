from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.db import db
from app.routers import drug_dictionary
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get port from environment variable or default to 8000
port = int(os.environ.get("PORT", 8000))

# Create FastAPI app
app = FastAPI(
    title="Drug Dictionary API",
    description="API for managing drug information and local pricing",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db.init_db()

# Include routers
app.include_router(drug_dictionary.router)

# Serve static files (for frontend)
if os.path.exists("../frontend"):
    app.mount("/static", StaticFiles(directory="../frontend"), name="static")

@app.get("/", include_in_schema=False)
async def root():
    # Redirect to the main drugs page
    return RedirectResponse(url="/static/drugs.html")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}