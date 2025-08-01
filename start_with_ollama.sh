#!/bin/bash
# start_with_ollama.sh - Start SkDucky AI with Ollama

echo "🦆 Starting SkDucky AI with CodeLlama..."

# Start Ollama in background
echo "🔧 Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to start..."
sleep 10

# Pull CodeLlama model if not already available
echo "📥 Ensuring CodeLlama model is available..."
ollama pull codellama:latest || echo "⚠️ CodeLlama download failed, but continuing..."

# Start the FastAPI application
echo "🚀 Starting SkDucky AI application..."
exec gunicorn app:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 300
