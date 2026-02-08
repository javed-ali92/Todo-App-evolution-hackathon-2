#!/usr/bin/env python3
"""Script to run the backend server"""

import uvicorn
from src.main import app

if __name__ == "__main__":
    print("Starting backend server on http://localhost:8001...")
    print("Press Ctrl+C to stop the server")
    try:
        uvicorn.run(app, host="127.0.0.1", port=8001)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()