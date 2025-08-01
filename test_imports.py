#!/usr/bin/env python3

print("🔍 Testing imports...")

try:
    print("Testing models import...")
    from models import DocumentationQuery, ParseResult, ValidationResult, AIRequest, AIResponse
    print("✅ All models imported successfully")
    
    print("Testing routes import...")
    from routes import parser_router, ai_router, documentation_router, snippets_router
    print("✅ All routers imported successfully")
    
    print("Testing services import...")
    from services.ai_service import SkDuckyAIService
    from services.parser_service import SkriptParser
    print("✅ All services imported successfully")
    
    print("🎉 All imports successful! The server should work now.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
