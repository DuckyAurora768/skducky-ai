#!/usr/bin/env python3
"""
Start script for SkDucky AI on Render
"""
import os
import sys

def main():
    try:
        import uvicorn
        port = int(os.environ.get('PORT', 8000))
        print(f"🦆 Starting SkDucky AI on port {port}")
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
    except ImportError:
        print("❌ uvicorn not found, trying alternative...")
        os.system(f"python -m uvicorn main:app --host 0.0.0.0 --port {os.environ.get('PORT', 8000)}")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
