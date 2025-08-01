from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
from fastapi.staticfiles import StaticFiles
import uvicorn
import traceback
import sys
import os

print("🔍 Starting imports...")

try:
    from routes import parser_router, ai_router, documentation_router, snippets_router
    print("✅ Routers imported successfully")
except ImportError as e:
    print(f"❌ Error importing routers: {e}")
    print("📁 Check that the 'routes' directory exists with the necessary files")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error during import: {e}")
    traceback.print_exc()
    sys.exit(1)

print("🚀 Creating FastAPI application...")

app = FastAPI(
    title="SkDucky AI API",
    description="Advanced Skript AI for professional Minecraft development",
    version="1.0.0"
)

print("✅ FastAPI created")

# Check if static directory exists
import os
if os.path.exists("static"):
    print("✅ 'static' directory found")
    try:
        app.mount("/static", StaticFiles(directory="static"), name="static")
        print("✅ Static files mounted")
    except Exception as e:
        print(f"⚠️ Error mounting static files: {e}")
else:
    print("⚠️ 'static' directory not found - skipping static files")

print("🔧 Configuring middleware...")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("✅ Middleware configured")

# Route for main page (chat interface)
@app.get("/app")
async def serve_app():
    """Serve the main SkDucky AI interface"""
    return FileResponse("static/index.html")

# Alternative route for root that redirects to app
@app.get("/")
async def root():
    """Redirect to chat interface or show API info"""
    # Option 1: Serve interface directly
    return FileResponse("static/index.html")
    
    # Option 2: Show API info (comment line above and uncomment these)
    # return {
    #     "message": "SkDucky AI API",
    #     "version": "1.0.0",
    #     "skript_version": "2.12.0",
    #     "status": "running",
    #     "web_interface": "/app",
    #     "api_docs": "/docs",
    #     "endpoints": {
    #         "parser": "/api/v1/parse",
    #         "validate": "/api/v1/validate",
    #         "generate": "/api/v1/generate",
    #         "autocomplete": "/api/v1/autocomplete",
    #         "documentation": "/api/v1/docs",
    #         "snippets": "/api/v1/snippets"
    #     }
    # }

print("🔌 Including routers...")

try:
    app.include_router(parser_router, prefix="/api/v1/parser")
    print("✅ Parser router included")
    
    app.include_router(ai_router, prefix="/api/v1/ai")
    print("✅ AI router included")
    
    app.include_router(documentation_router, prefix="/api/v1/docs")
    print("✅ Documentation router included")
    
    app.include_router(snippets_router, prefix="/api/v1/snippets")
    print("✅ Snippets router included")
    
except Exception as e:
    print(f"❌ Error including routers: {e}")
    traceback.print_exc()
    sys.exit(1)

import os

print("✅ Application configured successfully")

# Get port from environment (for hosting platforms)
port = int(os.environ.get("PORT", 8000))

if __name__ == "__main__":
    print(f"🌐 Starting server on port {port}")
    print("🎨 Web interface available at root URL")
    print("📝 API documentation: /docs")
    print("🛑 Press Ctrl+C to stop the server")
    try:
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        traceback.print_exc()
        input("Press Enter to close...")