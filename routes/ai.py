from fastapi import APIRouter, HTTPException
from typing import List, Dict
import json
import os
try:
    import requests
except ImportError:
    requests = None
from models import AIRequest, AIResponse, AutocompleteRequest, AutocompleteResponse, SkriptCode, LearnRequest, FeedbackRequest
from services.ai_service import SkDuckyAIService

router = APIRouter(tags=["ai"])
ai_service = SkDuckyAIService()

@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify router is working"""
    return {"status": "working", "message": "🦆 Router is loaded correctly!"}

@router.post("/generate", response_model=AIResponse)
async def generate_code(request: AIRequest):
    try:
        response = ai_service.generate_code(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/learn")
async def learn_example(request: LearnRequest):
    """Teach a new example to the AI"""
    try:
        result = ai_service.learn(request.prompt, request.code)
        return {"message": result, "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/examples")
async def get_examples():
    """Get all learned examples"""
    return []  # Return empty array for now to test

@router.get("/ollama/status")
async def ollama_status_simple():
    """Simple Ollama status check"""
    return {"available": True, "message": "Testing"}

@router.get("/ollama/diagnose")
async def ollama_diagnose_simple():
    """Simple Ollama diagnosis"""
    return {"status": "testing", "message": "Diagnosis endpoint working"}

@router.post("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete_code(request: AutocompleteRequest):
    try:
        suggestions = ai_service.autocomplete(
            request.code, 
            request.cursor_position
        )
        
        return AutocompleteResponse(
            suggestions=suggestions,
            context_aware=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def get_code_templates():
    return {
        "templates": list(ai_service.knowledge["patterns"].keys()),
        "total": len(ai_service.knowledge["patterns"])
    }

@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    if template_id not in ai_service.knowledge["patterns"]:
        raise HTTPException(status_code=404, detail="Template not found")
    
    template = ai_service.knowledge["patterns"][template_id]
    return {
        "id": template_id,
        "description": template["description"],
        "code": template["template"]
    }

@router.get("/best-practices")
async def get_best_practices():
    return {
        "practices": ai_service.knowledge["best_practices"],
        "common_errors": ai_service.knowledge["common_errors"]
    }

@router.post("/explain")
async def explain_code(code: SkriptCode):
    try:
        explanation = ai_service.generate_explanation("code analysis", code.code)
        confidence = ai_service.calculate_confidence(code.code)
        suggestions = ai_service.generate_suggestions(code.code)
        
        return {
            "explanation": explanation,
            "confidence": confidence,
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Enhanced feedback submission that trains both traditional AI and Ollama"""
    try:
        # Determine the source of the original code generation
        source = "traditional"  # Default
        if hasattr(request, 'source') and request.source:
            source = request.source
        
        result = ai_service.process_feedback(
            prompt=request.prompt,
            code=request.code,
            feedback_type=request.feedback_type,
            observations=request.observations,
            corrected_code=request.corrected_code,
            source=source
        )
        return {"message": result, "success": True, "learning_enhanced": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- OLLAMA ENDPOINTS ---

@router.post("/generate-ollama")
async def generate_with_ollama(request: AIRequest):
    """Generate Skript code using Ollama AI"""
    try:
        if not ai_service.ollama_enabled:
            raise HTTPException(status_code=503, detail="Ollama service is not available")
        
        result = ai_service.generate_with_ollama(request.prompt, request.include_explanation)
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ollama/status")
async def get_ollama_status():
    """Get Ollama service status"""
    try:
        status = ai_service.get_ollama_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ollama/models")
async def get_ollama_models():
    """Get available Ollama models"""
    try:
        models = ai_service.get_ollama_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ollama/model/{model_name}")
async def switch_ollama_model(model_name: str):
    """Switch Ollama model"""
    try:
        message = ai_service.switch_ollama_model(model_name)
        return {"message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ollama/feedback")
async def submit_ollama_feedback(request: dict):
    """Submit feedback about Ollama-generated code"""
    try:
        result = ai_service.learn_from_ollama_feedback(
            prompt=request.get("prompt", ""),
            ollama_code=request.get("ollama_code", ""),
            feedback=request.get("feedback", ""),
            corrected_code=request.get("corrected_code")
        )
        return {"message": result, "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/codellama/feedback")
async def submit_codellama_feedback(request: dict):
    """Submit feedback for CodeLlama to improve future generations"""
    try:
        result = ai_service.submit_codellama_feedback(
            prompt=request.get("prompt", ""),
            generated_code=request.get("generated_code", ""),
            feedback_type=request.get("feedback_type", "positive"),  # 'positive', 'negative', 'correction'
            corrected_code=request.get("corrected_code"),
            comments=request.get("comments", "")
        )
        return {"message": result, "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning/stats")
async def get_learning_stats():
    """Get comprehensive learning statistics for both traditional AI and Ollama"""
    try:
        stats = {
            "traditional_ai": {
                "total_examples": len(ai_service.examples),
                "user_corrections": len([ex for ex in ai_service.examples if ex.get("source") == "user_correction"]),
                "knowledge_patterns": len(ai_service.knowledge.get("patterns", {})),
                "best_practices": len(ai_service.knowledge.get("best_practices", []))
            },
            "ollama_ai": {
                "enabled": ai_service.ollama_enabled,
                "current_model": ai_service.ollama_model,
                "learning_examples": 0,
                "positive_feedback": 0,
                "corrections": 0,
                "negative_feedback": 0
            },
            "feedback_data": {
                "total_feedback": 0,
                "positive": 0,
                "negative": 0,
                "corrections": 0
            }
        }
        
        # Count Ollama learning examples
        try:
            if os.path.exists("ollama_learning_context.json"):
                with open("ollama_learning_context.json", "r", encoding="utf-8") as f:
                    ollama_data = json.load(f)
                    stats["ollama_ai"]["learning_examples"] = len(ollama_data)
                    stats["ollama_ai"]["positive_feedback"] = len([ex for ex in ollama_data if ex.get("type") == "positive_feedback"])
                    stats["ollama_ai"]["corrections"] = len([ex for ex in ollama_data if ex.get("type") == "correction_training"])
                    stats["ollama_ai"]["negative_feedback"] = len([ex for ex in ollama_data if ex.get("type") == "negative_feedback"])
        except Exception:
            pass
        
        # Count feedback data
        try:
            if os.path.exists("feedback_data.json"):
                with open("feedback_data.json", "r", encoding="utf-8") as f:
                    feedback_data = json.load(f)
                    stats["feedback_data"]["total_feedback"] = len(feedback_data)
                    stats["feedback_data"]["positive"] = len([fb for fb in feedback_data if fb.get("feedback_type") == "correct"])
                    stats["feedback_data"]["negative"] = len([fb for fb in feedback_data if fb.get("feedback_type") == "incorrect"])
                    stats["feedback_data"]["corrections"] = len([fb for fb in feedback_data if fb.get("corrected_code")])
        except Exception:
            pass
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning/context")
async def get_learning_context():
    """Get recent learning context for debugging and insights"""
    try:
        context = {}
        
        # Get recent Ollama learning examples
        try:
            if os.path.exists("ollama_learning_context.json"):
                with open("ollama_learning_context.json", "r", encoding="utf-8") as f:
                    ollama_data = json.load(f)
                    context["recent_ollama_learning"] = ollama_data[-5:]  # Last 5 examples
        except Exception:
            context["recent_ollama_learning"] = []
        
        # Get recent feedback
        try:
            if os.path.exists("feedback_data.json"):
                with open("feedback_data.json", "r", encoding="utf-8") as f:
                    feedback_data = json.load(f)
                    context["recent_feedback"] = feedback_data[-5:]  # Last 5 feedback entries
        except Exception:
            context["recent_feedback"] = []
        
        # Get recent user corrections
        recent_corrections = [ex for ex in ai_service.examples if ex.get("source") == "user_correction"][-5:]
        context["recent_corrections"] = recent_corrections
        
        return context
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ollama/diagnose")
async def diagnose_ollama():
    """Diagnose Ollama installation and provide setup instructions"""
    try:
        import subprocess
        
        diagnosis = {
            "installed": False,
            "running": False,
            "model_available": False,
            "issues": [],
            "solutions": [],
            "status": "checking"
        }
        
        # Check if requests is available
        if requests is None:
            diagnosis["issues"].append("requests library not available")
            diagnosis["solutions"].append("Install requests: pip install requests")
            diagnosis["status"] = "error"
            return diagnosis
        
        # Check if Ollama is installed
        try:
            result = subprocess.run(['ollama', '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                diagnosis["installed"] = True
                diagnosis["version"] = result.stdout.strip()
            else:
                diagnosis["issues"].append("Ollama command failed")
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            diagnosis["issues"].append("Ollama is not installed or not in PATH")
            diagnosis["solutions"].append("Install Ollama from https://ollama.ai/download")
        
        # Check if service is running
        if diagnosis["installed"]:
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                if response.status_code == 200:
                    diagnosis["running"] = True
                    response_data = response.json()
                    
                    # Handle different response structures
                    models = []
                    if "models" in response_data:
                        models = [m.get("name", "") for m in response_data["models"]]
                    elif isinstance(response_data, list):
                        models = [m.get("name", "") for m in response_data]
                    
                    diagnosis["available_models"] = models
                    
                    # Check for codellama specifically (including variants like codellama:latest)
                    codellama_found = any("codellama" in str(model).lower() for model in models)
                    if codellama_found:
                        diagnosis["model_available"] = True
                    else:
                        # Double-check by trying ollama list command
                        try:
                            import subprocess
                            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
                            if result.returncode == 0 and "codellama" in result.stdout.lower():
                                diagnosis["model_available"] = True
                                diagnosis["available_models"].append("codellama (detected via ollama list)")
                        except:
                            pass
                        
                        if not diagnosis["model_available"]:
                            diagnosis["issues"].append("codellama model not found")
                            diagnosis["solutions"].append("Run: ollama pull codellama")
                else:
                    diagnosis["issues"].append(f"Ollama API returned status {response.status_code}")
            except requests.RequestException as e:
                diagnosis["issues"].append(f"Ollama service is not running: {str(e)}")
                diagnosis["solutions"].append("Start Ollama service: ollama serve")
        
        # Determine overall status
        if diagnosis["installed"] and diagnosis["running"] and diagnosis["model_available"]:
            diagnosis["status"] = "ready"
        elif diagnosis["installed"] and diagnosis["running"]:
            diagnosis["status"] = "missing_model"
        elif diagnosis["installed"]:
            diagnosis["status"] = "not_running"
        else:
            diagnosis["status"] = "not_installed"
        
        return diagnosis
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "issues": ["Failed to diagnose Ollama"],
            "solutions": ["Check system manually"]
        }

@router.post("/ollama/start")
async def start_ollama():
    """Attempt to start Ollama service"""
    try:
        import subprocess
        import asyncio
        
        # Check if requests is available
        if requests is None:
            return {
                "success": False,
                "message": "🦆 Quack! requests library not available. Please install: pip install requests",
                "error": "requests not available"
            }
        
        # Check if already running
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "🦆 Quack! Ollama is already running!",
                    "already_running": True
                }
        except:
            pass
        
        # Try to start Ollama in background
        try:
            # Start ollama serve in background
            process = subprocess.Popen(
                ['ollama', 'serve'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if hasattr(subprocess, 'CREATE_NEW_CONSOLE') else 0
            )
            
            # Wait a few seconds and check if it started
            await asyncio.sleep(3)
            
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                if response.status_code == 200:
                    return {
                        "success": True,
                        "message": "🦆 Quack! Ollama service started successfully!",
                        "started": True
                    }
                else:
                    return {
                        "success": False,
                        "message": "🦆 Quack! Ollama started but isn't responding properly. Try manually: ollama serve",
                        "partial_success": True
                    }
            except:
                return {
                    "success": False,
                    "message": "🦆 Quack! Started Ollama but can't verify it's working. Check manually.",
                    "partial_success": True
                }
                
        except FileNotFoundError:
            return {
                "success": False,
                "message": "🦆 Quack! Ollama isn't installed. Please install it from https://ollama.ai/download",
                "not_installed": True
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"🦆 Quack! Failed to start Ollama: {str(e)}",
                "error": str(e)
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": "🦆 Quack! Something went wrong trying to start Ollama",
            "error": str(e)
        }