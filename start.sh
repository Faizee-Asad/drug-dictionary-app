#!/bin/bash
<<<<<<< HEAD
# Navigate to the backend directory and start the application
cd backend
exec python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
=======
export PYTHONPATH=$PYTHONPATH:/opt/render/project/src/backend
uvicorn app.main:app --host 0.0.0.0 --port $PORT
>>>>>>> 2853a3f237991fe0b366ebce744d1a1df4cd7e25
