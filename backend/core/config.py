from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Database - Railway automatically provides these
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/arogya_swarm")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # LLM
    GOOGLE_API_KEY: str
    VITE_GEMINI_API_KEY: Optional[str] = None  # For RAG system
    
    # External APIs
    AIR_QUALITY_API_KEY: str = ""  # Google Maps Air Quality API key (backend-only, not exposed to frontend)
    SAFAR_AIR_API_KEY: Optional[str] = None
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    TWILIO_WHATSAPP_NUMBER: Optional[str] = None
    
    # Messaging Features (Phase 1)
    ENABLE_REAL_SMS: bool = False
    ENABLE_REAL_WHATSAPP: bool = False
    
    # Payment (Phase 3)
    RAZORPAY_KEY_ID: Optional[str] = None
    RAZORPAY_KEY_SECRET: Optional[str] = None
    RAZORPAY_WEBHOOK_SECRET: Optional[str] = None
    
    # Hospital Configuration
    HOSPITAL_NAME: str = "Apollo Metro Hospital"
    HOSPITAL_CITY: str = "Mumbai"
    HOSPITAL_BEDS: int = 400
    
    # Feature Flags
    DEMO_MODE: bool = True
    ENABLE_VOICE_NARRATION: bool = True
    ENABLE_SMS_NOTIFICATIONS: bool = False
    ENABLE_TWITTER_MOCK: bool = True
    ENABLE_RAG_CHATBOT: bool = True
    
    # App Settings
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False
    PORT: int = int(os.getenv("PORT", "8000"))  # Railway provides PORT variable
    
    # Translation API (Phase 1)
    TRANSLATION_API_PROVIDER: str = "mymemory"
    TRANSLATION_API_EMAIL: Optional[str] = None
    
    # Image Diagnosis (Phase 2)
    GOOGLE_CLOUD_PROJECT_ID: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    
    # Video Conferencing (Phase 3)
    JITSI_DOMAIN: str = "meet.jit.si"
    DAILY_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra environment variables (e.g., old GOOGLE_MAPS_API_KEY)

settings = Settings()
