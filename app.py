# app.py - Compatibility layer for Render deployment
# This file allows Render to use the default 'gunicorn app:app' command
# while redirecting to our actual FastAPI application in main.py

from main import app

# Export the FastAPI app instance for gunicorn
__all__ = ['app']
