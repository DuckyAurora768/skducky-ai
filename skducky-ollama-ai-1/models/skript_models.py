from pydantic import BaseModel
from typing import List, Optional

class SkriptCodeRequest(BaseModel):
    prompt: str
    include_explanation: Optional[bool] = False

class SkriptCodeResponse(BaseModel):
    code: str
    explanation: Optional[str] = None
    message: str
    learned_from: Optional[str] = None

class SkriptExample(BaseModel):
    prompt: str
    code: str
    timestamp: str
    usage_count: int

class SkriptKnowledge(BaseModel):
    patterns: dict
    best_practices: List[str]
    common_errors: List[str]