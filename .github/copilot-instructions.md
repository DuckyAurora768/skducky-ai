# SkDucky AI - AI Coding Assistant Instructions

## Project Overview
SkDucky AI is a **Skript code generation and assistance system** using FastAPI that helps users generate Minecraft Skript code through an AI learning service. The system learns from examples and provides code generation, autocomplete, templates, and code explanation features.

## Architecture & Key Components

### Core Services (`services/`)
- **`SkDuckyAIService`** - Main AI service that learns from examples and generates Skript code
  - Uses intelligent word matching with relevance scoring for better code generation
  - Persists learned examples to `training_data.json` with metadata (timestamps, usage counts)
  - Maintains knowledge base in `knowledge_base.json` with patterns, best practices, and common errors
  - Returns structured responses with code, explanations, and learning attribution
- **`SkriptParser`** - Referenced but not yet implemented, intended for Skript syntax parsing

### API Layer (`routes/`)
- **FastAPI routers** organized by functionality: `ai`, `parser`, `documentation`, `snippets`
- **AI endpoints**: 
  - `/generate` - Generate code from natural language prompts
  - `/learn` - Teach the AI new examples
  - `/examples` - Retrieve all learned examples
  - `/autocomplete` - Code completion suggestions
  - `/templates` - Get predefined code templates
  - `/explain` - Analyze and explain code

### Data Models (`models/`)
- `AIRequest/AIResponse` - Core request/response models for code generation
- `LearnRequest` - Model for teaching new examples to the AI
- `AutocompleteRequest/AutocompleteResponse` - Code completion models  
- `SkriptCode` - Represents Skript code for analysis

### Frontend (`static/`)
- **`index.html`** - Complete web interface for interacting with the AI
  - Code generation form with explanation options
  - Learning interface to teach new examples
  - Examples browser to view learned patterns
  - Responsive design with loading states and error handling

## Critical Patterns & Conventions

### Learning System Architecture
```python
# The AI service learns through examples with metadata
ai_service.learn("give 1 diamond on join", "on join:\n    give 1 diamond to player")

# Generation uses intelligent relevance scoring
request = AIRequest(prompt="when a player joins, he gets a diamond")
response = ai_service.generate_code(request)
```

### Intelligent Matching Algorithm
- **Word overlap scoring**: Measures exact word matches between prompts
- **Substring matching**: Handles partial word matches and variations
- **Usage tracking**: Increments usage_count for popular examples
- **Relevance threshold**: Only returns matches above minimum confidence

### Service Instantiation Pattern
```python
# In routes - services are instantiated at module level
router = APIRouter(tags=["ai"])
ai_service = SkDuckyAIService()  # Singleton pattern per router
```

### Response Structure Convention
All AI responses include:
- `code` - Generated Skript code
- `explanation` - Human-readable explanation with relevance score
- `message` - Status/feedback message
- `learned_from` - Attribution to source example

## Development Workflows

### Testing the AI Service
```python
# Fixed version - use SkDuckyAIService() not AIService()
from services.ai_service import SkDuckyAIService
ai = SkDuckyAIService()
```

### Adding New Routes
1. Create router in `routes/<feature>.py`
2. Import in `routes/__init__.py` 
3. Follow pattern: `router as <feature>_router`
4. Include in `main.py` with prefix `/api/v1`

### Data Persistence Structure
```json
// training_data.json
[
  {
    "prompt": "give diamond on join",
    "code": "on join:\n    give 1 diamond to player",
    "timestamp": "2025-01-31T...",
    "usage_count": 5
  }
]

// knowledge_base.json
{
  "patterns": { "join_event": {...} },
  "best_practices": [...],
  "common_errors": [...]
}
```

## Known Issues & Gotchas

### Fixed Issues
- ✅ **Test file bug**: `services/test_ai.py` now uses `SkDuckyAIService()` instead of undefined `AIService()`
- ✅ **Missing routes**: Added `/learn` and `/examples` endpoints for frontend integration
- ✅ **Frontend integration**: Created functional HTML interface with proper API calls
- ✅ **Internationalization**: All interface text, messages, and examples converted to English

### Missing Dependencies
- **Pydantic**: Required for data validation but may need installation
- **FastAPI/Uvicorn**: Web framework dependencies need installation

### Implementation Gaps
- **Parser service**: `SkriptParser` referenced but not implemented
- **External models**: Routes expect models from `models` module which may have import issues
- **Error handling**: File I/O operations need better exception handling

## Integration Points

### External Dependencies
- **FastAPI** - Web framework for API layer
- **Pydantic** - Data validation and serialization  
- **Uvicorn** - ASGI server for running the application
- **Skript Language** - Target code generation format (Minecraft plugin scripting)

### Data Flow
1. User submits prompt via frontend or `/generate` endpoint
2. `SkDuckyAIService.generate_code()` calculates relevance scores against learned examples
3. Best match returned with explanation including confidence and usage statistics
4. New examples added via `/learn` endpoint with automatic metadata
5. All interactions persist to JSON files for continuous learning

### Frontend Integration
- **API Base**: `/api/v1` prefix for all API calls
- **CORS enabled**: Allows frontend to communicate with backend
- **Static files**: Served from `/static` directory via FastAPI
- **Real-time updates**: Frontend fetches examples and updates displays dynamically
- **English interface**: All UI text, placeholders, and messages in English

## Startup Instructions

1. **Install dependencies**: `pip install fastapi uvicorn pydantic`
2. **Run server**: `python main.py` or `uvicorn main:app --reload`
3. **Access interface**: `http://localhost:8000` for web UI
4. **API documentation**: `http://localhost:8000/docs` for interactive API docs

## English Language Support

The entire system now operates in English:
- **Web interface**: All buttons, labels, and messages in English
- **API responses**: Error messages and explanations in English
- **Initial examples**: Default examples use English descriptions and comments
- **Knowledge base**: Best practices and common errors in English
- **Code comments**: Generated Skript code includes English comments
