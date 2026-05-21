# API Testing Guide

Complete guide for testing the Fingerprint Scanner API.

## Prerequisites

- Backend running at http://localhost:8000
- Postman, curl, or HTTPie installed
- Valid user credentials

## Quick Test Flow

### 1. Health Check

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy"
}
```

### 2. Register User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "email": "test@example.com",
  "full_name": "Test User",
  "is_active": true,
  "created_at": "2026-05-17T09:40:48.355Z"
}
```

### 3. Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Save the token:**
```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 4. Create Scan Session

```bash
curl -X POST http://localhost:8000/scans/sessions \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "status": "in_progress",
  "created_at": "2026-05-17T09:40:48.355Z",
  "updated_at": "2026-05-17T09:40:48.355Z",
  "completed_at": null,
  "fingerprints": []
}
```

### 5. Upload Fingerprint

```bash
curl -X POST http://localhost:8000/scans/sessions/1/fingerprints \
  -H "Authorization: Bearer $TOKEN" \
  -F "finger_position=right_thumb" \
  -F "file=@fingerprint.png"
```

**Expected Response:**
```json
{
  "id": 1,
  "scan_session_id": 1,
  "finger_position": "right_thumb",
  "image_path": "fingerprints/1/1/right_thumb_abc123.png",
  "quality_score": 85.5,
  "created_at": "2026-05-17T09:40:48.355Z"
}
```

### 6. List Session Fingerprints

```bash
curl -X GET http://localhost:8000/scans/sessions/1/fingerprints \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
[
  {
    "id": 1,
    "scan_session_id": 1,
    "finger_position": "right_thumb",
    "image_path": "fingerprints/1/1/right_thumb_abc123.png",
    "quality_score": 85.5,
    "created_at": "2026-05-17T09:40:48.355Z"
  }
]
```

### 7. Generate Report

```bash
curl -X POST http://localhost:8000/reports/sessions/1/generate \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "id": 1,
  "scan_session_id": 1,
  "overall_score": 82.3,
  "pdf_path": "reports/1/1/report.pdf",
  "metrics": {
    "total_fingerprints": 10,
    "quality_scores": {
      "right_thumb": 85.5,
      "right_index": 80.2,
      "right_middle": 83.1,
      "right_ring": 81.5,
      "right_pinky": 79.8,
      "left_thumb": 84.2,
      "left_index": 82.7,
      "left_middle": 83.9,
      "left_ring": 80.5,
      "left_pinky": 81.9
    },
    "average_quality": 82.3
  },
  "created_at": "2026-05-17T09:40:48.355Z"
}
```

### 8. Get Report

```bash
curl -X GET http://localhost:8000/reports/sessions/1 \
  -H "Authorization: Bearer $TOKEN"
```

## Complete Test Script

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"
EMAIL="test@example.com"
PASSWORD="password123"

echo "1. Health Check"
curl -s $BASE_URL/health | jq

echo -e "\n2. Register User"
curl -s -X POST $BASE_URL/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\",\"full_name\":\"Test User\"}" | jq

echo -e "\n3. Login"
TOKEN=$(curl -s -X POST $BASE_URL/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" | jq -r '.access_token')

echo "Token: $TOKEN"

echo -e "\n4. Create Scan Session"
SESSION_ID=$(curl -s -X POST $BASE_URL/scans/sessions \
  -H "Authorization: Bearer $TOKEN" | jq -r '.id')

echo "Session ID: $SESSION_ID"

echo -e "\n5. Upload Fingerprints"
for finger in right_thumb right_index right_middle right_ring right_pinky left_thumb left_index left_middle left_ring left_pinky; do
  echo "Uploading $finger..."
  curl -s -X POST $BASE_URL/scans/sessions/$SESSION_ID/fingerprints \
    -H "Authorization: Bearer $TOKEN" \
    -F "finger_position=$finger" \
    -F "file=@test_fingerprint.png" | jq
done

echo -e "\n6. List Fingerprints"
curl -s -X GET $BASE_URL/scans/sessions/$SESSION_ID/fingerprints \
  -H "Authorization: Bearer $TOKEN" | jq

echo -e "\n7. Generate Report"
curl -s -X POST $BASE_URL/reports/sessions/$SESSION_ID/generate \
  -H "Authorization: Bearer $TOKEN" | jq

echo -e "\n8. Get Report"
curl -s -X GET $BASE_URL/reports/sessions/$SESSION_ID \
  -H "Authorization: Bearer $TOKEN" | jq

echo -e "\nTest completed!"
```

## Postman Collection

### Import Collection

1. Open Postman
2. Click "Import"
3. Paste the following JSON:

```json
{
  "info": {
    "name": "Fingerprint Scanner API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Auth",
      "item": [
        {
          "name": "Register",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"test@example.com\",\n  \"password\": \"password123\",\n  \"full_name\": \"Test User\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/auth/register",
              "host": ["{{base_url}}"],
              "path": ["auth", "register"]
            }
          }
        },
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"test@example.com\",\n  \"password\": \"password123\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/auth/login",
              "host": ["{{base_url}}"],
              "path": ["auth", "login"]
            }
          }
        }
      ]
    },
    {
      "name": "Scans",
      "item": [
        {
          "name": "Create Session",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              }
            ],
            "url": {
              "raw": "{{base_url}}/scans/sessions",
              "host": ["{{base_url}}"],
              "path": ["scans", "sessions"]
            }
          }
        },
        {
          "name": "Upload Fingerprint",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              }
            ],
            "body": {
              "mode": "formdata",
              "formdata": [
                {
                  "key": "finger_position",
                  "value": "right_thumb",
                  "type": "text"
                },
                {
                  "key": "file",
                  "type": "file",
                  "src": "/path/to/fingerprint.png"
                }
              ]
            },
            "url": {
              "raw": "{{base_url}}/scans/sessions/{{session_id}}/fingerprints",
              "host": ["{{base_url}}"],
              "path": ["scans", "sessions", "{{session_id}}", "fingerprints"]
            }
          }
        }
      ]
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    },
    {
      "key": "token",
      "value": ""
    },
    {
      "key": "session_id",
      "value": ""
    }
  ]
}
```

## Error Responses

### 401 Unauthorized

```json
{
  "detail": "Invalid authentication credentials"
}
```

### 404 Not Found

```json
{
  "detail": "Session not found"
}
```

### 422 Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Performance Testing

### Load Test with Apache Bench

```bash
# Test login endpoint
ab -n 1000 -c 10 -p login.json -T application/json \
  http://localhost:8000/auth/login

# Test health endpoint
ab -n 10000 -c 100 http://localhost:8000/health
```

### Load Test with wrk

```bash
wrk -t12 -c400 -d30s http://localhost:8000/health
```

## Automated Testing

### Python Script

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Register
response = requests.post(f"{BASE_URL}/auth/register", json={
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
})
print("Register:", response.json())

# Login
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "test@example.com",
    "password": "password123"
})
token = response.json()["access_token"]
print("Token:", token)

# Create session
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(f"{BASE_URL}/scans/sessions", headers=headers)
session_id = response.json()["id"]
print("Session ID:", session_id)

# Upload fingerprint
files = {"file": open("fingerprint.png", "rb")}
data = {"finger_position": "right_thumb"}
response = requests.post(
    f"{BASE_URL}/scans/sessions/{session_id}/fingerprints",
    headers=headers,
    files=files,
    data=data
)
print("Upload:", response.json())
```

## Troubleshooting

### Connection Refused
- Check backend is running: `docker-compose ps`
- Verify port 8000 is not in use: `lsof -i :8000`

### 401 Unauthorized
- Check token is valid
- Verify token is not expired
- Ensure Authorization header format: `Bearer <token>`

### 422 Validation Error
- Check request body format
- Verify all required fields are present
- Ensure data types are correct

---

For more details, visit http://localhost:8000/docs
