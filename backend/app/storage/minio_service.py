from minio import Minio
from minio.error import S3Error
from app.core.config import settings
import io
from datetime import timedelta


class MinIOService:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            print(f"Error ensuring bucket exists: {e}")
    
    def upload_fingerprint(self, file_data: bytes, object_name: str) -> str:
        try:
            self.client.put_object(
                self.bucket_name,
                object_name,
                io.BytesIO(file_data),
                length=len(file_data),
                content_type="image/png"
            )
            return object_name
        except S3Error as e:
            raise Exception(f"Error uploading file: {e}")
    
    def get_fingerprint(self, object_name: str) -> bytes:
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            return response.read()
        except S3Error as e:
            raise Exception(f"Error downloading file: {e}")
    
    def delete_fingerprint(self, object_name: str):
        try:
            self.client.remove_object(self.bucket_name, object_name)
        except S3Error as e:
            raise Exception(f"Error deleting file: {e}")
    
    def get_presigned_url(self, object_name: str, expires: int = 3600) -> str:
        try:
            url = self.client.get_presigned_download_url(
                self.bucket_name,
                object_name,
                expires=timedelta(seconds=expires)
            )
            return url
        except S3Error as e:
            raise Exception(f"Error generating presigned URL: {e}")
