#!/usr/bin/env python3
"""
Startup script for Cloud Run deployment
Handles environment variables and graceful startup
"""
import os
import sys

def main():
    # Get port from environment variable (Cloud Run sets this)
    port = int(os.environ.get("PORT", 8080))
    
    print(f"Starting server on port {port}")
    print(f"Qdrant URL: {os.environ.get('QDRANT_URL', 'Not set')}")
    print(f"Collection: {os.environ.get('COLLECTION_NAME', 'products')}")
    
    # Use gunicorn for better Cloud Run compatibility
    import subprocess
    cmd = [
        "gunicorn",
        "--bind", f"0.0.0.0:{port}",
        "--workers", "1",
        "--worker-class", "uvicorn.workers.UvicornWorker",
        "--timeout", "120",
        "--keep-alive", "2",
        "--max-requests", "1000",
        "--max-requests-jitter", "50",
        "--access-logfile", "-",
        "--error-logfile", "-",
        "--log-level", "info",
        "api:app"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
