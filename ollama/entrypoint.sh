#!/bin/sh

echo "🦆 Starting Ollama server..."
./bin/ollama serve &

echo "⏳ Waiting for Ollama to be ready..."
sleep 10

echo "📥 Downloading CodeLlama model..."
curl -X POST http://localhost:11434/api/pull -d '{"name": "codellama"}'

echo "✅ CodeLlama ready! Ollama service running..."
sleep 5

# Keep the container running
tail -f /dev/null
