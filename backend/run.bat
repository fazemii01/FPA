@echo off
echo Starting 10-Finger Fingerprint Scanner Backend...
echo.

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo Running database migrations...
alembic upgrade head

echo.
echo Starting FastAPI server...
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
