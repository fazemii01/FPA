from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://fpa_user:fpa_password@localhost:5432/fpa_db"
    SECRET_KEY: str = "dev_secret_key_placeholder"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 180
    
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "fingerprints"
    MINIO_RELEASE_BUCKET_NAME: str = "release"
    MINIO_SECURE: bool = False
    
    class Config:
        env_file = ".env"


settings = Settings()
