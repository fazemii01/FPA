from fastapi import APIRouter
from app.storage.minio_service import MinIOService
from app.core.config import settings

router = APIRouter(prefix="/app", tags=["App Info"])

# This constant will be updated whenever a new release is pushed
LATEST_VERSION = "1.0.1"

@router.get("/version")
def get_app_version():
    """Returns the latest FPA mobile app version and a dynamic 24h presigned URL to download it."""
    minio = MinIOService()
    
    # Generate a secure presigned URL valid for 24 hours (86400 seconds)
    apk_download_url = minio.get_presigned_url(
        "releases/fpa-latest.apk", 
        expires=86400,
        bucket_name=settings.MINIO_RELEASE_BUCKET_NAME
    )
    
    return {
        "latest_version": LATEST_VERSION,
        "apk_url": apk_download_url,
        "ios_url": "https://tab.jaribakat.com/download",  # Placeholder redirection page for iOS
        "force_update": True
    }
