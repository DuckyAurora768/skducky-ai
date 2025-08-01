#!/bin/bash
# Build script for Render - Force Python 3.12

echo "🦆 Starting SkDucky AI build with Python 3.12..."

# Check Python version
python --version

# Upgrade pip first
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies with specific Python version
echo "📦 Installing dependencies for Python 3.12..."
pip install -r requirements.txt

echo "✅ Build completed successfully with Python $(python --version)!"
