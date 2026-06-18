#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

ACTION=${1:-deploy}

# Function to stop the server
stop_server() {
    echo "Stopping FastAPI backend..."
    if [ -f "uvicorn.pid" ]; then
        PID=$(cat uvicorn.pid)
        if kill -0 "$PID" 2>/dev/null; then
            echo "Stopping running FastAPI instance (PID: $PID)..."
            kill "$PID"
            sleep 2
        else
            echo "FastAPI PID $PID is not running."
        fi
    fi

    # Double check if port 8000 is still bound (fallback cleanup)
    PORT_PID=$(lsof -t -i:8000 2>/dev/null || netstat -nlp 2>/dev/null | grep :8000 | awk '{print $7}' | cut -d'/' -f1 || true)
    if [ ! -z "$PORT_PID" ]; then
        echo "Port 8000 occupied by PID $PORT_PID. Stopping it..."
        kill -9 "$PORT_PID" 2>/dev/null || true
        sleep 1
    fi
}

# Function to start the server
start_server() {
    # Activate virtual environment
    if [ -f "/www/server/pyporject_evn/backend-tab/bin/activate" ]; then
        echo "Detected aaPanel Python Manager environment. Activating..."
        source /www/server/pyporject_evn/backend-tab/bin/activate
    elif [ -d "venv" ]; then
        source venv/bin/activate
    fi

    echo "Starting FastAPI in background on port 8000..."
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &
    echo $! > uvicorn.pid
    echo "FastAPI started with PID: $(cat uvicorn.pid)"
}

# ----------------- CLI Router -----------------

if [ "$ACTION" = "stop" ]; then
    stop_server
    echo "=== Backend Stopped ==="
    exit 0
elif [ "$ACTION" = "start" ]; then
    start_server
    echo "=== Backend Started ==="
    exit 0
fi

# Default: Git Pull & Install Dependencies & Database Migrations
echo "=== Starting Allia Tap finger (FPA) Backend Update ==="

# 1. Pull latest code from Git (updates the whole repo)
echo "Pulling latest changes from Git..."
git pull

# 2. Activate virtual environment and update packages
echo "Updating Python dependencies..."
if [ -f "/www/server/pyporject_evn/backend-tab/bin/activate" ]; then
    echo "Detected aaPanel Python Manager environment. Activating..."
    source /www/server/pyporject_evn/backend-tab/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
elif [ -d "venv" ]; then
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "Virtual environment 'venv' not found. Creating it..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# 3. Run database migrations
echo "Running database migrations..."
alembic upgrade head

echo "=== Backend Update Completed Successfully ==="
