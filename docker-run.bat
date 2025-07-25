@echo off
echo 🐳 Ultimate Job Applier - Docker Setup
echo =====================================

echo.
echo 📋 Checking Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker not found! Please install Docker Desktop first.
    echo 📖 Download from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo ✅ Docker found!
echo.

echo 🔧 Building Docker image...
docker-compose build

if %errorlevel% neq 0 (
    echo ❌ Build failed!
    pause
    exit /b 1
)

echo ✅ Build complete!
echo.

echo 🚀 Starting Job Applier...
echo 💡 This will:
echo    - Start Ollama service
echo    - Download AI model (if needed)
echo    - Launch job application system
echo.

docker-compose up

echo.
echo 👋 Job Applier stopped.
pause
