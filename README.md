# SkDucky AI - Intelligent Skript Code Generator

SkDucky AI is an intelligent assistant that learns from examples to automatically generate Skript code. The system uses simple machine learning to relate natural language descriptions to functional Skript code.

## 🚀 Installation and Usage

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the server
```bash
python main.py
```

### 3. Access the web interface
- **Main interface**: http://localhost:8000
- **API documentation**: http://localhost:8000/docs

## 🎯 Key Features

### ✨ Code Generation
- Describe what you want to do in natural language
- The AI searches for similar examples and generates Skript code
- Includes detailed explanations and relevance scoring

### 📚 Learning System
- Teach new examples to the AI
- Examples are permanently saved in `training_data.json`
- Usage-based scoring: most popular examples get priority

### 💾 Intelligent Persistence
- **`training_data.json`**: Learned examples with metadata (timestamps, usage counters)
- **`knowledge_base.json`**: Patterns, best practices, and common errors
- Automatic loading when service starts

## 📋 Usage Examples

### Generate code
```
Prompt: "when a player joins the server, give them 1 diamond"
Result:
on join:
    give 1 diamond to player
    send "Welcome! I've given you a diamond." to player
```

### Teach the AI
```
Description: "fly command"
Code:
command /fly:
    trigger:
        if player has permission "skript.fly":
            set flight mode of player to true
            send "Flight mode activated!" to player
        else:
            send "You don't have permission to fly" to player
```

## 🔧 API Endpoints

- **POST `/api/v1/generate`** - Generate code from description
- **POST `/api/v1/learn`** - Teach new example
- **GET `/api/v1/examples`** - Get learned examples
- **GET `/api/v1/templates`** - Predefined templates
- **GET `/api/v1/best-practices`** - Best practices

## 🛠️ Development

### Project Structure
```
skducky-ai/
├── main.py                 # Main FastAPI application
├── services/
│   ├── ai_service.py      # AI logic and learning
│   └── test_ai.py         # Service tests
├── routes/
│   ├── ai.py              # AI endpoints
│   └── __init__.py        # Router configuration
├── models/
│   └── __init__.py        # Pydantic models
├── static/
│   └── index.html         # Web interface
└── .github/
    └── copilot-instructions.md
```

### Relevance Algorithm
The system uses a hybrid scoring algorithm:
1. **Exact word matches** (70% of score)
2. **Substring matches** (30% of score)
3. **Usage-based sorting**: Most used examples appear first

## 🎮 For Skript Developers

This system is ideal for:
- **Beginners**: Learn Skript by seeing generated examples
- **Intermediate developers**: Speed up development with base code
- **Teams**: Share common patterns between developers

## 🔍 Troubleshooting

### AI doesn't find examples
- Use more specific keywords
- Teach similar examples first
- Check loaded examples at `/api/v1/examples`

### Connection errors
- Verify the server is running on port 8000
- Check console for dependency errors
- Install dependencies: `pip install -r requirements.txt`

---

Contributions and suggestions are welcome! 🦆
