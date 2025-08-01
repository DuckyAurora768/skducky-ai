from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from models import DocumentationQuery, DocumentationResult

router = APIRouter(tags=["documentation"])

class DocumentationService:
    def __init__(self):
        self.documentation = {
            "events": [
                {
                    "name": "on join",
                    "description": "Called when a player joins the server",
                    "examples": ["on join:", "    send \"Welcome %player%!\" to player"],
                    "since": "1.0",
                    "category": "player",
                    "addon": "skript"
                },
                {
                    "name": "on quit",
                    "description": "Called when a player leaves the server",
                    "examples": ["on quit:", "    broadcast \"%player% left the game\""],
                    "since": "1.0",
                    "category": "player",
                    "addon": "skript"
                },
                {
                    "name": "on death",
                    "description": "Called when an entity dies",
                    "examples": ["on death of player:", "    send \"You died!\" to victim"],
                    "since": "1.0",
                    "category": "entity",
                    "addon": "skript"
                },
                {
                    "name": "on block break",
                    "description": "Called when a block is broken",
                    "examples": ["on block break:", "    cancel event"],
                    "since": "1.0",
                    "category": "block",
                    "addon": "skript"
                },
                {
                    "name": "on right click",
                    "description": "Called when a player right clicks",
                    "examples": ["on right click on oak sign:", "    send \"You clicked a sign!\" to player"],
                    "since": "1.0",
                    "category": "interaction",
                    "addon": "skript"
                }
            ],
            "effects": [
                {
                    "name": "send",
                    "syntax": "send %texts% to %players%",
                    "description": "Sends a message to players",
                    "examples": ["send \"Hello!\" to player", "send \"&aGreen text\" to all players"],
                    "since": "1.0",
                    "category": "message",
                    "addon": "skript"
                },
                {
                    "name": "teleport",
                    "syntax": "teleport %entities% to %location%",
                    "description": "Teleports entities to a location",
                    "examples": ["teleport player to spawn", "teleport all players to {arena::spawn}"],
                    "since": "1.0",
                    "category": "movement",
                    "addon": "skript"
                },
                {
                    "name": "give",
                    "syntax": "give %items% to %players%",
                    "description": "Gives items to players",
                    "examples": ["give 1 diamond to player", "give 64 emeralds to all players"],
                    "since": "1.0",
                    "category": "item",
                    "addon": "skript"
                },
                {
                    "name": "set",
                    "syntax": "set %~objects% to %objects%",
                    "description": "Sets a value to an expression",
                    "examples": ["set player's health to 10", "set {variable} to true"],
                    "since": "1.0",
                    "category": "variable",
                    "addon": "skript"
                }
            ],
            "expressions": [
                {
                    "name": "player",
                    "return_type": "player",
                    "description": "The player involved in an event",
                    "examples": ["%player%", "player's name", "uuid of player"],
                    "since": "1.0",
                    "category": "player",
                    "addon": "skript"
                },
                {
                    "name": "location",
                    "return_type": "location",
                    "description": "The location of an entity or block",
                    "examples": ["player's location", "location of event-block"],
                    "since": "1.0",
                    "category": "location",
                    "addon": "skript"
                },
                {
                    "name": "health",
                    "return_type": "number",
                    "description": "The health of an entity",
                    "examples": ["player's health", "victim's health"],
                    "since": "1.0",
                    "category": "entity",
                    "addon": "skript"
                }
            ],
            "conditions": [
                {
                    "name": "is online",
                    "syntax": "%offlineplayers% (is|are) online",
                    "description": "Checks if a player is online",
                    "examples": ["player is online", "arg-1 is not online"],
                    "since": "1.0",
                    "category": "player",
                    "addon": "skript"
                },
                {
                    "name": "has permission",
                    "syntax": "%players% (has|have) permission %text%",
                    "description": "Checks if a player has a permission",
                    "examples": ["player has permission \"admin.use\"", "player doesn't have permission \"build.break\""],
                    "since": "1.0",
                    "category": "player",
                    "addon": "skript"
                },
                {
                    "name": "is set",
                    "syntax": "%~objects% (is|are) set",
                    "description": "Checks if a variable is set",
                    "examples": ["{variable} is set", "{home::%player%} is not set"],
                    "since": "1.0",
                    "category": "variable",
                    "addon": "skript"
                }
            ],
            "types": [
                {
                    "name": "player",
                    "description": "An online player",
                    "examples": ["player", "all players", "player argument"],
                    "category": "entity",
                    "addon": "skript"
                },
                {
                    "name": "item",
                    "description": "An item or item type",
                    "examples": ["diamond", "64 emeralds", "iron sword"],
                    "category": "item",
                    "addon": "skript"
                },
                {
                    "name": "location",
                    "description": "A location in a world",
                    "examples": ["player's location", "spawn", "location at (0, 64, 0)"],
                    "category": "world",
                    "addon": "skript"
                }
            ],
            "functions": [
                {
                    "name": "floor",
                    "syntax": "floor(%number%)",
                    "description": "Rounds a number down",
                    "examples": ["floor(5.8)", "set {_rounded} to floor(player's health)"],
                    "since": "2.2",
                    "category": "math",
                    "addon": "skript"
                },
                {
                    "name": "random",
                    "syntax": "random(%number%, %number%)",
                    "description": "Returns a random number between two values",
                    "examples": ["random(1, 10)", "set {_chance} to random(0, 100)"],
                    "since": "2.2",
                    "category": "math",
                    "addon": "skript"
                }
            ],
            "skbee": [
                {
                    "name": "scoreboard",
                    "syntax": "set line %number% of scoreboard of %player% to %text%",
                    "description": "Manages player scoreboards",
                    "examples": ["set title of scoreboard of player to \"&6&lServer\"", "set line 1 of scoreboard of player to \"&aOnline: %size of all players%\""],
                    "category": "display",
                    "addon": "skbee"
                },
                {
                    "name": "nbt",
                    "syntax": "nbt of %item/entity/block%",
                    "description": "Access NBT data",
                    "examples": ["set {_nbt} to nbt of player's tool", "add \"{Enchantments:[{id:sharpness,lvl:5}]}\" to nbt of player's tool"],
                    "category": "nbt",
                    "addon": "skbee"
                },
                {
                    "name": "structure",
                    "syntax": "save structure between %location% and %location% as %text%",
                    "description": "Save and load structures",
                    "examples": ["save structure between {pos1} and {pos2} as \"mybuilding\"", "load structure \"mybuilding\" at player's location"],
                    "category": "world",
                    "addon": "skbee"
                }
            ]
        }
        
    def search(self, query: str, category: Optional[str] = None, addon: Optional[str] = None) -> List[dict]:
        results = []
        query_lower = query.lower()
        
        for doc_type, items in self.documentation.items():
            for item in items:
                if addon and item.get("addon", "skript") != addon:
                    continue
                if category and item.get("category") != category:
                    continue
                    
                if (query_lower in item.get("name", "").lower() or
                    query_lower in item.get("description", "").lower() or
                    any(query_lower in ex.lower() for ex in item.get("examples", []))):
                    results.append({**item, "type": doc_type})
                    
        return results

doc_service = DocumentationService()

@router.post("/docs/search", response_model=DocumentationResult)
async def search_documentation(query: DocumentationQuery):
    try:
        results = doc_service.search(query.search, query.category, query.addon)
        categories = list(set(item.get("category", "other") for item in results))
        
        return DocumentationResult(
            items=results,
            total=len(results),
            categories=categories
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/docs/categories")
async def get_categories():
    categories = set()
    for doc_type, items in doc_service.documentation.items():
        for item in items:
            if "category" in item:
                categories.add(item["category"])
    
    return {"categories": sorted(list(categories))}

@router.get("/docs/types")
async def get_documentation_types():
    return {"types": list(doc_service.documentation.keys())}

@router.get("/docs/{doc_type}")
async def get_documentation_by_type(
    doc_type: str,
    category: Optional[str] = Query(None),
    addon: Optional[str] = Query("skript")
):
    if doc_type not in doc_service.documentation:
        raise HTTPException(status_code=404, detail="Documentation type not found")
    
    items = doc_service.documentation[doc_type]
    
    if addon:
        items = [item for item in items if item.get("addon", "skript") == addon]
    if category:
        items = [item for item in items if item.get("category") == category]
    
    return {
        "type": doc_type,
        "items": items,
        "total": len(items)
    }