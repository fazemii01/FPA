import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == "admin"
    assert "id" in data


def test_login_user(client):
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_create_scan_session(client):
    register_response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    login_response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    token = login_response.json()["access_token"]
    
    response = client.post(
        "/scans/sessions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "participant_name": "Test Participant",
            "participant_age": 12,
            "participant_gender": "male"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["participant_name"] == "Test Participant"
    assert data["status"] == "registered"


def test_staff_history_visibility_restriction(client):
    # 1. Register first user (automatically becomes ADMIN because it's the first user)
    client.post(
        "/auth/register",
        json={
            "email": "admin@example.com",
            "password": "adminpassword123",
            "full_name": "Admin User"
        }
    )

    # 2. Login admin to get token
    login_resp = client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "adminpassword123"}
    )
    admin_token = login_resp.json()["access_token"]

    # 3. Register Staff 1 under the admin
    client.post(
        "/auth/register",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": "staff1@example.com",
            "password": "staff1password123",
            "full_name": "Staff One",
            "role": "staff"
        }
    )

    # 4. Register Staff 2 under the admin
    client.post(
        "/auth/register",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": "staff2@example.com",
            "password": "staff2password123",
            "full_name": "Staff Two",
            "role": "staff"
        }
    )

    # 5. Login Staff 1 and Staff 2
    login1 = client.post("/auth/login", json={"email": "staff1@example.com", "password": "staff1password123"})
    staff1_token = login1.json()["access_token"]

    login2 = client.post("/auth/login", json={"email": "staff2@example.com", "password": "staff2password123"})
    staff2_token = login2.json()["access_token"]

    # 6. Create session 1 as Staff 1
    resp1 = client.post(
        "/scans/sessions",
        headers={"Authorization": f"Bearer {staff1_token}"},
        json={"participant_name": "Participant One", "participant_age": 10}
    )
    session1_id = resp1.json()["id"]

    # 7. Create session 2 as Staff 2
    resp2 = client.post(
        "/scans/sessions",
        headers={"Authorization": f"Bearer {staff2_token}"},
        json={"participant_name": "Participant Two", "participant_age": 20}
    )
    session2_id = resp2.json()["id"]

    # 8. Staff 1 lists sessions (should only see session 1)
    list1 = client.get("/scans/sessions", headers={"Authorization": f"Bearer {staff1_token}"})
    assert list1.status_code == 200
    ids1 = [s["id"] for s in list1.json()]
    assert session1_id in ids1
    assert session2_id not in ids1

    # 9. Staff 2 lists sessions (should only see session 2)
    list2 = client.get("/scans/sessions", headers={"Authorization": f"Bearer {staff2_token}"})
    assert list2.status_code == 200
    ids2 = [s["id"] for s in list2.json()]
    assert session2_id in ids2
    assert session1_id not in ids2

    # 10. Staff 1 attempts to get session 2 directly (should get 404)
    get2_by_staff1 = client.get(f"/scans/sessions/{session2_id}", headers={"Authorization": f"Bearer {staff1_token}"})
    assert get2_by_staff1.status_code == 404

    # 11. Admin lists sessions (should see both sessions as they belong to the same institution)
    list_admin = client.get("/scans/sessions", headers={"Authorization": f"Bearer {admin_token}"})
    assert list_admin.status_code == 200
    ids_admin = [s["id"] for s in list_admin.json()]
    assert session1_id in ids_admin
    assert session2_id in ids_admin
