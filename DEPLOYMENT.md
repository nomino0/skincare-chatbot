# Pre-Deployment Checklist

## ✅ Completed Items

### 1. MLOps Infrastructure
- [x] DVC for data versioning
- [x] MLflow for experiment tracking
- [x] Docker containerization (training + inference)
- [x] GitHub Actions CI/CD pipeline
- [x] SQLAlchemy database models
- [x] LangGraph agentic AI

### 2. Backend API (Flask)
- [x] `/api/analyze` - Skin analysis
- [x] `/api/chat` - AI assistant
- [x] `/api/history` - User scan history
- [x] `/api/admin/*` - Admin portal
- [x] Firebase authentication middleware
- [x] CORS configuration

### 3. Frontend
- [x] Next.js application
- [x] Firebase auth integration
- [x] API service with auth interceptor
- [x] Admin portal UI
- [x] Scan history dashboard

### 4. Documentation
- [x] README with setup instructions
- [x] API documentation
- [x] MLOps compliance checklist
- [x] Kaggle integration guide
- [x] Walkthrough documentation

## 🔄 Pre-Deployment Tasks

### Environment Setup
```bash
# 1. Set environment variables
export GROQ_API_KEY="your_groq_api_key"
export FIREBASE_ADMIN_CREDENTIALS="path/to/firebase-credentials.json"
export DATABASE_URL="postgresql://user:pass@host:5432/skinpredict"  # or sqlite:///./skinpredict.db
export GOOGLE_MAPS_API_KEY="your_maps_key"  # optional

# 2. Activate venv
.\api\venv\Scripts\activate  # Windows
source api/venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r api/requirements.txt
npm install  # Frontend
```

### Testing
```bash
# 1. Test Phase 2 backend
python api/test_phase2.py

# 2. Start MLflow
docker-compose up mlflow -d

# 3. Start backend
python api/server.py

# 4. Test complete app (in new terminal)
python test_app.py

# 5. Start frontend (in new terminal)
npm run dev

# 6. Manual testing
# - Visit http://localhost:3000
# - Test login/signup
# - Test skin analysis
# - Test chat
# - Test admin portal at /admin
```

### Database Migration
```bash
# Initialize database
python -c "from api.app.database import init_db; init_db()"

# Verify tables created
python -c "from api.app.database import SessionLocal; from api.app.models.sql_models import User, Scan; db = SessionLocal(); print(f'Users: {db.query(User).count()}, Scans: {db.query(Scan).count()}')"
```

## 🚀 Deployment Steps

### Option 1: DigitalOcean (Recommended)
```bash
# 1. Create Droplet
# - Ubuntu 22.04
# - 4GB RAM minimum
# - Docker pre-installed

# 2. SSH into droplet
ssh root@your-droplet-ip

# 3. Clone repository
git clone https://github.com/your-username/SkinPredict.git
cd SkinPredict

# 4. Set environment variables
nano .env
# Add all required variables

# 5. Pull DVC data
dvc pull

# 6. Start services
docker-compose up -d

# 7. Setup domain (optional)
# - Point domain to droplet IP
# - Configure nginx reverse proxy
# - Setup SSL with Let's Encrypt
```

### Option 2: Docker Compose (Local/Server)
```bash
# 1. Update docker-compose.yml with production settings
# 2. Build images
docker-compose build

# 3. Start all services
docker-compose up -d

# 4. Check logs
docker-compose logs -f api
```

### Option 3: Kubernetes (Advanced)
```bash
# See k8s/ directory for manifests
kubectl apply -f k8s/
```

## 📊 Monitoring Setup

### MLflow
- URL: http://your-domain:5001
- Track experiments
- Compare models
- Register best models

### Application Logs
```bash
# View logs
docker-compose logs -f api

# Or if running locally
tail -f logs/skinpredict.log
```

### Database Backup
```bash
# PostgreSQL
pg_dump skinpredict > backup.sql

# SQLite
cp skinpredict.db skinpredict_backup.db
```

## 🔒 Security Checklist

- [ ] Change default passwords
- [ ] Set strong SECRET_KEY for Flask
- [ ] Enable HTTPS (SSL certificate)
- [ ] Configure firewall rules
- [ ] Set up rate limiting
- [ ] Enable CORS only for trusted domains
- [ ] Rotate API keys regularly
- [ ] Set up database backups
- [ ] Enable logging and monitoring
- [ ] Review admin access controls

## 📈 Post-Deployment

### Week 1
- [ ] Monitor error rates
- [ ] Check API response times
- [ ] Verify MLflow tracking
- [ ] Test all user flows
- [ ] Collect initial feedback

### Week 2
- [ ] Analyze user behavior
- [ ] Check data drift
- [ ] Review model performance
- [ ] Optimize slow endpoints
- [ ] Update documentation

### Ongoing
- [ ] Weekly model retraining
- [ ] Monthly security updates
- [ ] Quarterly feature releases
- [ ] Continuous monitoring

## 🎯 Success Metrics

### Technical
- API uptime > 99%
- Response time < 2s
- Error rate < 1%
- Model accuracy > 85%

### Business
- User registrations
- Scans per day
- Chat interactions
- Admin labels submitted

## 🐛 Troubleshooting

### Common Issues

**1. Database Connection Error**
```bash
# Check DATABASE_URL
echo $DATABASE_URL

# Test connection
python -c "from api.app.database import engine; print(engine.connect())"
```

**2. Firebase Auth Error**
```bash
# Verify credentials file
cat $FIREBASE_ADMIN_CREDENTIALS

# Test Firebase
python -c "import firebase_admin; firebase_admin.initialize_app()"
```

**3. MLflow Not Accessible**
```bash
# Check if running
docker-compose ps mlflow

# Restart
docker-compose restart mlflow
```

**4. CORS Errors**
```bash
# Update CORS_ORIGINS in api/app/config.py
# Add your frontend URL
```

## 📝 Final Notes

- **Backup before deployment**: Always backup data and code
- **Test in staging first**: Use docker-compose for staging environment
- **Monitor closely**: Watch logs for first 24 hours
- **Have rollback plan**: Keep previous version ready
- **Document changes**: Update README with deployment info

## 🎉 Ready to Deploy!

Once all checklist items are complete:
1. Run final tests
2. Create deployment tag: `git tag v1.0.0`
3. Push to production
4. Monitor and celebrate! 🚀
