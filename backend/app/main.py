from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, scan, report, super_admin, invoice
from app.db.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="10-Finger Fingerprint Scanner API",
    description="Backend API for fingerprint scanning and analysis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(scan.router)
app.include_router(report.router)
app.include_router(super_admin.router)
app.include_router(invoice.router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}
