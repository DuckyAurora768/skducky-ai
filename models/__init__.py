from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

class SkriptVersion(str, Enum):
    V2_12_0 = "2.12.0"
    V2_11_2 = "2.11.2"
    V2_10_1 = "2.10.1"
    V2_9_5 = "2.9.5"

class AIRequest(BaseModel):
    prompt: str
    context: Optional[str] = ""
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 500
    include_explanation: Optional[bool] = True
    style: Optional[str] = "default"

class AIResponse(BaseModel):
    code: str
    explanation: Optional[str] = None
    confidence: Optional[float] = None
    suggestions: Optional[List[str]] = None
    related_snippets: Optional[List[str]] = None
    message: Optional[str] = None
    learned_from: Optional[str] = None

class LearnRequest(BaseModel):
    prompt: str
    code: str

class AutocompleteRequest(BaseModel):
    code: str
    cursor_position: int
    context_lines: Optional[int] = 5

class AutocompleteResponse(BaseModel):
    suggestions: List[Dict[str, Any]]
    context_aware: bool = False

class SkriptCode(BaseModel):
    code: str
    filename: Optional[str] = None
    version: Optional[SkriptVersion] = SkriptVersion.V2_12_0
    include_skbee: Optional[bool] = True

class ParseResult(BaseModel):
    success: bool
    ast: Optional[Dict[str, Any]] = None
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    syntax_tree: Optional[Dict[str, Any]] = None

class ValidationResult(BaseModel):
    valid: bool
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    suggestions: List[str]

class SnippetRequest(BaseModel):
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    search: Optional[str] = None

class Snippet(BaseModel):
    id: str
    title: str
    description: str
    code: str
    category: str
    tags: List[str]
    author: Optional[str] = None
    version_compatible: List[SkriptVersion]
    requires_addons: List[str]

class DocumentationQuery(BaseModel):
    search: str
    category: Optional[str] = None
    addon: Optional[str] = "skript"

class DocumentationResult(BaseModel):
    items: List[Dict[str, Any]]
    total: int
    categories: List[str]

class FeedbackRequest(BaseModel):
    prompt: str
    code: str
    feedback_type: str  # 'correct' or 'incorrect'
    observations: str
    corrected_code: Optional[str] = None
