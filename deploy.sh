#!/bin/bash

# ==============================================
# LumiRun System Linux Deployment Script
# ==============================================

set -e

echo "=============================================="
echo "  LumiRun System Linux Deployment Script"
echo "=============================================="
echo ""

# Set variables
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "WARNING: Running as root is not recommended!"
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "[STEP 1/6] Checking system environment..."

# Check Python
echo "[CHECK] Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found! Please install Python 3.10+ first."
    echo "       Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
    echo "       CentOS/RHEL: sudo yum install python3 python3-pip"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "OK: Python $PYTHON_VERSION installed"

# Check Node.js
echo "[CHECK] Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js not found! Please install Node.js 18+ first."
    echo "       Ubuntu/Debian: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -"
    echo "                     sudo apt-get install -y nodejs"
    echo "       CentOS/RHEL: curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -"
    echo "                     sudo yum install -y nodejs"
    exit 1
fi
NODE_VERSION=$(node --version)
echo "OK: Node.js $NODE_VERSION installed"

# Check MySQL
echo "[CHECK] MySQL installation..."
if ! command -v mysql &> /dev/null; then
    echo "WARN: MySQL client not found. Please ensure MySQL server is installed and running."
fi

echo ""
echo "[STEP 2/6] Creating directory structure..."

# Create necessary directories
mkdir -p "$PROJECT_DIR/logs"
echo "OK: logs directory created"

mkdir -p "$BACKEND_DIR/uploads"
echo "OK: backend/uploads directory created"

echo ""
echo "[STEP 3/6] Configuring backend environment..."

# Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "[CREATE] Python virtual environment..."
    python3 -m venv "$VENV_DIR"
    if [ $? -eq 0 ]; then
        echo "OK: Virtual environment created successfully"
    else
        echo "ERROR: Failed to create virtual environment!"
        exit 1
    fi
else
    echo "OK: Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo "[INSTALL] Python dependencies..."
source "$VENV_DIR/bin/activate"

# Try to install dependencies
pip install -r "$BACKEND_DIR/requirements.txt"
if [ $? -eq 0 ]; then
    echo "OK: Python dependencies installed successfully"
else
    echo "WARN: Failed to install with default source, trying China mirror..."
    pip install -r "$BACKEND_DIR/requirements.txt" -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
    if [ $? -eq 0 ]; then
        echo "OK: Python dependencies installed successfully with China mirror"
    else
        echo "ERROR: Failed to install Python dependencies!"
        exit 1
    fi
fi

echo ""
echo "[STEP 4/6] Configuring frontend environment..."

cd "$FRONTEND_DIR"

# Install Node.js dependencies
echo "[INSTALL] Node.js dependencies..."
npm install
if [ $? -eq 0 ]; then
    echo "OK: Node.js dependencies installed successfully"
else
    echo "WARN: Failed to install with default registry, trying China mirror..."
    npm config set registry https://registry.npmmirror.com/
    npm install
    if [ $? -eq 0 ]; then
        echo "OK: Node.js dependencies installed successfully with China mirror"
    else
        echo "ERROR: Failed to install Node.js dependencies!"
        exit 1
    fi
fi

# Build frontend
echo "[BUILD] Frontend project..."
npm run build
if [ $? -eq 0 ]; then
    echo "OK: Frontend project built successfully"
else
    echo "ERROR: Failed to build frontend project!"
    exit 1
fi

echo ""
echo "[STEP 5/6] Configuring environment variables..."

# Copy environment templates
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo "[COPY] Backend environment config..."
    cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
    if [ $? -eq 0 ]; then
        echo "OK: Backend environment config created"
    else
        echo "ERROR: Failed to create backend environment config!"
    fi
else
    echo "OK: Backend environment config exists"
fi

if [ ! -f "$FRONTEND_DIR/.env.local" ]; then
    echo "[COPY] Frontend environment config..."
    cp "$FRONTEND_DIR/.env.example" "$FRONTEND_DIR/.env.local"
    if [ $? -eq 0 ]; then
        echo "OK: Frontend environment config created"
    else
        echo "ERROR: Failed to create frontend environment config!"
    fi
else
    echo "OK: Frontend environment config exists"
fi

echo ""
echo "[STEP 6/6] Initializing database..."

# Initialize database tables and data
echo "[INIT] Creating database tables..."
python "$BACKEND_DIR/init_db.py"
if [ $? -eq 0 ]; then
    echo "OK: Database tables created successfully"
else
    echo "WARN: Failed to create database tables. Please check your database configuration."
fi

echo "[INIT] Initializing roles, users and permissions..."
python "$BACKEND_DIR/init_data.py"
if [ $? -eq 0 ]; then
    echo "OK: Database data initialized successfully"
else
    echo "WARN: Failed to initialize database data. Please check your database configuration."
fi

echo ""
echo "=============================================="
echo "DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "=============================================="
echo ""
echo "Default Accounts:"
echo "┌─────────────────────────────┬──────────┬──────────────┬─────────────┐"
echo "│ Email                       │ Username │ Password     │ Role        │"
echo "├─────────────────────────────┼──────────┼──────────────┼─────────────┤"
echo "│ admin@example.com           │ admin    │ Password123  │ Super Admin │"
echo "│ teacher@example.com         │ teacher  │ Password123  │ Teacher     │"
echo "│ student@example.com         │ student  │ Password123  │ Student     │"
echo "└─────────────────────────────┴──────────┴──────────────┴─────────────┘"
echo ""
echo "⚠️  Security: Please change default passwords after first login!"
echo ""
echo "How to start the application:"
echo "-----------------------------"
echo "1. Start backend service:"
echo "   cd $BACKEND_DIR"
echo "   source $VENV_DIR/bin/activate"
echo "   uvicorn main:app --host 0.0.0.0 --port 8000"
echo ""
echo "2. Start frontend service (development mode):"
echo "   cd $FRONTEND_DIR"
echo "   npm run dev"
echo ""
echo "Or use systemd services for production:"
echo "   sudo systemctl start lumirun-backend"
echo "   sudo systemctl start lumirun-frontend"
echo ""
echo "Access URLs:"
echo "   - Frontend: http://localhost:3002"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
