class OllamaAIService:
    def __init__(self, knowledge_service, ollama_client):
        self.knowledge_service = knowledge_service
        self.ollama_client = ollama_client

    def generate_skript_code(self, prompt: str) -> str:
        """Generate Skript code based on the provided prompt using the Ollama AI model."""
        knowledge = self.knowledge_service.get_relevant_knowledge(prompt)
        response = self.ollama_client.send_request(prompt, knowledge)
        return response.get('code', '')

    def update_knowledge(self):
        """Update the knowledge base with new information from JSON files."""
        self.knowledge_service.load_knowledge()

    def get_best_practices(self) -> list:
        """Retrieve best practices for Skript coding."""
        return self.knowledge_service.get_best_practices()

    def get_common_errors(self) -> list:
        """Retrieve common errors related to Skript coding."""
        return self.knowledge_service.get_common_errors()