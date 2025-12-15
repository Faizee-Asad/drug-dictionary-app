from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.middleware.base import BaseHTTPMiddleware
import secrets

# Simple admin credentials (in production, use a proper database)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# For demo purposes, we'll store the logged in users in memory
# In production, use a proper session store
active_sessions = set()

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for certain endpoints
        if (
            request.url.path.startswith("/api/docs") or
            request.url.path.startswith("/api/redoc") or
            request.url.path.startswith("/api/openapi.json") or
            request.url.path == "/health" or
            request.url.path == "/" or
            request.url.path.startswith("/static/") or
            request.method == "GET" and (
                request.url.path.startswith("/api/drugs/") and 
                "search" in request.url.path or
                request.url.path == "/api/drugs/" or
                request.url.path.startswith("/api/drugs/") and request.url.path.count("/") == 3
            )
        ):
            response = await call_next(request)
            return response
        
        # Check if it's an admin-only endpoint
        is_admin_endpoint = (
            request.method in ["PUT", "DELETE"] or
            "bulk-import" in request.url.path or
            "export" in request.url.path
        )
        
        # For admin endpoints, check for admin session
        if is_admin_endpoint:
            session_token = request.headers.get("Authorization")
            if not session_token or not session_token.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Admin authentication required")
            
            token = session_token.split(" ")[1]
            if token not in active_sessions:
                raise HTTPException(status_code=401, detail="Invalid or expired session")
        
        response = await call_next(request)
        return response

def verify_admin(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    """Verify admin credentials"""
    correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

def create_session_token():
    """Create a simple session token"""
    return secrets.token_hex(16)