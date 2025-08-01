from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import os
import re
import requests
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to sys.path to find models
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import models from the centralized models module
from models import AIRequest, AIResponse, LearnRequest

# --- SERVICE ---

class SkDuckyAIService:
    def __init__(self, training_path: str = "training_data.json", knowledge_path: str = "knowledge_base.json"):
        self.examples: List[Dict[str, str]] = []
        self.training_path = training_path
        self.knowledge_path = knowledge_path
        self.learning_enabled = True
        
        # Ollama configuration (disabled in production)
        self.ollama_base_url = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
        self.ollama_model = "codellama"
        self.ollama_enabled = os.environ.get("OLLAMA_ENABLED", "false").lower() == "true"
        
        # Inicializar knowledge base
        self.knowledge = {
            "patterns": {},
            "best_practices": [],
            "common_errors": []
        }
        
        self.load_examples()
        self.load_knowledge_base()
        self._check_ollama_availability()

    def learn(self, prompt: str, code: str):
        """Learn a new example with timestamp and duck charm"""
        prompt = prompt.strip().lower()
        code = code.strip()

        if not self.learning_enabled:
            return "🦆 Quack! Learning is disabled right now, but I'm still a smart duck! 🧠"

        # Add example metadata
        example = {
            "prompt": prompt,
            "code": code,
            "timestamp": datetime.now().isoformat(),
            "usage_count": 0
        }
        
        self.examples.append(example)
        self.save_examples()
        return f"🦆 Quack quack! I learned a new trick: '{prompt}' 📚✨"

    def generate_code(self, request: AIRequest) -> AIResponse:
        """Generate code using intelligent matching, knowledge base, and optionally Ollama"""
        prompt = request.prompt.strip().lower()

        # Check if Ollama should be used and is available
        if hasattr(request, 'use_ollama') and request.use_ollama and self.ollama_enabled:
            ollama_result = self.generate_with_ollama(request.prompt, True)
            if ollama_result.get("code"):
                return AIResponse(
                    code=ollama_result["code"],
                    explanation=ollama_result.get("explanation", "Generated with Ollama AI"),
                    confidence=0.85,  # High confidence for Ollama
                    source="ollama",
                    examples_used=[],
                    model_info=f"Ollama {self.ollama_model}",
                    message=ollama_result.get("message", "Generated with Ollama")
                )

        # First, try intelligent pattern matching using knowledge base
        intelligent_result = self._try_intelligent_generation(prompt)
        if intelligent_result:
            # Check if this matches any known error patterns
            error_check = self._check_error_patterns(prompt, intelligent_result.code)
            if error_check and error_check["warning"]:
                # Modify the response to include warning
                intelligent_result.explanation += (
                    f"\n\n⚠️ WARNING: Similar code has been marked as incorrect {error_check['occurrences']} time(s) before.\n"
                    f"Known issue: {error_check['issue']}\n"
                    f"Please verify this is what you need, or provide feedback if it's wrong again."
                )
                intelligent_result.message += " (with error pattern warning)"
            
            return intelligent_result

        # Fallback to example matching
        relevant = []
        
        for ex in self.examples:
            score = self._calculate_relevance_score(prompt, ex["prompt"])
            if score > 0:
                relevant.append((ex, score))
        
        # Sort by relevance
        relevant.sort(key=lambda x: x[1], reverse=True)

        if relevant:
            best_example, score = relevant[0]
            
            # Check if this example was marked as incorrect before
            error_check = self._check_error_patterns(prompt, best_example["code"])
            if error_check and error_check["warning"]:
                # Skip this example and try the next one
                for alt_example, alt_score in relevant[1:]:
                    alt_error_check = self._check_error_patterns(prompt, alt_example["code"])
                    if not alt_error_check or not alt_error_check["warning"]:
                        best_example, score = alt_example, alt_score
                        break
            
            # Increment usage counter
            best_example["usage_count"] = best_example.get("usage_count", 0) + 1
            self.save_examples()
            
            explanation = None
            if request.include_explanation:
                explanation = (
                    f"This code was generated based on a similar example: '{best_example['prompt']}'.\n"
                    f"Relevance: {score:.2f}. Used {best_example['usage_count']} times.\n"
                    f"Does this code work for your case? If not, you can teach me a more specific example."
                )
                
                # Add error pattern warning if applicable
                final_error_check = self._check_error_patterns(prompt, best_example["code"])
                if final_error_check and final_error_check["warning"]:
                    explanation += (
                        f"\n\n⚠️ Note: Similar approach has had issues before ({final_error_check['occurrences']} times).\n"
                        f"Previous issue: {final_error_check['issue']}\n"
                        f"Please double-check if this is correct."
                    )
            
            return AIResponse(
                code=best_example["code"],
                explanation=explanation,
                message=f"Code generated from learned examples (relevance: {score:.2f})",
                learned_from=best_example["prompt"]
            )

        return AIResponse(
            code="",
            explanation="",
            message="I don't have enough examples to generate this yet. You can teach me using the learning form.",
            learned_from=None
        )

    def _try_intelligent_generation(self, prompt: str) -> Optional[AIResponse]:
        """Try to generate code using intelligent pattern analysis from learned examples"""
        
        # First, try to learn from existing examples using pattern recognition
        pattern_result = self._analyze_learned_patterns(prompt)
        if pattern_result:
            return pattern_result
        
        # Fallback to basic hardcoded patterns only for very specific cases
        if "command" in prompt:
            # Only keep the most basic kick command as fallback
            if "kick" in prompt and not any("kick" in ex["prompt"] for ex in self.examples):
                code = """command /kick <player> [<text>]:
    permission: op
    trigger:
        if arg-2 is set:
            kick arg-1 due to "%arg-2%"
        else:
            kick arg-1 due to "Kicked by an operator\""""
            
                explanation = (
                    "Generated using basic fallback pattern (no learned examples found):\n"
                    "• Basic kick command structure\n"
                    "• This is a temporary solution - please teach better examples!\n\n"
                    "Usage: /kick PlayerName or /kick PlayerName reason"
                )
                
                return AIResponse(
                    code=code,
                    explanation=explanation,
                    message="Generated using basic fallback pattern",
                    learned_from="Basic hardcoded pattern"
                )
        
        return None

    def _analyze_learned_patterns(self, prompt: str) -> Optional[AIResponse]:
        """Analyze patterns from learned examples to generate intelligent responses"""
        if not self.examples:
            return None
        
        # Extract key concepts from the user prompt
        prompt_concepts = self._extract_concepts(prompt)
        
        # Find examples with similar concepts
        pattern_matches = []
        for example in self.examples:
            example_concepts = self._extract_concepts(example["prompt"])
            
            # Calculate concept similarity
            concept_overlap = len(prompt_concepts.intersection(example_concepts))
            if concept_overlap > 0:
                # Analyze the structure of the example code
                code_structure = self._analyze_code_structure(example["code"])
                
                pattern_matches.append({
                    "example": example,
                    "concepts": example_concepts,
                    "overlap": concept_overlap,
                    "structure": code_structure,
                    "relevance": self._calculate_pattern_relevance(prompt_concepts, example_concepts, code_structure)
                })
        
        if not pattern_matches:
            return None
        
        # Sort by relevance
        pattern_matches.sort(key=lambda x: x["relevance"], reverse=True)
        best_match = pattern_matches[0]
        
        # If relevance is high enough, try to adapt the pattern
        if best_match["relevance"] > 0.4:
            adapted_code = self._adapt_code_pattern(prompt, best_match)
            if adapted_code:
                explanation = (
                    f"Generated by learning from pattern in: '{best_match['example']['prompt']}'\n"
                    f"• Detected concepts: {', '.join(prompt_concepts)}\n"
                    f"• Pattern relevance: {best_match['relevance']:.2f}\n"
                    f"• Code structure: {best_match['structure']['type']}\n"
                    f"• Adapted for your specific request\n\n"
                    "This code was intelligently generated by analyzing similar patterns from learned examples."
                )
                
                return AIResponse(
                    code=adapted_code,
                    explanation=explanation,
                    message="Generated using intelligent pattern learning",
                    learned_from=f"Pattern from: {best_match['example']['prompt']}"
                )
        
        return None

    def _extract_concepts(self, text: str) -> set:
        """Extract key concepts from text"""
        text = text.lower()
        
        # Define concept categories
        concepts = set()
        
        # Events
        if any(word in text for word in ["join", "connect", "enter"]):
            concepts.add("join_event")
        if any(word in text for word in ["death", "die", "dies", "kill"]):
            concepts.add("death_event")
        if any(word in text for word in ["break", "destroy"]):
            concepts.add("break_event")
        if any(word in text for word in ["place", "put"]):
            concepts.add("place_event")
        
        # Actions
        if any(word in text for word in ["give", "receive", "get"]):
            concepts.add("give_action")
        if any(word in text for word in ["kick", "remove"]):
            concepts.add("kick_action")
        if any(word in text for word in ["ban", "block"]):
            concepts.add("ban_action")
        if any(word in text for word in ["heal", "restore"]):
            concepts.add("heal_action")
        if any(word in text for word in ["teleport", "tp", "move"]):
            concepts.add("teleport_action")
        if any(word in text for word in ["fly", "flight"]):
            concepts.add("fly_action")
        if any(word in text for word in ["send", "message", "tell"]):
            concepts.add("message_action")
        
        # Entities
        if any(word in text for word in ["player", "user"]):
            concepts.add("player_entity")
        if any(word in text for word in ["mob", "monster", "zombie", "skeleton", "creeper"]):
            concepts.add("mob_entity")
        
        # Items
        if any(word in text for word in ["diamond", "emerald", "gold", "iron", "item"]):
            concepts.add("item_concept")
        
        # Code structures
        if any(word in text for word in ["command", "cmd"]):
            concepts.add("command_structure")
        if any(word in text for word in ["function", "func"]):
            concepts.add("function_structure")
        if any(word in text for word in ["event", "on", "when"]):
            concepts.add("event_structure")
        
        return concepts

    def _analyze_code_structure(self, code: str) -> dict:
        """Analyze the structure of code to understand patterns"""
        structure = {
            "type": "unknown",
            "has_conditions": False,
            "has_permissions": False,
            "has_parameters": False,
            "actions": [],
            "entities": []
        }
        
        lines = code.split('\n')
        first_line = lines[0].strip() if lines else ""
        
        # Determine structure type
        if first_line.startswith("command"):
            structure["type"] = "command"
            if "<" in first_line and ">" in first_line:
                structure["has_parameters"] = True
        elif first_line.startswith("on "):
            structure["type"] = "event"
        elif first_line.startswith("function"):
            structure["type"] = "function"
            if "(" in first_line and ")" in first_line:
                structure["has_parameters"] = True
        
        # Analyze content
        code_lower = code.lower()
        if "permission" in code_lower:
            structure["has_permissions"] = True
        if any(word in code_lower for word in ["if", "else", "while"]):
            structure["has_conditions"] = True
        
        # Extract actions
        if "give" in code_lower:
            structure["actions"].append("give")
        if "kick" in code_lower:
            structure["actions"].append("kick")
        if "ban" in code_lower:
            structure["actions"].append("ban")
        if "heal" in code_lower:
            structure["actions"].append("heal")
        if "teleport" in code_lower:
            structure["actions"].append("teleport")
        if "send" in code_lower:
            structure["actions"].append("send")
        
        return structure

    def _calculate_pattern_relevance(self, prompt_concepts: set, example_concepts: set, code_structure: dict) -> float:
        """Calculate how relevant a pattern is for the current prompt"""
        if not prompt_concepts or not example_concepts:
            return 0.0
        
        # Concept overlap score
        overlap = len(prompt_concepts.intersection(example_concepts))
        concept_score = overlap / len(prompt_concepts.union(example_concepts))
        
        # Structure compatibility score
        structure_score = 0.0
        if "command_structure" in prompt_concepts and code_structure["type"] == "command":
            structure_score = 0.5
        elif "event_structure" in prompt_concepts and code_structure["type"] == "event":
            structure_score = 0.5
        elif "function_structure" in prompt_concepts and code_structure["type"] == "function":
            structure_score = 0.5
        
        # Action compatibility score
        action_score = 0.0
        for concept in prompt_concepts:
            if concept.endswith("_action"):
                action_name = concept.replace("_action", "")
                if action_name in code_structure["actions"]:
                    action_score += 0.2
        
        # Combined score with weights
        total_score = (concept_score * 0.5) + (structure_score * 0.3) + (action_score * 0.2)
        return min(total_score, 1.0)

    def _adapt_code_pattern(self, prompt: str, pattern_match: dict) -> Optional[str]:
        """Adapt a code pattern to match the current prompt"""
        example = pattern_match["example"]
        structure = pattern_match["structure"]
        original_code = example["code"]
        
        # Extract specific details from the prompt
        adapted_code = original_code
        
        # Replace items if different ones are mentioned
        items = ["diamond", "emerald", "gold ingot", "iron ingot", "stone", "coal", "bread", "apple"]
        prompt_lower = prompt.lower()
        
        for item in items:
            if item in prompt_lower and item not in example["prompt"].lower():
                # Find what item to replace in the original code
                for original_item in items:
                    if original_item in original_code.lower():
                        adapted_code = adapted_code.replace(original_item, item)
                        break
        
        # Adapt command names
        if structure["type"] == "command":
            # Extract command name from prompt
            command_indicators = ["command", "cmd"]
            for indicator in command_indicators:
                if indicator in prompt_lower:
                    words = prompt_lower.split()
                    try:
                        idx = words.index(indicator)
                        if idx < len(words) - 1:
                            new_command = words[idx + 1]
                            # Replace command name in code
                            import re
                            adapted_code = re.sub(r'command /\w+', f'command /{new_command}', adapted_code)
                    except ValueError:
                        pass
        
        # Adapt function names
        if structure["type"] == "function":
            # Extract what the function should do
            if "give" in prompt_lower and any(item in prompt_lower for item in items):
                for item in items:
                    if item in prompt_lower:
                        item_name = item.replace(" ", "").replace("ingot", "")
                        new_function_name = f"give{item_name.title()}"
                        adapted_code = re.sub(r'function \w+\(', f'function {new_function_name}(', adapted_code)
                        break
        
        return adapted_code if adapted_code != original_code else None

    def _calculate_relevance_score(self, user_prompt: str, example_prompt: str) -> float:
        """Calculate relevance between prompts using different methods"""
        user_words = set(user_prompt.split())
        example_words = set(example_prompt.split())
        
        # Exact word matches
        common_words = user_words.intersection(example_words)
        word_score = len(common_words) / max(len(user_words), len(example_words))
        
        # Substring matches
        substring_score = 0
        for word in user_words:
            if any(word in ex_word or ex_word in word for ex_word in example_words):
                substring_score += 1
        substring_score = substring_score / len(user_words) if user_words else 0
        
        # Combined score
        return (word_score * 0.7) + (substring_score * 0.3)

    def get_examples(self) -> List[Dict]:
        """Get all learned examples"""
        return sorted(self.examples, key=lambda x: x.get("usage_count", 0), reverse=True)

    def autocomplete(self, code: str, cursor_position: int):
        """Placeholder for autocomplete functionality"""
        # This function would be implemented later
        return ["give", "send", "teleport", "loop", "if", "else"]

    def generate_explanation(self, analysis_type: str, code: str):
        """Placeholder for code explanation"""
        return f"Analysis type '{analysis_type}': This code appears to be valid."

    def calculate_confidence(self, code: str):
        """Placeholder for confidence calculation"""
        return 0.85

    def generate_suggestions(self, code: str):
        """Placeholder for suggestions"""
        return ["Consider adding comments", "Validate variables before using them"]

    def disable_learning(self):
        self.learning_enabled = False

    def enable_learning(self):
        self.learning_enabled = True

    def process_feedback(self, prompt: str, code: str, feedback_type: str, observations: str, corrected_code: Optional[str] = None, source: str = "traditional") -> str:
        """Enhanced feedback processing that trains both traditional AI and Ollama"""
        try:
            # Analyze the specific issues mentioned in the feedback
            feedback_analysis = self._analyze_feedback_specifics(prompt, code, observations, corrected_code)
            
            feedback_entry = {
                "prompt": prompt.strip().lower(),
                "generated_code": code,
                "feedback_type": feedback_type,
                "observations": observations,
                "corrected_code": corrected_code,
                "timestamp": datetime.now().isoformat(),
                "source": source,  # "traditional", "ollama", or "mixed"
                "analysis": feedback_analysis,
                "learning_actions": [],
                "ollama_learning": {}
            }
            
            # Load existing feedback or create new list
            feedback_path = "feedback_data.json"
            feedback_data = []
            if os.path.exists(feedback_path):
                try:
                    with open(feedback_path, "r", encoding="utf-8") as f:
                        feedback_data = json.load(f)
                except json.JSONDecodeError:
                    feedback_data = []
            
            # Process feedback intelligently for traditional system
            response_parts = []
            
            if feedback_type == "correct":
                self._boost_related_examples(prompt)
                feedback_entry["learning_actions"].append("boosted_related_examples")
                response_parts.append("✅ Positive feedback processed for traditional AI")
                
                # Train Ollama with positive examples
                if self.ollama_enabled:
                    ollama_learning = self._train_ollama_positive(prompt, code, observations)
                    feedback_entry["ollama_learning"] = ollama_learning
                    response_parts.append("✅ Ollama learned from successful pattern")
                
            elif feedback_type == "incorrect":
                if corrected_code:
                    # Learn the corrected example with enhanced metadata
                    corrected_example = {
                        "prompt": prompt.strip().lower(),
                        "code": corrected_code.strip(),
                        "timestamp": datetime.now().isoformat(),
                        "usage_count": 0,
                        "source": "user_correction",
                        "corrects_error": feedback_analysis["error_type"],
                        "original_mistake": code,
                        "feedback_context": observations
                    }
                    self.examples.append(corrected_example)
                    self.save_examples()
                    feedback_entry["learning_actions"].append("learned_corrected_version")
                    
                    # Create specific error pattern to avoid in the future
                    self._create_error_pattern(prompt, code, feedback_analysis)
                    feedback_entry["learning_actions"].append("created_error_pattern")
                    
                    response_parts.append("✅ Traditional AI learned from correction")
                    
                    # Train Ollama with negative examples and corrections
                    if self.ollama_enabled:
                        ollama_learning = self._train_ollama_correction(prompt, code, corrected_code, observations, feedback_analysis)
                        feedback_entry["ollama_learning"] = ollama_learning
                        response_parts.append("✅ Ollama learned to avoid this mistake")
                    
                else:
                    # Mark as negative example without correction
                    self._penalize_incorrect_examples(prompt, code)
                    feedback_entry["learning_actions"].append("penalized_incorrect_example")
                    response_parts.append("⚠️ Traditional AI marked example as problematic")
                    
                    # Train Ollama with negative feedback
                    if self.ollama_enabled:
                        ollama_learning = self._train_ollama_negative(prompt, code, observations, feedback_analysis)
                        feedback_entry["ollama_learning"] = ollama_learning
                        response_parts.append("⚠️ Ollama learned to avoid this pattern")
            
            elif feedback_type == "partial":
                # Update knowledge base with nuanced understanding
                self._update_knowledge_from_partial_feedback(prompt, code, observations, corrected_code)
                feedback_entry["learning_actions"].append("updated_knowledge_base")
                response_parts.append("📝 Knowledge base updated with insights")
                
                # Train Ollama with partial feedback
                if self.ollama_enabled:
                    ollama_learning = self._train_ollama_partial(prompt, code, observations, corrected_code, feedback_analysis)
                    feedback_entry["ollama_learning"] = ollama_learning
                    response_parts.append("📝 Ollama learned partial improvements")
            
            # Save comprehensive feedback data
            feedback_data.append(feedback_entry)
            with open(feedback_path, "w", encoding="utf-8") as f:
                json.dump(feedback_data, f, indent=2, ensure_ascii=False)
            
            # Save comprehensive feedback data
            feedback_data.append(feedback_entry)
            with open(feedback_path, "w", encoding="utf-8") as f:
                json.dump(feedback_data, f, indent=2, ensure_ascii=False)
            
            # Update Ollama's learning context file
            if self.ollama_enabled:
                self._update_ollama_learning_context(feedback_entry)
            
            return " | ".join(response_parts) + f" | Total learning actions: {len(feedback_entry['learning_actions'])}"
                
        except Exception as e:
            return f"❌ Error processing feedback: {str(e)}"

    def _analyze_feedback_specifics(self, prompt: str, generated_code: str, observations: str, corrected_code: Optional[str] = None) -> dict:
        """Analyze feedback to identify specific issues and learning opportunities"""
        analysis = {
            "error_type": "unknown",
            "specific_issue": "unspecified",
            "solution_pattern": "none",
            "confidence": 0.0
        }
        
        prompt_lower = prompt.lower()
        code_lower = generated_code.lower()
        obs_lower = observations.lower() if observations else ""
        
        # Identify error types based on observations and code analysis
        
        # 1. Wrong command structure
        if any(word in obs_lower for word in ["wrong command", "incorrect syntax", "bad structure"]):
            analysis["error_type"] = "command_structure"
            if "kick" in prompt_lower and "kick" not in code_lower:
                analysis["specific_issue"] = "generated wrong command type"
            elif "<player>" not in generated_code and "player" in prompt_lower:
                analysis["specific_issue"] = "missing required parameter"
            else:
                analysis["specific_issue"] = "incorrect command structure"
            analysis["confidence"] = 0.8
        
        # 2. Wrong action/effect
        elif any(word in obs_lower for word in ["wrong action", "doesn't do", "should", "instead"]):
            analysis["error_type"] = "wrong_action"
            # Extract what action was expected vs what was generated
            expected_actions = ["kick", "ban", "give", "heal", "teleport", "fly"]
            for action in expected_actions:
                if action in prompt_lower and action not in code_lower:
                    analysis["specific_issue"] = f"should use '{action}' action but didn't"
                    break
            analysis["confidence"] = 0.7
        
        # 3. Permission issues
        elif any(word in obs_lower for word in ["permission", "op", "access"]):
            analysis["error_type"] = "permission_issue"
            if "permission" not in code_lower:
                analysis["specific_issue"] = "missing permission check"
            else:
                analysis["specific_issue"] = "incorrect permission level"
            analysis["confidence"] = 0.6
        
        # 4. Parameter problems
        elif any(word in obs_lower for word in ["parameter", "argument", "missing", "arg"]):
            analysis["error_type"] = "parameter_issue"
            if "<" not in generated_code or ">" not in generated_code:
                analysis["specific_issue"] = "missing command parameters"
            else:
                analysis["specific_issue"] = "incorrect parameter structure"
            analysis["confidence"] = 0.7
        
        # 5. Item/entity mismatches
        elif any(word in obs_lower for word in ["item", "diamond", "emerald", "gold", "iron"]):
            analysis["error_type"] = "item_mismatch"
            items = ["diamond", "emerald", "gold ingot", "iron ingot"]
            for item in items:
                if item in prompt_lower and item not in code_lower:
                    analysis["specific_issue"] = f"should give '{item}' but gave something else"
                    break
            analysis["confidence"] = 0.8
        
        # 6. Event type errors
        elif any(word in obs_lower for word in ["event", "trigger", "when", "on"]):
            analysis["error_type"] = "event_mismatch"
            events = ["join", "death", "break", "place"]
            for event in events:
                if event in prompt_lower and f"on {event}" not in code_lower:
                    analysis["specific_issue"] = f"should trigger on '{event}' event"
                    break
            analysis["confidence"] = 0.7
        
        # Analyze solution pattern from corrected code
        if corrected_code:
            corrected_lower = corrected_code.lower()
            
            # Find what was fixed
            if analysis["error_type"] == "command_structure":
                if "command /" in corrected_lower and "command /" not in code_lower:
                    analysis["solution_pattern"] = "use proper 'command /' syntax"
                elif "<player>" in corrected_code and "<player>" not in generated_code:
                    analysis["solution_pattern"] = "include <player> parameter"
            
            elif analysis["error_type"] == "wrong_action":
                actions_in_correction = []
                for action in ["kick", "ban", "give", "heal", "teleport"]:
                    if action in corrected_lower:
                        actions_in_correction.append(action)
                if actions_in_correction:
                    analysis["solution_pattern"] = f"use {', '.join(actions_in_correction)} action(s)"
            
            elif analysis["error_type"] == "item_mismatch":
                items = ["diamond", "emerald", "gold ingot", "iron ingot"]
                for item in items:
                    if item in corrected_lower and item not in code_lower:
                        analysis["solution_pattern"] = f"give '{item}' specifically"
                        break
        
        return analysis

    def _create_error_pattern(self, prompt: str, incorrect_code: str, analysis: dict):
        """Create a specific error pattern to avoid in the future"""
        try:
            error_patterns_path = "error_patterns.json"
            error_patterns = []
            
            if os.path.exists(error_patterns_path):
                with open(error_patterns_path, "r", encoding="utf-8") as f:
                    error_patterns = json.load(f)
            
            # Create specific error pattern
            error_pattern = {
                "prompt_pattern": prompt.strip().lower(),
                "incorrect_approach": {
                    "code_snippet": incorrect_code,
                    "error_type": analysis["error_type"],
                    "issue": analysis["specific_issue"]
                },
                "avoid_when": self._extract_concepts(prompt),
                "severity": "high" if analysis["confidence"] > 0.7 else "medium",
                "timestamp": datetime.now().isoformat(),
                "occurrences": 1
            }
            
            # Check if similar error pattern already exists
            similar_found = False
            for existing_pattern in error_patterns:
                if (existing_pattern["prompt_pattern"] == error_pattern["prompt_pattern"] and
                    existing_pattern["incorrect_approach"]["error_type"] == error_pattern["incorrect_approach"]["error_type"]):
                    existing_pattern["occurrences"] += 1
                    existing_pattern["timestamp"] = datetime.now().isoformat()
                    similar_found = True
                    break
            
            if not similar_found:
                error_patterns.append(error_pattern)
            
            # Save error patterns
            with open(error_patterns_path, "w", encoding="utf-8") as f:
                json.dump(error_patterns, f, indent=2, ensure_ascii=False)
                
        except Exception:
            pass  # Non-critical, don't break the flow

    def _check_error_patterns(self, prompt: str, proposed_code: str) -> Optional[dict]:
        """Check if the proposed code matches any known error patterns"""
        try:
            error_patterns_path = "error_patterns.json"
            if not os.path.exists(error_patterns_path):
                return None
            
            with open(error_patterns_path, "r", encoding="utf-8") as f:
                error_patterns = json.load(f)
            
            prompt_concepts = self._extract_concepts(prompt)
            
            for pattern in error_patterns:
                # Check if the current prompt has similar concepts to a known error pattern
                pattern_concepts = set(pattern["avoid_when"])
                concept_overlap = len(prompt_concepts.intersection(pattern_concepts))
                
                if concept_overlap >= 2:  # Significant overlap
                    # Check if the proposed code is similar to the known incorrect approach
                    code_similarity = self._calculate_code_similarity(proposed_code, pattern["incorrect_approach"]["code_snippet"])
                    
                    if code_similarity > 0.6:  # High similarity to known error
                        return {
                            "warning": True,
                            "error_type": pattern["incorrect_approach"]["error_type"],
                            "issue": pattern["incorrect_approach"]["issue"],
                            "occurrences": pattern["occurrences"],
                            "confidence": code_similarity
                        }
            
            return None
            
        except Exception:
            return None

    def _calculate_code_similarity(self, code1: str, code2: str) -> float:
        """Calculate similarity between two code snippets"""
        # Simple similarity based on common lines and structure
        lines1 = set(line.strip().lower() for line in code1.split('\n') if line.strip())
        lines2 = set(line.strip().lower() for line in code2.split('\n') if line.strip())
        
        if not lines1 or not lines2:
            return 0.0
        
        common_lines = len(lines1.intersection(lines2))
        total_lines = len(lines1.union(lines2))
        
        return common_lines / total_lines if total_lines > 0 else 0.0
    
    def _boost_related_examples(self, prompt: str):
        """Increase usage count of examples related to successful feedback"""
        prompt = prompt.strip().lower()
        for example in self.examples:
            relevance = self._calculate_relevance_score(prompt, example["prompt"])
            if relevance > 0.3:  # If reasonably related
                example["usage_count"] = example.get("usage_count", 0) + 2  # Boost by 2
        self.save_examples()
    
    def _penalize_incorrect_examples(self, prompt: str, incorrect_code: str):
        """Mark examples as potentially problematic"""
        # For now, just log this. In the future, we could implement
        # a confidence scoring system or negative examples
        try:
            penalty_path = "negative_examples.json"
            penalties = []
            if os.path.exists(penalty_path):
                with open(penalty_path, "r", encoding="utf-8") as f:
                    penalties = json.load(f)
            
            penalties.append({
                "prompt": prompt.strip().lower(),
                "incorrect_code": incorrect_code,
                "timestamp": datetime.now().isoformat()
            })
            
            with open(penalty_path, "w", encoding="utf-8") as f:
                json.dump(penalties, f, indent=2, ensure_ascii=False)
                
        except Exception:
            pass  # Non-critical, so don't break the flow

    def save_examples(self):
        """Save examples with error handling"""
        try:
            with open(self.training_path, "w", encoding="utf-8") as f:
                json.dump(self.examples, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving examples: {e}")

    def load_examples(self):
        """Load examples with error handling"""
        try:
            if os.path.exists(self.training_path):
                with open(self.training_path, "r", encoding="utf-8") as f:
                    self.examples = json.load(f)
            else:
                # Create initial examples if file doesn't exist
                self._create_initial_examples()
        except Exception as e:
            print(f"Error loading examples: {e}")
            self._create_initial_examples()

    def load_knowledge_base(self):
        """Load knowledge base"""
        try:
            if os.path.exists(self.knowledge_path):
                with open(self.knowledge_path, "r", encoding="utf-8") as f:
                    self.knowledge = json.load(f)
            else:
                self._create_initial_knowledge()
                self.save_knowledge_base()
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            self._create_initial_knowledge()

    def save_knowledge_base(self):
        """Save knowledge base"""
        try:
            with open(self.knowledge_path, "w", encoding="utf-8") as f:
                json.dump(self.knowledge, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving knowledge base: {e}")

    def _create_initial_examples(self):
        """Create initial examples with proper structure and duck personality"""
        initial_examples = [
            {
                "prompt": "give diamond on join",
                "code": "on join:\n    welcomePlayer(player)\n\nfunction welcomePlayer(p: player):\n    give 1 diamond to {_p}\n    send \"🦆 Welcome to our pond! Here's a shiny diamond! ✨\" to {_p}",
                "timestamp": datetime.now().isoformat(),
                "usage_count": 0
            },
            {
                "prompt": "teleport to spawn on death",
                "code": "on death:\n    wait 3 seconds\n    respawnPlayer(player)\n\nfunction respawnPlayer(p: player):\n    teleport {_p} to spawn\n    send \"🦆 Quack! You've been teleported back to the pond! 🏠\" to {_p}",
                "timestamp": datetime.now().isoformat(),
                "usage_count": 0
            },
            {
                "prompt": "fly command",
                "code": "command /fly:\n    permission: skript.fly\n    trigger:\n        toggleFlight(player)\n\nfunction toggleFlight(p: player):\n    if flight mode of {_p} is true:\n        set flight mode of {_p} to false\n        send \"🦆 Flight disabled! Back to swimming! 💧\" to {_p}\n    else:\n        set flight mode of {_p} to true\n        send \"🦆 Quack! You can now soar like a duck! 🦅✨\" to {_p}",
                "timestamp": datetime.now().isoformat(),
                "usage_count": 0
            },
            {
                "prompt": "heal command with cooldown",
                "code": "# Options\noptions:\n    heal-cooldown: 30 seconds\n\n# Commands\ncommand /heal [<player>]:\n    permission: skript.heal\n    trigger:\n        performHeal(player, arg-1)\n\n# Functions\nfunction performHeal(executor: player, target: player):\n    if {heal.cooldown::%uuid of {_executor}%} is set:\n        send \"🦆 Quack! You need to wait before healing again! ⏰\" to {_executor}\n        stop\n    \n    set {_target} to {_executor} if {_target} is not set\n    heal {_target}\n    send \"🦆 *healing quacks* You've been healed! 💚✨\" to {_target}\n    if {_target} is not {_executor}:\n        send \"🦆 You healed %{_target}%! Good duck! 👨‍⚕️\" to {_executor}\n    \n    set {heal.cooldown::%uuid of {_executor}%} to true\n    wait {@heal-cooldown}\n    delete {heal.cooldown::%uuid of {_executor}%}",
                "timestamp": datetime.now().isoformat(),
                "usage_count": 0
            }
        ]
        self.examples = initial_examples
        self.save_examples()

    def _create_initial_knowledge(self):
        """Create initial knowledge base"""
        self.knowledge = {
            "patterns": {
                "join_event": {
                    "description": "Event when a player joins the server",
                    "template": "on join:\n    # your code here"
                },
                "command_creation": {
                    "description": "Create a custom command",
                    "template": "command /name:\n    trigger:\n        # your code here"
                },
                "death_event": {
                    "description": "Event when a player dies",
                    "template": "on death:\n    # your code here"
                }
            },
            "best_practices": [
                "Always check permissions before executing important commands",
                "Use clear messages to inform players what's happening",
                "Add delays when necessary to prevent spam",
                "Validate variables before using them"
            ],
            "common_errors": [
                "Not checking if player exists before performing actions",
                "Forgetting to add permissions to important commands",
                "Not handling cases where variables might be null"
            ]
        }

    def _check_ollama_availability(self):
        """Check if Ollama is available"""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            self.ollama_enabled = response.status_code == 200
        except Exception:
            self.ollama_enabled = False
    
    def generate_with_ollama(self, prompt: str, include_explanation: bool = False) -> Dict:
        """Generate Skript code using Ollama AI with enhanced context"""
        if not self.ollama_enabled:
            return {
                "code": "",
                "message": "🦆 Quack! Ollama AI isn't available right now.\n\n💡 To enable advanced AI features:\n1. Visit the Ollama Settings page\n2. Follow the setup guide\n3. Or run setup_ollama.bat\n\nDon't worry - I can still help with basic Skript generation! 🚀",
                "error": "Service unavailable"
            }
        
        try:
            # Build comprehensive context for Ollama
            context = self._build_skript_context_for_ollama(prompt)
            
            # Create enhanced prompt with Skript-specific instructions and duck personality
            enhanced_prompt = f"""You are SkDucky 🦆, an expert Skript developer duck! You're helpful, friendly, and love clean code.

🦆 DUCKY'S SKRIPT RULES:
- Use proper indentation (4 spaces) - ducks like organized nests!
- Always end event/command lines with colons
- Use 'give X Y to player' for items
- Use 'send "message" to player' for messages
- Commands start with 'command /name:'
- Events start with 'on event:'

🏗️ DUCKY'S CODE STRUCTURE (in this order):
1. Options (if needed)
2. Commands 
3. Events
4. Functions (PRIORITIZE functions for complex logic!)

📋 FUNCTION PRIORITY RULE:
- If the logic is more than 3-4 lines, CREATE A FUNCTION!
- Keep events clean by calling functions
- Example: Instead of long code in "on join:", create a "welcomePlayer()" function

REQUEST: {prompt}

RELEVANT EXAMPLES:
{context}

🦆 Generate clean, well-structured Skript code. If it's complex, use functions to keep it tidy!
Remember: A happy duck writes organized code! 🦆✨"""

            # Call Ollama API
            response = self._call_ollama_api(enhanced_prompt)
            
            if response:
                code = self._clean_ollama_generated_code(response)
                
                result = {
                    "code": code,
                    "message": "🦆 Quack! Code generated with Ollama's magic duck powers! ✨",
                    "model_used": self.ollama_model,
                    "source": "ollama"
                }
                
                if include_explanation:
                    explanation = self._generate_ollama_explanation(prompt, code)
                    result["explanation"] = f"🦆 {explanation}"
                    
                return result
            else:
                # Fallback to learning system when Ollama fails
                print("🦆 Ollama timeout/error - falling back to learning system")
                fallback_request = AIRequest(prompt=prompt, include_explanation=include_explanation)
                fallback_result = self.generate_code(fallback_request)
                fallback_result.message = "🦆 Ollama was slow, so I used my learned examples instead! Still good code! ✨"
                return fallback_result.dict()
                
        except Exception as e:
            # Fallback to learning system on any error
            print(f"🦆 Ollama error: {e} - falling back to learning system")
            try:
                fallback_request = AIRequest(prompt=prompt, include_explanation=include_explanation)
                fallback_result = self.generate_code(fallback_request)
                fallback_result.message = f"🦆 Ollama had trouble ({str(e)[:50]}...), but I used my learned examples! ✨"
                return fallback_result.dict()
            except Exception as fallback_error:
                return {
                    "code": "",
                    "message": f"🦆 Both Ollama and learning system failed: {str(fallback_error)}",
                    "error": str(e)
                }
    
    def _build_skript_context_for_ollama(self, prompt: str) -> str:
        """Build comprehensive context from examples, knowledge, and learning feedback"""
        context_parts = []
        prompt_lower = prompt.lower()
        
        # Get relevant examples from existing training data
        relevant_examples = []
        for example in self.examples:
            if any(word in example["prompt"].lower() for word in prompt_lower.split()):
                relevant_examples.append(f"# {example['prompt']}:\n{example['code']}")
        
        context_parts.extend(relevant_examples[:3])  # Limit to 3 most relevant
        
        # Add knowledge patterns if available
        if hasattr(self, 'knowledge') and 'patterns' in self.knowledge:
            for pattern_name, pattern_info in self.knowledge['patterns'].items():
                if any(word in pattern_name.lower() for word in prompt_lower.split()):
                    context_parts.append(f"# {pattern_info['description']}:\n{pattern_info['template']}")
        
        # Add Ollama-specific learning context
        ollama_context = self._get_ollama_learning_context(prompt)
        if ollama_context:
            context_parts.append("# IMPORTANT LEARNING FROM FEEDBACK:")
            context_parts.extend(ollama_context)
        
        return "\n\n".join(context_parts)

    def _get_ollama_learning_context(self, prompt: str) -> List[str]:
        """Get relevant learning context from previous Ollama feedback"""
        try:
            context_path = "ollama_learning_context.json"
            if not os.path.exists(context_path):
                return []
            
            with open(context_path, "r", encoding="utf-8") as f:
                learning_data = json.load(f)
            
            relevant_context = []
            prompt_words = set(prompt.lower().split())
            
            # Find relevant learning examples
            for example in learning_data[-20:]:  # Check last 20 examples
                example_words = set(example.get("prompt", "").lower().split())
                
                # Check for word overlap
                if prompt_words.intersection(example_words):
                    if example["type"] == "positive_feedback":
                        relevant_context.append(f"✅ SUCCESSFUL PATTERN: {example['training_prompt'][:200]}...")
                    elif example["type"] == "correction_training":
                        relevant_context.append(f"⚠️ AVOID THIS MISTAKE: {example['training_prompt'][:200]}...")
                    elif example["type"] == "negative_feedback":
                        relevant_context.append(f"❌ DON'T USE: {example['training_prompt'][:200]}...")
            
            return relevant_context[:3]  # Limit to 3 most relevant
            
        except Exception as e:
            print(f"Error getting Ollama learning context: {e}")
            return []
    
    def _call_ollama_api(self, prompt: str) -> Optional[str]:
        """Make API call to Ollama"""
        try:
            url = f"{self.ollama_base_url}/api/generate"
            
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,  # Lower temperature for faster, more consistent code
                    "top_p": 0.8,
                    "num_predict": 300,  # Limit output length for faster response
                    "num_ctx": 2048,     # Smaller context for faster processing
                    "repeat_penalty": 1.1
                }
            }
            
            # Reduced timeout for faster user experience
            response = requests.post(url, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                print(f"Ollama API error: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Connection error to Ollama: {e}")
            return None
    
    def _clean_ollama_generated_code(self, raw_code: str) -> str:
        """Clean and validate generated Skript code from Ollama"""
        # Remove common Ollama artifacts
        code = raw_code.strip()
        
        # Remove markdown code blocks if present
        if code.startswith("```"):
            lines = code.split("\n")
            code = "\n".join(lines[1:-1]) if len(lines) > 2 else code
        
        # Remove any explanatory text after the code
        lines = code.split("\n")
        clean_lines = []
        
        for line in lines:
            # Stop at common explanation indicators
            if any(indicator in line.lower() for indicator in ["explanation:", "this code", "note:"]):
                break
            clean_lines.append(line)
        
        return "\n".join(clean_lines).strip()
    
    def _generate_ollama_explanation(self, prompt: str, code: str) -> str:
        """Generate explanation for the Skript code using Ollama"""
        explanation_prompt = f"""Explain this Skript code in simple terms:

ORIGINAL REQUEST: {prompt}

GENERATED CODE:
{code}

Provide a brief explanation of what this code does and how it works in Skript."""

        explanation = self._call_ollama_api(explanation_prompt)
        return explanation if explanation else "Code explanation unavailable"
    
    def get_ollama_models(self) -> List[str]:
        """Get list of available Ollama models"""
        try:
            url = f"{self.ollama_base_url}/api/tags"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            else:
                return ["codellama", "llama2", "mistral"]  # Fallback list
                
        except Exception:
            return ["codellama", "llama2", "mistral"]
    
    def switch_ollama_model(self, model_name: str) -> str:
        """Switch to a different Ollama model"""
        self.ollama_model = model_name
        return f"Switched to Ollama model: {model_name}"
    
    def get_ollama_status(self) -> Dict:
        """Get Ollama service status"""
        self._check_ollama_availability()
        return {
            "ollama_available": self.ollama_enabled,
            "current_model": self.ollama_model,
            "base_url": self.ollama_base_url,
            "available_models": self.get_ollama_models() if self.ollama_enabled else []
        }
    
    def learn_from_ollama_feedback(self, prompt: str, ollama_code: str, feedback: str, corrected_code: Optional[str] = None) -> str:
        """Learn from feedback on Ollama-generated code"""
        # Store the feedback for future Ollama context building
        feedback_entry = {
            "prompt": prompt,
            "ollama_generated": ollama_code,
            "feedback": feedback,
            "corrected_code": corrected_code,
            "timestamp": datetime.now().isoformat(),
            "source": "ollama_feedback"
        }
        
        # Save to a special Ollama feedback file
        feedback_path = "ollama_feedback.json"
        try:
            feedbacks = []
            if os.path.exists(feedback_path):
                with open(feedback_path, "r", encoding="utf-8") as f:
                    feedbacks = json.load(f)
            
            feedbacks.append(feedback_entry)
            
            with open(feedback_path, "w", encoding="utf-8") as f:
                json.dump(feedbacks, f, indent=2, ensure_ascii=False)
            
            # Also add corrected code as a new example if provided
            if corrected_code:
                self.learn(prompt, corrected_code)
            
            return "Ollama feedback processed and learned"
            
        except Exception as e:
            return f"Error processing Ollama feedback: {e}"

    def _train_ollama_positive(self, prompt: str, code: str, observations: str) -> Dict:
        """Train Ollama with positive feedback examples"""
        try:
            # Create a positive training pattern for Ollama
            training_prompt = f"""This is an EXCELLENT Skript code example that users love:

USER REQUEST: {prompt}
GENERATED CODE:
{code}

USER FEEDBACK: {observations}

This code worked perfectly. Learn this pattern for similar requests."""
            
            # Store in Ollama training context
            positive_example = {
                "type": "positive_feedback",
                "prompt": prompt,
                "code": code,
                "feedback": observations,
                "training_prompt": training_prompt,
                "timestamp": datetime.now().isoformat(),
                "confidence_boost": 0.2
            }
            
            self._add_to_ollama_context(positive_example)
            
            return {
                "action": "positive_training",
                "confidence_boost": 0.2,
                "pattern_reinforced": True
            }
            
        except Exception as e:
            return {"error": str(e)}

    def _train_ollama_correction(self, prompt: str, wrong_code: str, correct_code: str, observations: str, analysis: Dict) -> Dict:
        """Train Ollama with correction examples"""
        try:
            # Create a correction training pattern for Ollama
            training_prompt = f"""IMPORTANT CORRECTION LESSON:

USER REQUEST: {prompt}

WRONG CODE (AVOID THIS):
{wrong_code}

CORRECT CODE (USE THIS INSTEAD):
{correct_code}

WHY IT WAS WRONG: {observations}
ERROR TYPE: {analysis.get('error_type', 'Unknown')}
SPECIFIC ISSUE: {analysis.get('specific_issue', 'Not specified')}

Remember: When you see requests like "{prompt}", avoid patterns like the wrong code and use patterns like the correct code instead."""
            
            correction_example = {
                "type": "correction_training",
                "prompt": prompt,
                "wrong_code": wrong_code,
                "correct_code": correct_code,
                "feedback": observations,
                "analysis": analysis,
                "training_prompt": training_prompt,
                "timestamp": datetime.now().isoformat(),
                "error_weight": -0.3
            }
            
            self._add_to_ollama_context(correction_example)
            
            return {
                "action": "correction_training",
                "error_pattern_learned": True,
                "correction_reinforced": True
            }
            
        except Exception as e:
            return {"error": str(e)}

    def _train_ollama_negative(self, prompt: str, code: str, observations: str, analysis: Dict) -> Dict:
        """Train Ollama with negative feedback"""
        try:
            training_prompt = f"""AVOID THIS PATTERN:

USER REQUEST: {prompt}

PROBLEMATIC CODE (DON'T GENERATE):
{code}

USER FEEDBACK: {observations}
ERROR TYPE: {analysis.get('error_type', 'Unknown')}

This code didn't work well. For requests like "{prompt}", avoid generating similar patterns."""
            
            negative_example = {
                "type": "negative_feedback",
                "prompt": prompt,
                "code": code,
                "feedback": observations,
                "analysis": analysis,
                "training_prompt": training_prompt,
                "timestamp": datetime.now().isoformat(),
                "avoidance_weight": -0.5
            }
            
            self._add_to_ollama_context(negative_example)
            
            return {
                "action": "negative_training",
                "pattern_to_avoid": True,
                "avoidance_weight": -0.5
            }
            
        except Exception as e:
            return {"error": str(e)}

    def _train_ollama_partial(self, prompt: str, code: str, observations: str, corrected_code: Optional[str], analysis: Dict) -> Dict:
        """Train Ollama with partial feedback"""
        try:
            if corrected_code:
                training_prompt = f"""PARTIAL IMPROVEMENT LESSON:

USER REQUEST: {prompt}

ORIGINAL CODE (PARTIALLY CORRECT):
{code}

IMPROVED CODE:
{corrected_code}

USER FEEDBACK: {observations}

The original code was on the right track but needed improvements. Learn both what worked and what needed fixing."""
            else:
                training_prompt = f"""PARTIAL FEEDBACK:

USER REQUEST: {prompt}

CODE GENERATED:
{code}

USER FEEDBACK: {observations}

This code was partially correct but had some issues. Learn from this feedback for future improvements."""
            
            partial_example = {
                "type": "partial_feedback",
                "prompt": prompt,
                "code": code,
                "corrected_code": corrected_code,
                "feedback": observations,
                "analysis": analysis,
                "training_prompt": training_prompt,
                "timestamp": datetime.now().isoformat(),
                "learning_weight": 0.1
            }
            
            self._add_to_ollama_context(partial_example)
            
            return {
                "action": "partial_training",
                "incremental_learning": True,
                "refinement_applied": bool(corrected_code)
            }
            
        except Exception as e:
            return {"error": str(e)}

    def _add_to_ollama_context(self, training_example: Dict):
        """Add training example to Ollama's learning context"""
        try:
            context_path = "ollama_learning_context.json"
            context_data = []
            
            if os.path.exists(context_path):
                with open(context_path, "r", encoding="utf-8") as f:
                    context_data = json.load(f)
            
            context_data.append(training_example)
            
            # Keep only the last 100 training examples to avoid huge files
            if len(context_data) > 100:
                context_data = context_data[-100:]
            
            with open(context_path, "w", encoding="utf-8") as f:
                json.dump(context_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error adding to Ollama context: {e}")

    def _update_ollama_learning_context(self, feedback_entry: Dict):
        """Update Ollama's overall learning context"""
        try:
            # Create a comprehensive learning summary for Ollama
            learning_summary = {
                "timestamp": datetime.now().isoformat(),
                "feedback_type": feedback_entry["feedback_type"],
                "prompt_pattern": feedback_entry["prompt"],
                "learning_insights": feedback_entry["learning_actions"],
                "ollama_specific": feedback_entry["ollama_learning"]
            }
            
            summary_path = "ollama_learning_summary.json"
            summaries = []
            
            if os.path.exists(summary_path):
                with open(summary_path, "r", encoding="utf-8") as f:
                    summaries = json.load(f)
            
            summaries.append(learning_summary)
            
            # Keep only the last 50 summaries
            if len(summaries) > 50:
                summaries = summaries[-50:]
            
            with open(summary_path, "w", encoding="utf-8") as f:
                json.dump(summaries, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error updating Ollama learning context: {e}")

    def _update_knowledge_from_partial_feedback(self, prompt: str, code: str, observations: str, corrected_code: Optional[str]):
        """Update knowledge base with insights from partial feedback"""
        try:
            # Extract learning insights from partial feedback
            if "permission" in observations.lower():
                self.knowledge["best_practices"].append(f"For requests like '{prompt}': Always check permissions")
            
            if "message" in observations.lower() and "player" in observations.lower():
                self.knowledge["best_practices"].append(f"For requests like '{prompt}': Include user feedback messages")
            
            if corrected_code and "wait" in corrected_code and "wait" not in code:
                self.knowledge["best_practices"].append(f"For requests like '{prompt}': Consider adding delays")
            
            # Remove duplicates
            self.knowledge["best_practices"] = list(set(self.knowledge["best_practices"]))
            
            # Save updated knowledge
            self.save_knowledge_base()
            
        except Exception as e:
            print(f"Error updating knowledge from partial feedback: {e}")

# --- MANUAL TESTING ---

if __name__ == "__main__":
    ai = SkDuckyAIService()

    # Teach something
    print(ai.learn("when player joins give diamond", "on join:\n    give 1 diamond to player"))

    # Ask something similar
    request = AIRequest(prompt="when a player enters give them 1 diamond")
    result = ai.generate_code(request)
    print(result.code)
    print(result.explanation)
