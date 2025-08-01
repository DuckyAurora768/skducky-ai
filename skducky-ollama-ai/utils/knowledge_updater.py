from typing import Dict, Any
import json
import os

def update_knowledge_base(knowledge_base_path: str, new_data: Dict[str, Any]) -> None:
    """Update the knowledge base with new data."""
    if os.path.exists(knowledge_base_path):
        with open(knowledge_base_path, "r", encoding="utf-8") as f:
            knowledge_base = json.load(f)
    else:
        knowledge_base = {}

    knowledge_base.update(new_data)

    with open(knowledge_base_path, "w", encoding="utf-8") as f:
        json.dump(knowledge_base, f, indent=2, ensure_ascii=False)

def update_training_data(training_data_path: str, new_examples: List[Dict[str, Any]]) -> None:
    """Update the training data with new examples."""
    if os.path.exists(training_data_path):
        with open(training_data_path, "r", encoding="utf-8") as f:
            training_data = json.load(f)
    else:
        training_data = []

    training_data.extend(new_examples)

    with open(training_data_path, "w", encoding="utf-8") as f:
        json.dump(training_data, f, indent=2, ensure_ascii=False)