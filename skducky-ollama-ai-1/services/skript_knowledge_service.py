from typing import List, Dict, Any
import json
import os

class SkriptKnowledgeService:
    def __init__(self, knowledge_path: str = "data/knowledge_base.json"):
        self.knowledge_path = knowledge_path
        self.knowledge_base = self.load_knowledge_base()

    def load_knowledge_base(self) -> Dict[str, Any]:
        if os.path.exists(self.knowledge_path):
            with open(self.knowledge_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "patterns": {},
            "best_practices": [],
            "common_errors": []
        }

    def get_patterns(self) -> Dict[str, Any]:
        return self.knowledge_base.get("patterns", {})

    def get_best_practices(self) -> List[str]:
        return self.knowledge_base.get("best_practices", [])

    def get_common_errors(self) -> List[str]:
        return self.knowledge_base.get("common_errors", [])

    def update_knowledge_base(self, new_data: Dict[str, Any]):
        self.knowledge_base.update(new_data)
        self.save_knowledge_base()

    def save_knowledge_base(self):
        with open(self.knowledge_path, "w", encoding="utf-8") as f:
            json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)