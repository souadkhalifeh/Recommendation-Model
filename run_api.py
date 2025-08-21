#!/usr/bin/env python3
"""
Simple script to run the API server with better error handling
"""
import uvicorn
import sys
import traceback

if __name__ == "__main__":
    try:
        print("Starting API server...")
        uvicorn.run(
            "api:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"Error starting server: {e}")
        traceback.print_exc()
        sys.exit(1)
