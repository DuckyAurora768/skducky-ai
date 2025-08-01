# SkDucky AI - Ollama Private Service

This directory contains the configuration for running Ollama as a private service on Render.com.

## 🏗️ Architecture

- **Main App**: SkDucky AI FastAPI application
- **Ollama Service**: Private service running CodeLlama model
- **Communication**: Internal networking between services

## 📁 Files

- `Dockerfile`: Multi-stage build for Ollama with CodeLlama
- `entrypoint.sh`: Startup script that downloads CodeLlama model
- `README.md`: This documentation

## 🚀 Deployment

The private service is automatically deployed when you push to main branch.

1. Render builds the Ollama Docker image
2. Downloads CodeLlama model on startup
3. Main app connects via internal URL
4. CodeLlama + Examples hybrid system activated!

## 🔧 Configuration

The main app receives the Ollama URL via environment variable:
```yaml
envVars:
  - key: OLLAMA_URL
    fromService:
      name: skducky-ollama
      type: pserv
      property: hostport
```

## 🦆 Benefits

- ✅ Dedicated resources for Ollama
- ✅ CodeLlama model always available  
- ✅ Internal networking (secure + fast)
- ✅ Automatic scaling and management
- ✅ Perfect for hybrid AI system
