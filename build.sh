#!/bin/bash
# Build script for Render

echo "🦆 Starting SkDucky AI build..."

# Install Python dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Build completed successfully!"
