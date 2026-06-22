import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db
from app.models.user import User, UserRole
from app.models.lembaga import Lembaga
from app.models.invoice import Invoice

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_invoices.db"
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
    
    # Pre-seed a test user and a test Lembaga
    db = TestingSessionLocal()
    
    # Seed Lembaga
    lem = Lembaga(name="Lembaga Test", credits=10)
    db.add(lem)
    db.commit()
    db.refresh(lem)
    
    yield TestClient(app)
    
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_public_invoice_workflow(client):
    # 1. Create a super admin user in database manually for authentication
    db = TestingSessionLocal()
    # Hash of "admin123" using passlib/bcrypt
    from app.core.security import get_password_hash
    hashed = get_password_hash("admin123")
    
    user = User(
        email="superadmin@example.com",
        hashed_password=hashed,
        full_name="Super Admin",
        role=UserRole.SUPER_ADMIN,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 2. Login to get token
    login_res = client.post(
        "/auth/login",
        json={"email": "superadmin@example.com", "password": "admin123"}
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    
    # 3. Create Invoice via Super Admin API
    lem_id = db.query(Lembaga).filter(Lembaga.name == "Lembaga Test").first().id
    create_res = client.post(
        "/invoices",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "lembaga_id": lem_id,
            "client_name": "Klien Budi",
            "description": "Top up Kuota Kelas Utama",
            "credits": 10,
            "discount": 50000
        }
    )
    assert create_res.status_code == 200
    invoice_data = create_res.json()
    assert invoice_data["client_name"] == "Klien Budi"
    assert invoice_data["credits"] == 10
    # 10 * 125,000 - 50,000 = 1,200,000
    assert invoice_data["total_amount"] == 1200000
    assert invoice_data["status"] == "pending"
    assert "uuid" in invoice_data
    assert "code" in invoice_data
    invoice_uuid = invoice_data["uuid"]

    # 4. Access invoice detail publicly without token
    public_res = client.get(f"/invoices/public/{invoice_uuid}")
    assert public_res.status_code == 200
    assert public_res.json()["client_name"] == "Klien Budi"

    # 5. Upload mock payment proof publicly
    import io
    file_payload = {"file": ("test_receipt.png", io.BytesIO(b"dummy image data"), "image/png")}
    upload_res = client.post(
        f"/invoices/public/{invoice_uuid}/upload-proof",
        files=file_payload
    )
    assert upload_res.status_code == 200
    uploaded_invoice = upload_res.json()
    assert uploaded_invoice["status"] == "waiting_verification"
    assert "receipts/" in uploaded_invoice["payment_proof_path"]

    # 5b. Verify proxy endpoint works
    proof_url = uploaded_invoice["payment_proof_url"]
    from urllib.parse import urlparse
    parsed = urlparse(proof_url)
    proxy_res = client.get(parsed.path)
    assert proxy_res.status_code == 200
    assert proxy_res.content == b"dummy image data"
    assert proxy_res.headers["content-type"] == "image/png"


    # 6. List invoices as admin to check wait verification list
    list_res = client.get(
        "/invoices",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert list_res.status_code == 200
    invoices_list = list_res.json()
    assert any(inv["uuid"] == invoice_uuid for inv in invoices_list)

    # 7. Approve payment as Super Admin
    invoice_id = uploaded_invoice["id"]
    approve_res = client.post(
        f"/invoices/{invoice_id}/approve",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "success"

    # 8. Check that institution credits have been added successfully
    lem_after = db.query(Lembaga).filter(Lembaga.id == lem_id).first()
    # 10 original + 10 added = 20
    assert lem_after.credits == 20

    # 9. Clean up
    db.close()


def test_partner_invoice_pricing(client):
    db = TestingSessionLocal()
    from app.core.security import get_password_hash
    hashed = get_password_hash("admin123")
    
    # 1. Create super admin
    user = User(
        email="superadmin2@example.com",
        hashed_password=hashed,
        full_name="Super Admin 2",
        role=UserRole.SUPER_ADMIN,
        is_active=True
    )
    db.add(user)
    
    # 2. Seed Partner Lembaga
    lem = Lembaga(name="Lembaga Partner Test", credits=5, type="partner")
    db.add(lem)
    db.commit()
    db.refresh(lem)
    db.refresh(user)

    # 3. Login to get token
    login_res = client.post(
        "/auth/login",
        json={"email": "superadmin2@example.com", "password": "admin123"}
    )
    token = login_res.json()["access_token"]
    
    # 4. Create Invoice for Partner
    create_res = client.post(
        "/invoices",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "lembaga_id": lem.id,
            "client_name": "Klien Partner",
            "description": "Top up Partner",
            "credits": 10,
            "discount": 10000
        }
    )
    assert create_res.status_code == 200
    invoice_data = create_res.json()
    # 10 * 95,000 - 10,000 = 940,000
    assert invoice_data["total_amount"] == 940000
    db.close()
