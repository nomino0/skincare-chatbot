# Quick Start Guide

## Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose

## 1. Backend Setup

### Activate Virtual Environment
```bash
# Windows
.\api\venv\Scripts\activate

# Linux/Mac
source api/venv/bin/activate
```

### Install Dependencies
```bash
pip install -r api/requirements.txt
```

### Set Environment Variables
```bash
# Create .env file in api/ directory
GROQ_API_KEY=your_groq_api_key
FIREBASE_ADMIN_CREDENTIALS=path/to/firebase-credentials.json
DATABASE_URL=sqlite:///./skinpredict.db
GOOGLE_MAPS_API_KEY=your_maps_key  # optional
```

### Initialize Database
```bash
python -c "from api.app.database import init_db; init_db()"
```

### Start MLflow (Optional but Recommended)
```bash
docker-compose up mlflow -d
# Access at http://localhost:5001
```

### Start Backend Server
```bash
python api/server.py
# API running at http://localhost:5000
```

## 2. Frontend Setup

### Install Dependencies
```bash
npm install
```

### Start Development Server
```bash
npm run dev
# Frontend at http://localhost:3000
```

## 3. Test the Application

### API Health Check
```bash
curl http://localhost:5000/health
```

### Run Test Suite
```bash
python test_app.py
```

### Manual Testing
1. Open http://localhost:3000
2. Sign up / Log in
3. Upload a face image
4. Get skin analysis
5. Chat with AI assistant
6. View history
7. Access admin portal at /admin

## 4. Training the Model

### With Transfer Learning (Recommended)
```bash
python api/train.py
```

### Using DVC Pipeline
```bash
dvc repro
```

### Monitor in MLflow
```bash
# Open browser
http://localhost:5001
```

## 5. Kaggle Integration

### Download Datasets
```bash
# Already configured with your credentials
kaggle datasets download -d mahmoudima/skin-types-dataset
unzip skin-types-dataset.zip -d api/data/
```

### Train on Kaggle
1. Upload `api/train.py` to Kaggle Notebook
2. Enable GPU
3. Run training
4. Download model

## 6. Deployment

### Using Docker Compose
```bash
docker-compose up -d
```

### To DigitalOcean
```bash
# See DEPLOYMENT.md for detailed steps
```

## Common Issues

### "Module not found" errors
```bash
# Reinstall dependencies
pip install -r api/requirements.txt
```

### Database errors
```bash
# Reinitialize database
python -c "from api.app.database import init_db; init_db()"
```

### MLflow not accessible
```bash
# Restart MLflow
docker-compose restart mlflow
```

## Quick Commands

```bash
# Start everything
docker-compose up -d
npm run dev

# Stop everything
docker-compose down
```

## Support
- Documentation: See README.md
- MLOps Compliance: See MLOPS_COMPLIANCE.md
- Deployment: See DEPLOYMENT.md
- Kaggle: See KAGGLE_INTEGRATION.md
