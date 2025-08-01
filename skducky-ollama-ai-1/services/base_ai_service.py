class BaseAIService:
    def __init__(self, training_path: str, knowledge_path: str):
        self.training_path = training_path
        self.knowledge_path = knowledge_path
        self.examples = []
        self.knowledge = {}

        self.load_examples()
        self.load_knowledge_base()

    def load_examples(self):
        try:
            with open(self.training_path, "r", encoding="utf-8") as f:
                self.examples = json.load(f)
        except Exception as e:
            print(f"Error loading examples: {e}")

    def load_knowledge_base(self):
        try:
            with open(self.knowledge_path, "r", encoding="utf-8") as f:
                self.knowledge = json.load(f)
        except Exception as e:
            print(f"Error loading knowledge base: {e}")

    def save_examples(self):
        try:
            with open(self.training_path, "w", encoding="utf-8") as f:
                json.dump(self.examples, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving examples: {e}")

    def save_knowledge_base(self):
        try:
            with open(self.knowledge_path, "w", encoding="utf-8") as f:
                json.dump(self.knowledge, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving knowledge base: {e}")

    def generate_code(self, prompt: str):
        raise NotImplementedError("Subclasses should implement this method.")