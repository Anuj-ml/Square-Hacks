# Arogya-Swarm Backend

Multi-Agent Hospital Operations AI System - FastAPI Backend

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- PostgreSQL
- Redis

### Setup

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Run Database**
```bash
# Using Docker
docker-compose up -d postgres redis
```

4. **Start Server**
```bash
uvicorn main:app --reload --port 8000
```

API will be available at: http://localhost:8000

## 📚 API Documentation

- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **WebSocket**: ws://localhost:8000/ws

## 🌐 Railway Deployment

### Quick Deploy to Railway

1. **Follow the Deployment Checklist**
   - See [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)

2. **Detailed Guide**
   - See [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)

3. **Environment Variables Template**
   - See [.env.railway](./.env.railway)

### Key Files for Railway
- `nixpacks.toml` - Build configuration
- `Procfile` - Process definition
- `railway.json` - Railway-specific settings
- `requirements.txt` - Python dependencies

## 🏗️ Project Structure

```
backend/
├── agents/              # LangGraph multi-agent system
│   ├── sentinel_agent.py      # Monitors external data
│   ├── orchestrator_agent.py  # Coordinates decisions
│   └── action_agents.py       # Executes actions
├── api/                 # API endpoints
│   ├── routes.py        # REST API routes
│   └── websocket.py     # WebSocket manager
├── core/                # Core configuration
│   ├── config.py        # Settings & env vars
│   ├── database.py      # Database connection
│   └── logging_config.py
├── models/              # SQLAlchemy models
├── services/            # Business logic
│   ├── aqi_service.py
│   ├── forecasting.py
│   ├── rag_service.py
│   └── translation_service.py
├── simulation/          # Data generators
└── main.py             # FastAPI app entry point
```

## 🔑 Required API Keys

### Essential (Free Tier)
1. **Google Gemini API** - AI/LLM
   - Get from: https://makersuite.google.com/app/apikey
   - Free tier: 60 requests/min

2. **Google Maps Air Quality API** - Environmental data
   - Get from: https://console.cloud.google.com/google/maps-apis
   - Enable "Air Quality API"

### Optional
- **Twilio** - Real SMS/WhatsApp
- **Razorpay** - Payment processing
- **Hugging Face** - Image diagnosis

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_agents.py

# Run with coverage
pytest --cov=. --cov-report=html
```

## 📦 Key Dependencies

- **FastAPI** - Web framework
- **LangChain** - AI agent framework
- **LangGraph** - Multi-agent orchestration
- **SQLAlchemy** - Database ORM
- **Prophet** - Time-series forecasting
- **Redis** - Caching & pub/sub
- **Uvicorn** - ASGI server

## 🛠️ Development

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Code Quality

```bash
# Format code
black .

# Lint
flake8

# Type checking
mypy .
```

## 🔍 Monitoring

### Health Endpoints
- `/health` - Basic health check
- `/` - API info

### Logs
- Local: Check console output
- Railway: View in dashboard

## 🌟 Features

- ✅ Multi-agent AI system (LangGraph)
- ✅ Real-time WebSocket updates
- ✅ Air quality monitoring
- ✅ Patient surge prediction
- ✅ Resource optimization
- ✅ Multi-language support (translation)
- ✅ RAG-powered medical chatbot
- ✅ SMS/WhatsApp notifications (mock mode)
- ✅ Cost-benefit analysis

## 🔒 Security

- Environment variables for sensitive data
- CORS configured for frontend only
- Database credentials managed securely
- API rate limiting (via external services)

## 📝 Environment Variables

See `.env.example` for all available configuration options.

Essential variables:
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis connection
- `GOOGLE_API_KEY` - Gemini API
- `AIR_QUALITY_API_KEY` - Google Maps API
- `FRONTEND_URL` - CORS configuration

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
psql $DATABASE_URL

# Verify connection string format
postgresql://user:password@host:port/database
```

### Redis Connection Issues
```bash
# Test Redis connection
redis-cli -u $REDIS_URL ping
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📞 Support

- **Documentation**: Check `docs/` folder
- **Issues**: GitHub Issues
- **Railway Support**: https://discord.gg/railway

## 📄 License

See main project LICENSE file.

## 🚀 Deployment Status

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

---

**Built with ❤️ for Square Hacks**
