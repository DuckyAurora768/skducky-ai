from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class OllamaRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 150
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0

class OllamaResponse(BaseModel):
    generated_code: str
    explanation: str
    message: str
    learned_from: Optional[str] = None

class OllamaKnowledge(BaseModel):
    patterns: List[Dict[str, Any]]
    best_practices: List[str]
    common_errors: List[str]