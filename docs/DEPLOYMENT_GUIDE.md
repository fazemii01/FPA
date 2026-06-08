# Deployment Guide

## Prerequisites

- AWS account (or your cloud provider)
- Docker and Docker Compose
- kubectl (for Kubernetes)
- Terraform (for infrastructure as code)

## Backend Deployment

### Option 1: Docker on AWS EC2

#### 1. Launch EC2 Instance

```bash
# Create security group
aws ec2 create-security-group \
  --group-name fingerprint-scanner \
  --description "Fingerprint Scanner Security Group"

# Add inbound rules
aws ec2 authorize-security-group-ingress \
  --group-name fingerprint-scanner \
  --protocol tcp --port 80 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-name fingerprint-scanner \
  --protocol tcp --port 443 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-name fingerprint-scanner \
  --protocol tcp --port 5432 --cidr 10.0.0.0/8
```

#### 2. Connect and Deploy

```bash
# SSH into instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Install Docker
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone https://github.com/your-repo/fingerprint-scanner.git
cd fingerprint-scanner/backend

# Create production .env
cat > .env << EOF
DATABASE_URL=postgresql://fpa_user:fpa_password@postgres:5432/fpa_db
SECRET_KEY=$(openssl rand -hex 32)
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=$(openssl rand -hex 16)
MINIO_SECRET_KEY=$(openssl rand -hex 32)
EOF

# Start services
docker-compose up -d
```

### Option 2: AWS RDS + ECS

#### 1. Create RDS Database

```bash
aws rds create-db-instance \
  --db-instance-identifier fingerprint-scanner-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username fpa_user \
  --master-user-password $(openssl rand -hex 16) \
  --allocated-storage 20
```

#### 2. Create ECS Cluster

```bash
# Create cluster
aws ecs create-cluster --cluster-name fingerprint-scanner

# Register task definition
aws ecs register-task-definition \
  --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster fingerprint-scanner \
  --service-name fingerprint-scanner-api \
  --task-definition fingerprint-scanner:1 \
  --desired-count 2
```

### Option 3: Kubernetes

#### 1. Create Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fingerprint-scanner-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fingerprint-scanner-api
  template:
    metadata:
      labels:
        app: fingerprint-scanner-api
    spec:
      containers:
      - name: api
        image: your-registry/fingerprint-scanner-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: secret-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

#### 2. Deploy

```bash
# Create secrets
kubectl create secret generic app-secrets \
  --from-literal=database-url=postgresql://... \
  --from-literal=secret-key=$(openssl rand -hex 32)

# Deploy
kubectl apply -f deployment.yaml

# Expose service
kubectl expose deployment fingerprint-scanner-api \
  --type=LoadBalancer \
  --port=80 \
  --target-port=8000
```

## Mobile App Deployment

### Android Play Store

1. **Build Release APK**
   ```bash
   cd mobile
   flutter build apk --release
   ```

2. **Create Keystore**
   ```bash
   keytool -genkey -v -keystore ~/key.jks \
     -keyalg RSA -keysize 2048 -validity 10000 \
     -alias upload
   ```

3. **Sign APK**
   ```bash
   jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 \
     -keystore ~/key.jks \
     build/app/outputs/flutter-apk/app-release.apk upload
   ```

4. **Upload to Play Store**
   - Go to Google Play Console
   - Create new app
   - Upload signed APK
   - Fill in app details
   - Submit for review

### iOS App Store

1. **Build Release IPA**
   ```bash
   cd mobile
   flutter build ios --release
   ```

2. **Archive in Xcode**
   ```bash
   cd ios
   xcodebuild -workspace Runner.xcworkspace \
     -scheme Runner -configuration Release \
     -archivePath build/Runner.xcarchive archive
   ```

3. **Export IPA**
   - Open Xcode Organizer
   - Select archive
   - Click "Distribute App"
   - Choose "App Store Connect"
   - Follow prompts

4. **Upload to App Store**
   - Go to App Store Connect
   - Create new app
   - Upload IPA
   - Fill in app details
   - Submit for review

## Production Configuration

### Environment Variables

```bash
# Backend
DATABASE_URL=postgresql://user:password@host:5432/db
SECRET_KEY=<strong-random-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

MINIO_ENDPOINT=s3.amazonaws.com
MINIO_ACCESS_KEY=<aws-access-key>
MINIO_SECRET_KEY=<aws-secret-key>
MINIO_BUCKET_NAME=fingerprints
MINIO_SECURE=true
```

### SSL/TLS Certificate

```bash
# Using Let's Encrypt with Certbot
sudo certbot certonly --standalone -d your-domain.com

# Configure Nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
    }
}
```

### Database Backup

```bash
# Automated daily backup
0 2 * * * pg_dump -U fpa_user fpa_db | gzip > /backups/fpa_db_$(date +\%Y\%m\%d).sql.gz
```

### Monitoring

```bash
# Install monitoring tools
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v /path/to/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

docker run -d \
  --name grafana \
  -p 3000:3000 \
  grafana/grafana
```

## Scaling

### Horizontal Scaling

```bash
# Add more API instances
docker-compose up -d --scale backend=3

# Load balance with Nginx
upstream backend {
    server backend:8000;
    server backend:8001;
    server backend:8002;
}
```

### Database Scaling

```bash
# Read replicas
aws rds create-db-instance-read-replica \
  --db-instance-identifier fingerprint-scanner-db-replica \
  --source-db-instance-identifier fingerprint-scanner-db
```

## Monitoring & Logging

### Application Logs

```bash
# View logs
docker-compose logs -f backend

# Send to CloudWatch
docker-compose logs backend | aws logs put-log-events \
  --log-group-name /fingerprint-scanner/backend \
  --log-stream-name production
```

### Performance Monitoring

```bash
# Monitor API response times
curl -w "@curl-format.txt" -o /dev/null -s http://your-api.com/health

# Monitor database
SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
```

## Disaster Recovery

### Backup Strategy

- Daily automated backups
- Weekly full backups
- Monthly archive backups
- Test restore procedures monthly

### Failover

```bash
# Database failover
aws rds failover-db-cluster \
  --db-cluster-identifier fingerprint-scanner-cluster

# Application failover
# Use load balancer to route to healthy instances
```

## Rollback Procedure

```bash
# Rollback to previous version
docker-compose down
git checkout previous-tag
docker-compose up -d

# Database rollback
alembic downgrade -1
```

## Checklist

- [ ] SSL/TLS certificates configured
- [ ] Database backups automated
- [ ] Monitoring and alerting set up
- [ ] Load balancer configured
- [ ] Auto-scaling policies defined
- [ ] Disaster recovery plan tested
- [ ] Security audit completed
- [ ] Performance testing done
- [ ] Documentation updated
- [ ] Team trained on deployment

---

For more details, see individual service documentation.
