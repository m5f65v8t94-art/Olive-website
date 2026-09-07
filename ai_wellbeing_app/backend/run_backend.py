import os
import sys
import uvicorn

if __name__ == "__main__":
    print("========================================================")
    print("🌟 Starting Olive Youth Mental-Wellbeing Backend Server")
    print("📍 URL: http://127.0.0.1:8000")
    print("📖 API Docs: http://127.0.0.1:8000/docs")
    print("========================================================")
    
    # Ensure current directory is in sys.path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
