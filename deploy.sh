#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "=== Starting Allia Tap finger (FPA) Deployment ==="

# 1. Pull latest code from Git
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

# 4. Gracefully restart Gunicorn backend
echo "Restarting Gunicorn backend..."
if [ -f "gunicorn.pid" ]; then
    PID=$(cat gunicorn.pid)
    if kill -0 "$PID" 2>/dev/null; then
        kill -HUP "$PID"
        echo "Sent HUP signal to Gunicorn (PID: $PID) for graceful reload."
    else
        echo "Gunicorn PID $PID is not running."
    fi
else
    echo "No gunicorn.pid found. If you are using aaPanel Python Manager, please restart the project from the aaPanel GUI."
fi

# 5. Build frontend (if dashboard/ folder exists)
if [ -d "dashboard" ]; then
    echo "Updating Frontend (Next.js)..."
    cd dashboard
    npm install
    npm run build
    # Restart PM2 process
    if command -v pm2 &> /dev/null; then
        pm2 restart fpa-frontend || pm2 restart all || echo "PM2 not found or project not registered in PM2."
    fi
    cd ..
fi

echo "=== Deployment Completed Successfully ==="
