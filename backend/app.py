"""
Entry point for Vercel deployment.
This file imports the FastAPI app from src.api.main and exposes it for Vercel.
"""

from src.api.main import app
import uvicorn
import os

# Vercel will automatically detect and use this app instance

if __name__ == "__main__":
    # Get port from environment variable (for Vercel) or default to 8000
    port = int(os.environ.get("PORT", 8000))
    # Use 0.0.0.0 for production deployment
    host = "0.0.0.0" if os.environ.get("VERCEL") else "127.0.0.1"
    uvicorn.run(app, host=host, port=port, reload=False) 