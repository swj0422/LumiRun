#!/bin/bash

# ==============================================
# LumiRun System Linux Deployment Script
# ==============================================

set -e

echo "=============================================="
echo "  LumiRun System Linux Deployment Script"
echo "=============================================="
echo ""

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
PYTHON_EXE="$VENV_DIR/bin/python"

if [ "$EUID" -eq 0 ]; then
    echo "WARNING: Running as root is not recommended!"
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

if [ ! -f "$PYTHON_EXE" ]; then
    echo "ERROR: Python virtual environment not found!"
    echo "Please run the full deployment script first."
    exit 1
fi

echo ""
echo "[RUN] Core deployment logic..."
"$PYTHON_EXE" "$PROJECT_DIR/deploy-core.py" --project-dir "$PROJECT_DIR"

if [ $? -eq 0 ]; then
    echo ""
    echo "=============================================="
    echo "DEPLOYMENT COMPLETED SUCCESSFULLY!"
    echo "=============================================="
    echo ""
    echo "How to start the application:"
    echo "-----------------------------"
    echo "1. Start backend service:"
    echo "   cd $PROJECT_DIR/backend"
    echo "   source $VENV_DIR/bin/activate"
    echo "   uvicorn main:app --host 0.0.0.0 --port 8000"
    echo ""
    echo "2. Start frontend service (development mode):"
    echo "   cd $PROJECT_DIR/frontend"
    echo "   npm run dev"
    echo ""
else
    echo ""
    echo "ERROR: Deployment failed! Please check the error messages above."
    echo ""
    exit 1
fi