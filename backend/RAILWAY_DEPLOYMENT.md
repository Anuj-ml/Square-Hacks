# Railway Deployment Guide for Arogya-Swarm Backend

## Prerequisites
1. Railway account (sign up at https://railway.app)
2. GitHub repository connected to Railway
3. PostgreSQL and Redis databases

## Step 1: Create a New Project on Railway

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select your `Square-Hacks` repository
4. Railway will auto-detect the nixpacks configuration

## Step 2: Add Required Services

### Add PostgreSQL Database
1. Click "New" → "Database" → "Add PostgreSQL"
2. Railway will automatically create a database and provide `DATABASE_URL`
3. The variable will be automatically injected into your backend service

### Add Redis Database
1. Click "New" → "Database" → "Add Redis"
2. Railway will automatically provide `REDIS_URL`

## Step 3: Configure Environment Variables

Go to your backend service → Variables tab and add:

### Required Variables
```bash
# AI/LLM
GOOGLE_API_KEY=your_gemini_api_key_here

# External APIs
AIR_QUALITY_API_KEY=your_google_maps_api_key

# Translation (Optional - uses free tier by default)
TRANSLATION_API_PROVIDER=mymemory
TRANSLATION_API_EMAIL=your_email@example.com

# App Configuration
FRONTEND_URL=https://your-frontend-url.vercel.app
LOG_LEVEL=INFO
DEBUG=false
DEMO_MODE=true

# Hospital Configuration
HOSPITAL_NAME=Apollo Metro Hospital
HOSPITAL_CITY=Mumbai
HOSPITAL_BEDS=400

# Feature Flags
ENABLE_VOICE_NARRATION=true
ENABLE_SMS_NOTIFICATIONS=false
ENABLE_TWITTER_MOCK=true
ENABLE_RAG_CHATBOT=true
ENABLE_REAL_SMS=false
ENABLE_REAL_WHATSAPP=false
```

### Optional Variables (if using these services)
```bash
# Twilio (for real SMS/WhatsApp)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_NUMBER=+14155238886

# Razorpay (for payments)
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_secret

# Image Diagnosis
GOOGLE_CLOUD_PROJECT_ID=your_project_id
HUGGINGFACE_API_KEY=your_huggingface_token

# Video Conferencing
DAILY_API_KEY=your_daily_api_key
```

## Step 4: Configure Build Settings

Railway should automatically detect:
- **Build Command**: Uses nixpacks.toml configuration
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}`
- **Python Version**: 3.11 (from nixpacks.toml)

## Step 5: Set Root Directory (Important!)

Since your backend is in a subdirectory:
1. Go to Settings tab
2. Under "Service Settings"
3. Set **Root Directory** to: `backend`
4. Click "Save"

## Step 6: Deploy

1. Railway will automatically deploy when you push to your repository
2. Monitor the deployment logs in the Railway dashboard
3. Once deployed, Railway will provide a public URL like: `https://your-app.railway.app`

## Step 7: Database Migrations

After first deployment, run migrations:
1. Go to your service → "Deploy" tab
2. The database tables will be auto-created on startup via `Base.metadata.create_all()`
3. Alternatively, you can run Alembic migrations manually if needed

## Step 8: Update Frontend CORS

Update your frontend to use the Railway backend URL:
```typescript
const API_URL = 'https://your-backend.railway.app/api/v1';
```

And update `FRONTEND_URL` in Railway environment variables to your frontend URL.

## Health Check Endpoints

- **Root**: `https://your-app.railway.app/`
- **Health**: `https://your-app.railway.app/health`
- **API Docs**: `https://your-app.railway.app/docs`
- **WebSocket**: `wss://your-app.railway.app/ws`

## Monitoring

- **Logs**: Railway dashboard → Deployments tab
- **Metrics**: Railway provides CPU, Memory, and Network metrics
- **Alerts**: Set up alerts for deployment failures

## Cost Optimization

Railway offers:
- **Free tier**: $5 credit/month
- **Hobby Plan**: $5/month + usage
- **Pro Plan**: $20/month + usage

Tips to reduce costs:
1. Use Railway's PostgreSQL and Redis (included in plans)
2. Keep `DEMO_MODE=true` to reduce external API calls
3. Set `ENABLE_REAL_SMS=false` to use mock services
4. Monitor usage in the Railway dashboard

## Troubleshooting

### Deployment Fails
- Check logs in Railway dashboard
- Verify all required environment variables are set
- Ensure `DATABASE_URL` and `REDIS_URL` are properly connected

### Database Connection Issues
- Railway automatically injects `DATABASE_URL` - don't override it
- Check if PostgreSQL service is running
- Review connection logs

### Port Issues
- Railway automatically provides `PORT` environment variable
- The app is configured to use `${PORT:-8000}`

### CORS Issues
- Update `FRONTEND_URL` to match your actual frontend domain
- Check CORS middleware configuration in main.py

## Useful Commands

Connect to Railway CLI:
```bash
npm i -g @railway/cli
railway login
railway link
```

View logs:
```bash
railway logs
```

Run commands in Railway environment:
```bash
railway run python manage.py migrate
```

## Next Steps

1. Set up automatic deployments on push to main branch
2. Configure custom domain (if needed)
3. Set up environment-specific variables (staging/production)
4. Enable monitoring and alerts
5. Configure backup strategy for PostgreSQL

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Project Issues: Check your GitHub repository issues
