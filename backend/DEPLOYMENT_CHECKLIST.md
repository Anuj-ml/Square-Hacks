# Railway Deployment Checklist

## ✅ Pre-Deployment Setup

### Files Created/Updated
- [x] `Procfile` - Railway web process definition
- [x] `railway.json` - Railway deployment configuration
- [x] `nixpacks.toml` - Build configuration (already existed)
- [x] `.dockerignore` - Files to exclude from build
- [x] `RAILWAY_DEPLOYMENT.md` - Complete deployment guide
- [x] `core/config.py` - Updated for Railway environment variables
- [x] `main.py` - Updated CORS for production

### Required Files (Already Present)
- [x] `requirements.txt` - Python dependencies
- [x] `main.py` - FastAPI application entry point
- [x] `.env.example` - Environment variable template

## 🚀 Railway Deployment Steps

### 1. Create Railway Project
- [ ] Go to https://railway.app/new
- [ ] Click "Deploy from GitHub repo"
- [ ] Select your repository
- [ ] Set **Root Directory** to: `backend`

### 2. Add Databases
- [ ] Add PostgreSQL database (click "New" → "Database" → "Add PostgreSQL")
- [ ] Add Redis database (click "New" → "Database" → "Add Redis")
- [ ] Verify `DATABASE_URL` and `REDIS_URL` are automatically set

### 3. Configure Environment Variables

Copy these to Railway Variables tab:

#### Essential Variables ⚠️
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
AIR_QUALITY_API_KEY=your_google_maps_api_key
FRONTEND_URL=https://your-frontend-url.vercel.app
```

#### App Configuration
```bash
LOG_LEVEL=INFO
DEBUG=false
DEMO_MODE=true
HOSPITAL_NAME=Apollo Metro Hospital
HOSPITAL_CITY=Mumbai
HOSPITAL_BEDS=400
```

#### Feature Flags
```bash
ENABLE_VOICE_NARRATION=true
ENABLE_SMS_NOTIFICATIONS=false
ENABLE_TWITTER_MOCK=true
ENABLE_RAG_CHATBOT=true
ENABLE_REAL_SMS=false
ENABLE_REAL_WHATSAPP=false
```

#### Translation API (Free Tier)
```bash
TRANSLATION_API_PROVIDER=mymemory
TRANSLATION_API_EMAIL=your_email@example.com
```

### 4. Deploy
- [ ] Push code to GitHub (Railway auto-deploys)
- [ ] Monitor deployment logs in Railway dashboard
- [ ] Wait for build to complete (~3-5 minutes)

### 5. Verify Deployment
- [ ] Check health endpoint: `https://your-app.railway.app/health`
- [ ] Check API docs: `https://your-app.railway.app/docs`
- [ ] Test WebSocket: `wss://your-app.railway.app/ws`
- [ ] Verify database connection in logs

### 6. Update Frontend
- [ ] Update frontend API_URL to Railway backend URL
- [ ] Update `FRONTEND_URL` in Railway to match frontend domain
- [ ] Test CORS is working properly

## 🔍 Post-Deployment Verification

### API Endpoints to Test
```bash
# Health check
curl https://your-app.railway.app/health

# Root endpoint
curl https://your-app.railway.app/

# API docs (in browser)
https://your-app.railway.app/docs
```

### Database Verification
- [ ] Check Railway logs for "Database tables created successfully"
- [ ] Verify no database connection errors
- [ ] Test a few API endpoints that use database

### Common Issues & Solutions

#### Issue: Build fails with "No module named 'X'"
**Solution**: Check `requirements.txt` includes the module

#### Issue: Database connection errors
**Solution**: Verify PostgreSQL service is running and `DATABASE_URL` is set

#### Issue: CORS errors from frontend
**Solution**: Update `FRONTEND_URL` environment variable in Railway

#### Issue: Port binding errors
**Solution**: App is configured to use Railway's `PORT` variable automatically

## 📊 Monitoring

### Railway Dashboard
- [ ] Set up deployment notifications
- [ ] Monitor resource usage (CPU, Memory, Network)
- [ ] Check logs regularly for errors

### Cost Monitoring
- [ ] Check Railway usage in billing section
- [ ] Keep `DEMO_MODE=true` to reduce API costs
- [ ] Monitor external API usage (Google Maps, Gemini)

## 🔐 Security Checklist

- [ ] Never commit `.env` file to repository
- [ ] All API keys stored in Railway environment variables
- [ ] `DEBUG=false` in production
- [ ] CORS configured properly (not `allow_origins=["*"]` unless needed)
- [ ] Database credentials managed by Railway

## 📝 Optional Enhancements

### Custom Domain
- [ ] Add custom domain in Railway settings
- [ ] Update DNS records
- [ ] Update `FRONTEND_URL` to use custom domain

### CI/CD
- [ ] Set up GitHub Actions for automated testing
- [ ] Configure staging environment
- [ ] Set up deployment previews for PRs

### Monitoring & Logging
- [ ] Integrate with Sentry for error tracking
- [ ] Set up log aggregation (if needed)
- [ ] Configure uptime monitoring

## 🆘 Need Help?

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **Deployment Guide**: See `RAILWAY_DEPLOYMENT.md` for detailed instructions
- **Environment Variables**: See `.env.example` for all available options

## ✨ Deployment Complete!

Once all checkboxes are complete, your backend should be:
- ✅ Running on Railway
- ✅ Connected to PostgreSQL and Redis
- ✅ Accessible via HTTPS
- ✅ WebSocket enabled
- ✅ API documentation available at `/docs`

**Backend URL**: `https://your-app.railway.app`
**API Docs**: `https://your-app.railway.app/docs`
**WebSocket**: `wss://your-app.railway.app/ws`
