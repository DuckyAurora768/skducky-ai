from .parser import router as parser_router
from .ai import router as ai_router
from .documentation import router as documentation_router
from .snippets import router as snippets_router

__all__ = ["parser_router", "ai_router", "documentation_router", "snippets_router"]