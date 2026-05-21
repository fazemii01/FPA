# 10-Finger Fingerprint Scanner - Backend API

FastAPI backend for the 10-finger fingerprint scanning mobile application.

## Features

- User authentication (JWT)
- Scan session management
- Fingerprint image upload and storage (MinIO)
- Image quality analysis
- Report generation (PDF)
- PostgreSQL database
- RESTful API

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy
- **Storage**: MinIO (S3-compatible)
- **Image Processing**: OpenCV, Pillow
- **PDF Generation**: ReportLab
- **Authentication**: JWT (python-jose)

## Setup

### Prerequisites

- Python 3.11+
- Docker & Docker Compose

### Installation

1. Clone the repository
2. Copy environment file:
   ```bash
   cp .env.example .env
   ```
3. Update `.env` with your configuration

### Running with Docker Compose

```bash
docker-compose up -d
```

This will start:
- PostgreSQL (port 5432)
- MinIO (port 9000, console 9001)
- Backend API (port 8000)

### Running Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run migrations:
   ```bash
   alembic upgrade head
   ```

3. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token

### Scan Sessions
- `POST /scans/sessions` - Create new scan session
- `GET /scans/sessions` - List user's scan sessions
- `GET /scans/sessions/{id}` - Get session details

### Fingerprints
- `POST /scans/sessions/{id}/fingerprints` - Upload fingerprint
- `GET /scans/sessions/{id}/fingerprints` - List session fingerprints

## Project Structure

```
backend/
├── app/
│   ├── core/           # Config, security
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── routers/        # API endpoints
│   ├── repositories/   # Database access
│   ├── services/       # Business logic
│   ├── storage/        # MinIO service
│   ├── processing/     # Image processing
│   ├── report_engine/  # PDF generation
│   ├── middleware/     # Auth middleware
│   └── main.py         # FastAPI app
├── alembic/            # Database migrations
├── tests/              # Test suite
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Development

### Running Tests

```bash
pytest
```

### Creating Migrations

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## License

Proprietary
