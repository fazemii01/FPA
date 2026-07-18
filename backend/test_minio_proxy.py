import sys
from minio import Minio
from minio.error import S3Error

# Test parameters
endpoint = "storage.alliago.id"
access_key = "fazemii"
secret_key = "alexandria20"
secure = True

print(f"Connecting to MinIO via proxy: https://{endpoint}...")

try:
    client = Minio(
        endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=secure
    )
    # Try to list buckets
    buckets = client.list_buckets()
    print("SUCCESS! Successfully connected to MinIO via proxy.")
    print("Available Buckets:")
    for bucket in buckets:
        print(f" - {bucket.name}")
except S3Error as s3_err:
    print(f"\nS3 API Error: {s3_err}")
    print(f"Code: {s3_err.code}")
    print(f"Message: {s3_err.message}")
except Exception as e:
    print(f"\nConnection failed: {e}")
