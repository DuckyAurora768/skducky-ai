# SkDucky Ollama AI

## Project Overview
SkDucky Ollama AI is an AI-powered service designed to generate Skript code for Minecraft using the Ollama AI model. The service leverages a knowledge base built from JSON examples to provide relevant and accurate code suggestions, enhancing the scripting experience for Minecraft developers.

## Features
- **Skript Code Generation**: Generate Skript code snippets based on natural language prompts.
- **Knowledge Integration**: Utilizes a knowledge base of patterns, best practices, and common errors to improve code suggestions.
- **Ollama AI Model**: Integrates with the Ollama AI model for intelligent code generation.

## Project Structure
- **services/**: Contains the core service classes for AI functionality.
  - `ollama_ai_service.py`: Manages code generation using the Ollama AI model.
  - `skript_knowledge_service.py`: Handles loading and updating Skript-related knowledge.
  - `base_ai_service.py`: Provides common functionality for AI services.
  
- **models/**: Defines data models for requests and responses.
  - `ollama_models.py`: Models specific to the Ollama AI service.
  - `skript_models.py`: Models related to Skript code generation.

- **utils/**: Contains utility functions and classes.
  - `ollama_client.py`: Manages communication with the Ollama API.
  - `knowledge_updater.py`: Updates the knowledge base and training data.

- **data/**: Stores JSON files for training data and knowledge.
  - `training_data.json`: Contains training examples for the AI service.
  - `knowledge_base.json`: Holds the knowledge base for the AI service.
  - `skript_patterns.json`: Predefined Skript patterns for code generation.

- **config/**: Configuration settings for the project.
  - `ollama_config.py`: Contains API keys and endpoint URLs.

- **main.py**: Entry point for the application, initializing the AI service.

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd skducky-ollama-ai
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
To run the application, execute the following command:
```
python main.py
```

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.