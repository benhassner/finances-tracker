#!/usr/bin/env python
"""
Run the FastAPI backend server.
Supports both local development and production deployment (Render, etc.).
"""
from app.main import app
import os
import uvicorn

if __name__ == "__main__":
    # Use 0.0.0.0 for production deployment, defaults to 127.0.0.1 for local development
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
