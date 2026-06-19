import os
import sys
import subprocess
import shutil

def install_package(package):
    """Auto-install missing dependencies (like minio)."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Ensure minio library is installed
try:
    from minio import Minio
except ImportError:
    print("Installing missing dependency: minio...")
    install_package("minio")
    from minio import Minio

def load_env_vars(env_path):
    """Load S3 credentials from backend's .env file."""
    env_vars = {}
    if not os.path.exists(env_path):
        print(f"Error: Backend .env file not found at {env_path}")
        sys.exit(1)
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, val = line.split('=', 1)
            env_vars[key.strip()] = val.strip()
    return env_vars

def main():
    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    backend_env = os.path.join(project_root, "backend", ".env")
    
    # Try loading from system environment variables first (useful for GitHub Actions)
    endpoint = os.environ.get("MINIO_ENDPOINT")
    access_key = os.environ.get("MINIO_ACCESS_KEY")
    secret_key = os.environ.get("MINIO_SECRET_KEY")
    bucket = os.environ.get("MINIO_BUCKET_NAME")
    secure = os.environ.get("MINIO_SECURE")
    
    if not all([endpoint, access_key, secret_key]):
        print("Credentials not found in environment. Loading from backend .env...")
        env = load_env_vars(backend_env)
        endpoint = endpoint or env.get("MINIO_ENDPOINT")
        access_key = access_key or env.get("MINIO_ACCESS_KEY")
        secret_key = secret_key or env.get("MINIO_SECRET_KEY")
        bucket = bucket or env.get("MINIO_BUCKET_NAME", "fingerprints")
        secure = secure or env.get("MINIO_SECURE", "false")
    else:
        bucket = bucket or "fingerprints"
        secure = secure or "false"
        
    secure = secure.lower() == "true"
    
    if not all([endpoint, access_key, secret_key]):
        print("Error: Missing MinIO credentials in backend/.env file.")
        sys.exit(1)
    
    print(f"MinIO Endpoint: {endpoint}")
    print(f"Target Bucket:  {bucket}")
    print(f"Secure (SSL):   {secure}")
    
    # 1. Compile Flutter App
    print("\n--- Compiling Flutter App in Release Mode ---")
    os.chdir(script_dir)
    
    # Windows-safe execution of flutter build apk
    flutter_cmd = "flutter.bat" if os.name == 'nt' else "flutter"
    try:
        subprocess.run([flutter_cmd, "build", "apk", "--release"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: Flutter compilation failed: {e}")
        sys.exit(1)
    
    apk_path = os.path.join(script_dir, "build", "app", "outputs", "flutter-apk", "app-release.apk")
    if not os.path.exists(apk_path):
        print(f"Error: Compiled APK not found at {apk_path}")
        sys.exit(1)
        
    print(f"APK Compiled successfully at: {apk_path}")
    
    # 2. Upload to MinIO
    print("\n--- Connecting and Uploading to MinIO ---")
    try:
        client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
        
        # Ensure the bucket exists
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
            print(f"Created new bucket: {bucket}")
            
        object_name = "releases/fpa-latest.apk"
        
        print(f"Uploading {apk_path} to S3://{bucket}/{object_name}...")
        client.fput_object(
            bucket_name=bucket,
            object_name=object_name,
            file_path=apk_path,
            content_type="application/vnd.android.package-archive"
        )
        print("Upload successful!")
        print(f"Available internally inside bucket folder as '{object_name}'")
        
    except Exception as e:
        print(f"Error uploading to MinIO: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
