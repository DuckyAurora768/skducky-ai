from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

class SkriptVersion(str, Enum):
    V2_12_0 = "2.12.0"
    V2_11_2 = "2.11.2"
    V2_10_1 = "2.10.1"
    V2_9_5 = "2.9.5"

class SkriptCode(BaseModel):
    code: str
    version: Optional[SkriptVersion] = SkriptVersion.V2_12_0
    include_skbee: Optional[bool] = True

class ParseResult(BaseModel):
    success: bool
    ast: Optional[Dict[str, Any]]
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    syntax_tree: Optional[Dict[str, Any]]

class ValidationResult(BaseModel):
    valid: bool
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    suggestions: List[str]

class AIRequest(BaseModel):
    prompt: str
    context: Optional[str] = ""
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 500
    include_explanation: Optional[bool] = True
    style: Optional[str] = "default"
    use_ollama: Optional[bool] = False

class AIResponse(BaseModel):
    code: str
    explanation: Optional[str]
    confidence: float
    suggestions: List[str] = []
    related_snippets: List[str] = []
    source: Optional[str] = "examples"
    examples_used: List[str] = []
    model_info: Optional[str] = ""
    message: Optional[str] = ""

class AutocompleteRequest(BaseModel):
    code: str
    cursor_position: int
    context_lines: Optional[int] = 5

class AutocompleteResponse(BaseModel):
    suggestions: List[Dict[str, Any]]
    context_aware: bool

class SnippetRequest(BaseModel):
    category: Optional[str]
    tags: Optional[List[str]]
    search: Optional[str]

class Snippet(BaseModel):
    id: str
    title: str
    description: str
    code: str
    category: str
    tags: List[str]
    author: Optional[str]
    version_compatible: List[SkriptVersion]
    requires_addons: List[str]

class DocumentationQuery(BaseModel):
    search: str
    category: Optional[str]
    addon: Optional[str] = "skript"

class LearnRequest(BaseModel):
    prompt: str
    code: str
    explanation: Optional[str] = ""

class FeedbackRequest(BaseModel):
    prompt: str
    code: str
    feedback_type: str  # "correct", "incorrect", "partial"
    observations: str
    corrected_code: Optional[str] = None
    source: Optional[str] = "traditional"  # "traditional", "ollama", "mixed"

class DocumentationResult(BaseModel):
    items: List[Dict[str, Any]]
    total: int
    categories: List[str]