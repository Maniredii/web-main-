#!/bin/bash

echo "🐳 Ultimate Job Applier - Docker Setup"
echo "====================================="
echo

echo "📋 Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found! Please install Docker first."
    echo "📖 Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Docker found!"
echo

echo "🔧 Building Docker image..."
docker-compose build

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ Build complete!"
echo

echo "🚀 Starting Job Applier..."
echo "💡 This will:"
echo "   - Start Ollama service"
echo "   - Download AI model (if needed)"
echo "   - Launch job application system"
echo

docker-compose up

echo
echo "👋 Job Applier stopped."
