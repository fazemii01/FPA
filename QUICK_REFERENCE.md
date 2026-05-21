# ⚡ Quick Reference Card

## 🚀 Start Backend (30 seconds)

```bash
cd backend
docker-compose up -d
```

**Services:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- MinIO: http://localhost:9001
- Database: localhost:5432

## 📱 Start Mobile App (1 minute)

```bash
cd mobile
flutter pub get
flutter run
```

## 🔑 Default Credentials

**MinIO Console:**
- Username: `minioadmin`
- Password: `minioadmin`

**Database:**
- User: `fpa_user`
- Password: `fpa_password`
- Database: `fpa_db`

## 📚 Key Files

| File | Purpose |
|------|---------|
| `backend/docker-compose.yml` | Start all services |
| `backend/app/main.py` | FastAPI app |
| `mobile/lib/main.dart` | Flutter app |
| `backend/requirements.txt` | Python dependencies |
| `mobile/pubspec.yaml` | Flutter dependencies |

## 🔗 Important URLs

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| MinIO Console | http://localhost:9001 |
| Health Check | http://localhost:8000/health |

## 📋 API Endpoints

### Auth
```
POST /auth/register
POST /auth/login
```

### Scans
```
POST /scans/sessions
GET /scans/sessions
GET /scans/sessions/{id}
POST /scans/sessions/{id}/fingerprints
GET /scans/sessions/{id}/fingerprints
```

### Reports
```
POST /reports/sessions/{id}/generate
GET /reports/sessions/{id}
```

## 🧪 Quick Test

```bash
# Health check
curl http://localhost:8000/health

# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","full_name":"Test"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

## 🛠️ Common Commands

### Backend
```bash
cd backend
docker-compose up -d          # Start services
docker-compose down           # Stop services
docker-compose logs -f        # View logs
pytest tests/                 # Run tests
alembic upgrade head          # Run migrations
```

### Mobile
```bash
cd mobile
flutter pub get               # Install dependencies
flutter run                   # Run app
flutter test                  # Run tests
flutter build apk --release   # Build APK
```

## 📁 Project Structure

```
FPA/
├── backend/          # FastAPI backend
│   ├── app/         # Application code
│   ├── alembic/     # Database migrations
│   ├── tests/       # Test suite
│   └── docker-compose.yml
├── mobile/          # Flutter app
│   └── lib/         # Application code
└── docs/            # Documentation
```

## 🔐 Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://fpa_user:fpa_password@localhost:5432/fpa_db
SECRET_KEY=your-secret-key
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

### Mobile (app_config.dart)
```dart
static const String baseUrl = 'http://10.0.2.2:8000'; // Android
// or
static const String baseUrl = 'http://localhost:8000'; // iOS
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port in use | `lsof -i :8000` then `kill -9 <PID>` |
| DB connection error | Check `docker-compose ps` |
| API not responding | Verify backend is running |
| Mobile can't connect | Update API endpoint in config |
| Camera not working | Check permissions in manifest |

## 📖 Documentation

- **Getting Started**: GETTING_STARTED.md
- **API Testing**: API_TESTING_GUIDE.md
- **Deployment**: DEPLOYMENT_GUIDE.md
- **Architecture**: IMPLEMENTATION_PLAN.md
- **Backend**: backend/README.md
- **Mobile**: mobile/README.md

## 🎯 User Flow

1. Register/Login
2. Create scan session
3. Capture 10 fingerprints
4. Generate report
5. View results

## 📊 Tech Stack

**Backend**: FastAPI, PostgreSQL, MinIO, OpenCV
**Mobile**: Flutter, Provider, Dio, Camera
**Infrastructure**: Docker, Alembic, GitHub Actions

## ✅ Verification

```bash
# Backend
curl http://localhost:8000/health

# Mobile
flutter run

# API Docs
open http://localhost:8000/docs
```

## 🚀 Deployment

```bash
# Docker
cd backend && docker-compose up -d

# Mobile
flutter build apk --release
flutter build ios --release
```

## 📞 Quick Help

- API Docs: http://localhost:8000/docs
- Issues: Check GETTING_STARTED.md
- Setup: See GETTING_STARTED.md
- Deploy: See DEPLOYMENT_GUIDE.md

---

**Everything ready? Start with: `cd backend && docker-compose up -d`**
