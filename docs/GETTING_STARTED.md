# Getting Started Guide

## Prerequisites

- Python 3.11+ (for backend)
- Flutter 3.0+ (for mobile)
- Docker & Docker Compose (recommended)
- Git
- Postman or curl (for API testing)

## 5-Minute Quick Start

### Step 1: Start Backend with Docker

```bash
cd backend
docker-compose up -d
```

Wait for services to be healthy (30-60 seconds):
- PostgreSQL: localhost:5432
- MinIO: localhost:9000
- API: localhost:8000

### Step 2: Test Backend

```bash
# Health check
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs
```

### Step 3: Register & Login

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Step 4: Run Mobile App

```bash
cd mobile
flutter pub get
flutter run
```

## Detailed Setup

### Backend Setup (Local Development)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Environment Variables** (`.env`):
```
DATABASE_URL=postgresql://fpa_user:fpa_password@localhost:5432/fpa_db
SECRET_KEY=your-secret-key-here
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

### Backend Setup (Docker)

```bash
cd backend
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Mobile Setup

```bash
cd mobile

# Install dependencies
flutter pub get

# Configure API endpoint
# Edit lib/config/app_config.dart
# Set baseUrl based on your setup:
# - Android Emulator: http://10.0.2.2:8000
# - iOS Simulator: http://localhost:8000
# - Physical Device: http://YOUR_COMPUTER_IP:8000

# Run on emulator
flutter run

# Run on physical device
flutter run -d <device_id>

# Build APK
flutter build apk --release

# Build iOS
flutter build ios --release
```

## API Testing

### Using Postman

1. Import the API collection (create from Swagger docs)
2. Set base URL: `http://localhost:8000`
3. Create environment variables:
   - `base_url`: http://localhost:8000
   - `token`: (will be set after login)

### Using curl

```bash
# 1. Register
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  | jq -r '.access_token')

# 2. Create scan session
curl -X POST http://localhost:8000/scans/sessions \
  -H "Authorization: Bearer $TOKEN"

# 3. Upload fingerprint
curl -X POST http://localhost:8000/scans/sessions/1/fingerprints \
  -H "Authorization: Bearer $TOKEN" \
  -F "finger_position=right_thumb" \
  -F "file=@fingerprint.png"

# 4. Generate report
curl -X POST http://localhost:8000/reports/sessions/1/generate \
  -H "Authorization: Bearer $TOKEN"
```

## Database Management

### View Database

```bash
# Connect to PostgreSQL
psql -U fpa_user -d fpa_db -h localhost

# List tables
\dt

# View users
SELECT * FROM users;

# View scan sessions
SELECT * FROM scan_sessions;
```

### Create Migration

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "description of changes"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## MinIO Management

### Access MinIO Console

1. Open http://localhost:9001
2. Login with:
   - Username: minioadmin
   - Password: minioadmin

### Upload Test File

```bash
# Using MinIO client
mc alias set minio http://localhost:9000 minioadmin minioadmin
mc cp fingerprint.png minio/fingerprints/test/
```

## Troubleshooting

### Backend Issues

**Port already in use**
```bash
# Find process using port 8000
lsof -i :8000
# Kill process
kill -9 <PID>
```

**Database connection error**
```bash
# Check PostgreSQL is running
docker-compose ps

# Restart PostgreSQL
docker-compose restart postgres
```

**Migration errors**
```bash
# Reset database
alembic downgrade base
alembic upgrade head
```

### Mobile Issues

**API connection failed**
- Check backend is running
- Verify API endpoint in app_config.dart
- Check firewall settings
- For physical device, use computer's IP address

**Camera not working**
- Check permissions in AndroidManifest.xml / Info.plist
- Grant camera permission in device settings
- Test on physical device (emulator may have issues)

**Build errors**
```bash
flutter clean
flutter pub get
flutter run
```

## Development Workflow

### Backend Development

1. Make changes to code
2. Server auto-reloads (with `--reload`)
3. Test with Swagger UI at http://localhost:8000/docs
4. Run tests: `pytest tests/`
5. Check code: `flake8 app/`

### Mobile Development

1. Make changes to code
2. Hot reload: Press `r` in terminal
3. Hot restart: Press `R` in terminal
4. Test on emulator/device
5. Run tests: `flutter test`

## Performance Tips

### Backend
- Use connection pooling for database
- Cache frequently accessed data
- Optimize image processing
- Use CDN for static files

### Mobile
- Lazy load images
- Use image caching
- Implement pagination
- Minimize API calls

## Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Use HTTPS/TLS
- [ ] Enable CORS only for trusted domains
- [ ] Implement rate limiting
- [ ] Add request validation
- [ ] Use environment variables for secrets
- [ ] Enable database encryption
- [ ] Set up monitoring and logging
- [ ] Regular security updates
- [ ] Implement backup strategy

## Deployment Checklist

### Backend
- [ ] Update environment variables
- [ ] Configure production database
- [ ] Set up MinIO for production
- [ ] Enable HTTPS
- [ ] Configure reverse proxy (Nginx)
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Test all endpoints
- [ ] Load testing

### Mobile
- [ ] Update API endpoint
- [ ] Test on multiple devices
- [ ] Optimize app size
- [ ] Test offline functionality
- [ ] Prepare app store listings
- [ ] Set up crash reporting
- [ ] Configure analytics

## Useful Commands

```bash
# Backend
cd backend
python -m venv venv          # Create virtual environment
pip install -r requirements.txt  # Install dependencies
alembic upgrade head         # Run migrations
pytest tests/                # Run tests
flake8 app/                  # Check code style
black app/                   # Format code

# Mobile
cd mobile
flutter pub get              # Install dependencies
flutter run                  # Run app
flutter test                 # Run tests
flutter build apk --release  # Build APK
flutter build ios --release  # Build iOS

# Docker
docker-compose up -d         # Start services
docker-compose down          # Stop services
docker-compose logs -f       # View logs
docker-compose ps            # View status
```

## Next Steps

1. **Explore API**: Visit http://localhost:8000/docs
2. **Test Endpoints**: Use Postman or curl
3. **Run Mobile App**: Test on emulator/device
4. **Review Code**: Check implementation details
5. **Customize**: Modify for your needs
6. **Deploy**: Follow deployment guide

## Support

- API Documentation: http://localhost:8000/docs
- Backend README: `backend/README.md`
- Mobile README: `mobile/README.md`
- Implementation Plan: `IMPLEMENTATION_PLAN.md`

---

**Ready to start?** Run `docker-compose up -d` in the backend directory!
