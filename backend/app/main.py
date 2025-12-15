from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.db import db
from app.routers import drug_dictionary
from app.auth import AuthMiddleware, verify_admin, create_session_token, active_sessions
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

# Add authentication middleware
app.add_middleware(AuthMiddleware)

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

@app.post("/api/login")
async def login(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    username = verify_admin(credentials)
    token = create_session_token()
    active_sessions.add(token)
    return {"token": token, "username": username}

@app.post("/api/logout")
async def logout(token: str):
    if token in active_sessions:
        active_sessions.remove(token)
    return {"message": "Logged out successfully"}