from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from models import SkriptCode, ParseResult, ValidationResult
from services.parser_service import SkriptParser

router = APIRouter(tags=["parser"])
parser = SkriptParser()

@router.post("/parse", response_model=ParseResult)
async def parse_skript(code: SkriptCode):
    try:
        result = parser.parse(code.code)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/validate", response_model=ValidationResult)
async def validate_skript(code: SkriptCode):
    try:
        parse_result = parser.parse(code.code)
        
        suggestions = []
        if parse_result.errors:
            suggestions.append("Fix syntax errors before running the script")
        if parse_result.warnings:
            suggestions.append("Consider addressing warnings for better code quality")
            
        if "wait" in code.code and "seconds" not in code.code and "minutes" not in code.code:
            suggestions.append("Always specify time units with wait (seconds, minutes, etc.)")
            
        if "{" in code.code and "}" in code.code:
            if "%player%" in code.code and "%player's uuid%" not in code.code:
                suggestions.append("Use %player's uuid% for persistent data storage")
                
        return ValidationResult(
            valid=parse_result.success,
            errors=parse_result.errors,
            warnings=parse_result.warnings,
            suggestions=suggestions
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/syntax/{category}")
async def get_syntax(category: str):
    if category not in parser.syntax:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {
        "category": category,
        "items": parser.syntax[category],
        "total": len(parser.syntax[category])
    }

@router.get("/syntax")
async def get_all_syntax():
    return {
        "categories": list(parser.syntax.keys()),
        "syntax": parser.syntax
    }