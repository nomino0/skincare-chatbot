# DigitalOcean Deployment Guide

## 🌊 Overview

This guide covers deploying SkinPredict to DigitalOcean using:
- **App Platform** for API and Frontend
- **Managed PostgreSQL** for database
- **Spaces** for DVC data storage
- **Container Registry** for Docker images

## 📋 Prerequisites

1. DigitalOcean account
2. `doctl` CLI installed
3. Docker installed locally
4. DVC configured with Spaces credentials

## 🚀 Quick Start

### 1. Install doctl CLI

```bash
# Windows (Chocolatey)
choco install doctl

# macOS
brew install doctl

# Authenticate
doctl auth init
```

### 2. Create DigitalOcean Spaces (for DVC)

```bash
# Create a Space for DVC data
doctl spaces create skinpredict-data --region nyc3

# Configure DVC (already done)
dvc remote add -d digitalocean s3://skinpredict-data/dvc-storage
dvc remote modify digitalocean endpointurl https://nyc3.digitaloceanspaces.com
```

### 3. Set Spaces Credentials

Create Spaces access keys in DigitalOcean console:
- Go to **API → Tokens/Keys → Spaces Keys**
- Generate new key
- Save Access Key and Secret Key

```bash
# Configure DVC with credentials
dvc remote modify digitalocean access_key_id YOUR_KEY
dvc remote modify digitalocean secret_access_key YOUR_SECRET

# Push data to Spaces
dvc push
```

### 4. Create Container Registry

```bash
# Create registry
doctl registry create skinpredict-registry

# Login to registry
doctl registry login
```

### 5. Build and Push Docker Images

```bash
# Tag images for DO registry
docker build -t registry.digitalocean.com/skinpredict-registry/api:latest ./api
docker build -t registry.digitalocean.com/skinpredict-registry/frontend:latest -f Dockerfile.frontend .

# Push to registry
docker push registry.digitalocean.com/skinpredict-registry/api:latest
docker push registry.digitalocean.com/skinpredict-registry/frontend:latest
```

### 6. Create App Platform App

Create `do-app-spec.yaml`:

```yaml
name: skinpredict
region: nyc
services:
  - name: api
    image:
      registry_type: DOCR
      repository: api
      tag: latest
    instance_count: 1
    instance_size_slug: basic-xxs
    http_port: 5000
    routes:
      - path: /api
    envs:
      - key: FLASK_ENV
        value: production
      - key: DATABASE_URL
        scope: RUN_TIME
        type: SECRET
      - key: GROQ_API_KEY
        scope: RUN_TIME
        type: SECRET
      - key: GOOGLE_MAPS_API_KEY
        scope: RUN_TIME
        type: SECRET
    health_check:
      http_path: /health

  - name: frontend
    image:
      registry_type: DOCR
      repository: frontend
      tag: latest
    instance_count: 1
    instance_size_slug: basic-xxs
    http_port: 3000
    routes:
      - path: /
    envs:
      - key: NEXT_PUBLIC_API_URL
        value: ${api.PUBLIC_URL}

databases:
  - name: db
    engine: PG
    production: false
    cluster_name: skinpredict-db
    db_name: skinpredict
    db_user: skinpredict
```

Deploy:
```bash
doctl apps create --spec do-app-spec.yaml
```

## 💰 Cost Estimate

| Service | Specification | Monthly Cost |
|---------|---------------|--------------|
| App Platform (API) | Basic XXS (512MB) | $5 |
| App Platform (Frontend) | Basic XXS (512MB) | $5 |
| Managed Database | Basic (1GB) | $15 |
| Spaces | 250GB + Transfer | $5 |
| Container Registry | Free tier | $0 |
| **Total** | | **~$30/month** |

## 🔧 Environment Variables

Set these in DigitalOcean App Platform:

| Variable | Source | Description |
|----------|--------|-------------|
| `DATABASE_URL` | Auto (from managed DB) | PostgreSQL connection |
| `GROQ_API_KEY` | Secret | Groq API key |
| `GOOGLE_MAPS_API_KEY` | Secret | Google Maps key |
| `SECRET_KEY` | Secret | Flask secret |
| `ADMIN_SECRET_KEY` | Secret | Admin operations |

## 📊 Monitoring

DigitalOcean provides built-in monitoring:
- **App Platform Metrics**: CPU, Memory, HTTP metrics
- **Database Metrics**: Connections, queries, storage
- **Alerts**: Set up notifications for issues

## 🔄 CI/CD Integration

The GitHub Actions workflow (`.github/workflows/mlops.yml`) is configured to:
1. Run tests on push
2. Build Docker images
3. Push to DigitalOcean Container Registry
4. Deploy to App Platform

Add these secrets to GitHub:
- `DIGITALOCEAN_ACCESS_TOKEN`
- `DO_REGISTRY_NAME`

## 🔐 Security Checklist

- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS (automatic on App Platform)
- [ ] Set up firewall rules for database
- [ ] Use managed database (encrypted at rest)
- [ ] Enable 2FA on DigitalOcean account

## 📁 DVC Workflow

After deployment, to update data:

```bash
# Local: Add new data
dvc add api/data/raw

# Push to Spaces
dvc push

# Commit pointer to Git
git add api/data/raw.dvc
git commit -m "Update training data"
git push

# On server: Pull latest data
dvc pull
```

## 🆘 Troubleshooting

### DVC push fails
```bash
# Check credentials
dvc remote modify digitalocean access_key_id YOUR_KEY
dvc remote modify digitalocean secret_access_key YOUR_SECRET
```

### App Platform build fails
```bash
# Check logs
doctl apps logs APP_ID --type=build
```

### Database connection issues
```bash
# Get connection string
doctl databases connection DB_ID
```
