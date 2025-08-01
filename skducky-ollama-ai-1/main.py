from fastapi import FastAPI
from services.ollama_ai_service import OllamaAIService
from services.skript_knowledge_service import SkriptKnowledgeService

app = FastAPI()

# Initialize services
ollama_service = OllamaAIService()
knowledge_service = SkriptKnowledgeService()

@app.get("/")
def read_root():
    return {"message": "Welcome to the SkDucky Ollama AI service!"}

@app.post("/generate_skript_code/")
def generate_skript_code(prompt: str):
    response = ollama_service.generate_code(prompt)
    return response

@app.get("/knowledge/")
def get_knowledge():
    patterns = knowledge_service.get_patterns()
    best_practices = knowledge_service.get_best_practices()
    return {"patterns": patterns, "best_practices": best_practices}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)