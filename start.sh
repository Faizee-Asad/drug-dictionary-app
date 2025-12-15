#!/bin/bash
# Navigate to the backend directory and start the application
cd backend
exec python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT