#!/usr/bin/env python
"""
Simple script to run the FastAPI backend server.
"""
from app.main import app
import os
import uvicorn

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host=host, port=port)