"""
Entry point for Vercel deployment.
This file imports the FastAPI app from src.api.main and exposes it for Vercel.
"""

from src.api.main import app

# Vercel will automatically detect and use this app instance 