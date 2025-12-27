from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from core.database import get_db
from models.hospital import Bed, Staff, Inventory
from models.predictions import SurgePrediction
from models.actions import Recommendation
from agents import ArogyaSwarmGraph
from services.cost_calculator import CostCalculator
from services.rag_service import get_rag_service

router = APIRouter()

# ============================================
# REQUEST MODELS
# ============================================

class CrisisSimulationRequest(BaseModel):
    crisis_type: str  # 'pollution', 'dengue', 'trauma'

class RagQueryRequest(BaseModel):
    question: str
    context: Optional[dict] = None

class RagIngestRequest(BaseModel):
    documents: List[dict]

# ============================================
# HOSPITAL STATE ENDPOINTS
# ============================================

@router.get("/beds")
async def get_bed_availability(
    department: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get current bed availability"""
    query = db.query(Bed)
    if department:
        query = query.filter(Bed.department == department)
    beds = query.all()
    
    # Aggregate by department
    availability = {}
    for bed in beds:
        if bed.department not in availability:
            availability[bed.department] = {"total": 0, "available": 0, "occupied": 0}
        availability[bed.department]["total"] += 1
        if bed.status == "available":
            availability[bed.department]["available"] += 1
        elif bed.status == "occupied":
            availability[bed.department]["occupied"] += 1
    
    return availability

@router.get("/staff")
async def get_staff_availability(
    shift: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get staff availability"""
    query = db.query(Staff)
    if shift:
        query = query.filter(Staff.shift == shift)
    staff = query.all()
    
    # Calculate medical staff metrics (doctors + nurses only)
    doctors_count = len([s for s in staff if s.role == "doctor"])
    nurses_count = len([s for s in staff if s.role == "nurse"])
    doctors_available = len([s for s in staff if s.role == "doctor" and s.status == "available"])
    nurses_available = len([s for s in staff if s.role == "nurse" and s.status == "available"])
    
    total_medical_staff = doctors_count + nurses_count
    total_available = doctors_available + nurses_available
    on_duty_count = total_medical_staff - total_available
    
    return {
        "total": len(staff),
        "available": len([s for s in staff if s.status == "available"]),
        "on_duty": on_duty_count,
        "doctors": doctors_count,
        "nurses": nurses_count,
        "doctors_available": doctors_available,
        "nurses_available": nurses_available,
        "avg_fatigue": sum([s.fatigue_score for s in staff]) / len(staff) if staff else 0
    }

@router.get("/inventory")
async def get_inventory_status(
    critical_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get inventory levels"""
    query = db.query(Inventory)
    if critical_only:
        query = query.filter(Inventory.current_stock < Inventory.minimum_threshold)
    inventory = query.all()
    
    return [
        {
            "item": item.item_name,
            "current": item.current_stock,
            "threshold": item.minimum_threshold,
            "status": "critical" if item.current_stock < item.minimum_threshold else "ok"
        }
        for item in inventory
    ]

# ============================================
# AGENT & PREDICTION ENDPOINTS
# ============================================

@router.get("/predictions/latest")
async def get_latest_prediction(db: Session = Depends(get_db)):
    """Get most recent surge prediction"""
    prediction = db.query(SurgePrediction).order_by(SurgePrediction.prediction_time.desc()).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="No predictions available")
    return prediction

@router.get("/predictions/history")
async def get_prediction_history(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get historical predictions"""
    predictions = db.query(SurgePrediction).order_by(SurgePrediction.prediction_time.desc()).limit(limit).all()
    return predictions

@router.post("/agent/run")
async def trigger_agent_run(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Manually trigger agent workflow"""
    # Add to background tasks to avoid timeout
    background_tasks.add_task(run_agent_workflow, db)
    return {"message": "Agent workflow started", "status": "processing"}

async def run_agent_workflow(db: Session):
    """Execute agent workflow (called as background task)"""
    # Similar to monitoring loop in main.py
    pass

# ============================================
# RECOMMENDATIONS ENDPOINTS
# ============================================

@router.get("/recommendations")
async def get_recommendations(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get recommendations"""
    query = db.query(Recommendation)
    if status:
        query = query.filter(Recommendation.status == status)
    recommendations = query.order_by(Recommendation.created_at.desc()).all()
    return recommendations

@router.post("/recommendations/{rec_id}/approve")
async def approve_recommendation(
    rec_id: str,
    db: Session = Depends(get_db)
):
    """Approve a pending recommendation"""
    rec = db.query(Recommendation).filter(Recommendation.id == rec_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    rec.status = "approved"
    rec.executed_at = datetime.now()
    db.commit()
    
    return {"message": "Recommendation approved", "recommendation": rec}

@router.post("/recommendations/{rec_id}/reject")
async def reject_recommendation(
    rec_id: str,
    reason: str,
    db: Session = Depends(get_db)
):
    """Reject a recommendation"""
    rec = db.query(Recommendation).filter(Recommendation.id == rec_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    rec.status = "rejected"
    rec.outcome = f"Rejected: {reason}"
    db.commit()
    
    return {"message": "Recommendation rejected"}

# ============================================
# COST CALCULATOR ENDPOINT
# ============================================

@router.get("/analytics/cost-savings")
async def get_cost_savings(db: Session = Depends(get_db)):
    """Calculate total cost savings from approved recommendations"""
    calculator = CostCalculator(db)
    savings = calculator.calculate_total_savings()
    return savings

# ============================================
# SIMULATION ENDPOINTS (for demo)
# ============================================

@router.post("/simulation/trigger-crisis")
async def trigger_crisis_simulation(
    request: CrisisSimulationRequest,
    db: Session = Depends(get_db)
):
    """Trigger a crisis scenario for demo"""
    from simulation.scenarios import load_scenario
    scenario_data = load_scenario(request.crisis_type)
    
    # Inject scenario data into system
    # Update external data cache, trigger agent run
    
    return {
        "message": f"Crisis simulation '{request.crisis_type}' triggered",
        "scenario": scenario_data
    }

@router.get("/agents/test-reasoning")
async def test_agent_reasoning():
    """Generate sample agent reasoning chain for testing"""
    from datetime import datetime
    
    reasoning_chain = [
        {
            "agent": "Sentinel",
            "message": "Analyzing environmental data from OpenWeatherMap API...",
            "timestamp": datetime.now().isoformat(),
            "level": "info"
        },
        {
            "agent": "Sentinel",
            "message": "AQI levels detected at 187 (Unhealthy). PM2.5 concentration: 92 µg/m³",
            "timestamp": datetime.now().isoformat(),
            "level": "warning"
        },
        {
            "agent": "Sentinel",
            "message": "Historical correlation analysis: 68% increase in respiratory admissions during high AQI periods",
            "timestamp": datetime.now().isoformat(),
            "level": "info"
        },
        {
            "agent": "Orchestrator",
            "message": "Received alert from Sentinel. Initiating coordinated response protocol.",
            "timestamp": datetime.now().isoformat(),
            "level": "info"
        },
        {
            "agent": "Orchestrator",
            "message": "Predicted surge: +45 respiratory patients in next 6 hours. Current ICU capacity: 78%",
            "timestamp": datetime.now().isoformat(),
            "level": "warning"
        },
        {
            "agent": "Logistics",
            "message": "Inventory check: Nebulizers at 67%, Oxygen tanks at 82%, Bronchodilators at 71%",
            "timestamp": datetime.now().isoformat(),
            "level": "info"
        },
        {
            "agent": "Logistics",
            "message": "Calculating optimal resource allocation using dynamic programming...",
            "timestamp": datetime.now().isoformat(),
            "level": "info"
        },
        {
            "agent": "Action",
            "message": "Recommendation: Increase respiratory ward staffing by 30% for next shift",
            "timestamp": datetime.now().isoformat(),
            "level": "success"
        },
        {
            "agent": "Action",
            "message": "Recommendation: Pre-allocate 12 ICU beds for respiratory cases",
            "timestamp": datetime.now().isoformat(),
            "level": "success"
        },
        {
            "agent": "Orchestrator",
            "message": "Response plan finalized. Estimated cost savings: ₹2.4L vs reactive approach",
            "timestamp": datetime.now().isoformat(),
            "level": "success"
        }
    ]
    
    messages = [
        "High AQI alert detected",
        "Surge prediction: +45 respiratory cases",
        "Resource allocation optimized",
        "Staff scheduling updated"
    ]
    
    return {
        "reasoning_chain": reasoning_chain,
        "messages": messages,
        "surge_prediction": {
            "predicted_surge": 45,
            "confidence": 0.87,
            "timeline_hours": 6,
            "trigger": "environmental"
        },
        "recommendations": [
            {
                "priority": "high",
                "action": "Increase respiratory ward staffing by 30%",
                "estimated_cost": 15000,
                "department": "respiratory"
            },
            {
                "priority": "high", 
                "action": "Pre-allocate 12 ICU beds for respiratory cases",
                "estimated_cost": 0,
                "department": "icu"
            }
        ],
        "timestamp": datetime.now().isoformat()
    }

@router.get("/environment/aqi")
async def get_current_aqi(lat: Optional[float] = None, lon: Optional[float] = None, city: str = "Mumbai"):
    """
    Get real-time AQI from Google Maps Air Quality API.
    
    Uses adapter layer to maintain frontend contract compatibility.
    No frontend changes required.
    
    Args:
        lat: Optional latitude for live location
        lon: Optional longitude for live location
        city: City name (default: Mumbai) - used if lat/lon not provided
    
    Returns:
        OpenWeather-compatible response format with Google data
    """
    from services.aqi_service import AQIService
    from core.config import settings
    
    aqi_service = AQIService(settings.AIR_QUALITY_API_KEY)
    
    # Service returns full adapter response
    result = await aqi_service.get_current_aqi(city=city, lat=lat, lon=lon)
    
    # Add city context if using coordinates
    if lat and lon:
        result["city"] = "Current Location"
    else:
        result["city"] = city
    
    return result

# ============================================
# RAG CHATBOT ENDPOINTS
# ============================================

@router.post("/rag/query")
async def query_rag_chatbot(
    request: RagQueryRequest
):
    """
    Query the RAG chatbot with a question
    Returns AI-generated answer with source documents
    """
    try:
        rag_service = get_rag_service()
        result = rag_service.query(
            question=request.question,
            context=request.context,
            top_k=3
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")

@router.post("/rag/ingest")
async def ingest_rag_documents(
    request: RagIngestRequest,
    background_tasks: BackgroundTasks
):
    """
    Ingest new documents into RAG system
    Requires documents with 'id', 'content', 'metadata' fields
    """
    try:
        rag_service = get_rag_service()
        
        # Process in background to avoid timeout
        if len(request.documents) > 10:
            background_tasks.add_task(
                rag_service.ingest_documents,
                request.documents
            )
            return {
                "status": "processing",
                "message": f"Ingesting {len(request.documents)} documents in background"
            }
        else:
            result = rag_service.ingest_documents(request.documents)
            return result
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG ingestion failed: {str(e)}")

@router.get("/rag/status")
async def get_rag_status():
    """
    Get RAG system health and statistics
    """
    try:
        rag_service = get_rag_service()
        status = rag_service.get_status()
        return status
    except Exception as e:
        return {
            "status": "error",
            "initialized": False,
            "document_count": 0,
            "database_connected": False,
            "error": str(e)
        }

# ==================== PHASE 1: DYNAMIC MULTILINGUAL SUPPORT ====================
from services.translation_service import TranslationService
import logging

logger = logging.getLogger(__name__)

@router.post("/translate")
async def translate_text(
    text: str,
    target_lang: str,
    source_lang: str = 'auto',
    db: Session = Depends(get_db)
):
    """
    Dynamic translation using FREE MyMemory API
    Supports: English, Hindi, Marathi, Tamil, Telugu, Bengali
    Uses multi-layer caching for performance
    """
    try:
        translated = TranslationService.translate(
            text=text,
            target_lang=target_lang,
            source_lang=source_lang,
            db=db
        )
        
        detected_lang = TranslationService.detect_language(text) if source_lang == 'auto' else source_lang
        
        return {
            "success": True,
            "original": text,
            "translated": translated,
            "source_lang": detected_lang,
            "target_lang": target_lang,
            "cached": translated != text
        }
    except Exception as e:
        logger.error(f"Translation endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/translate/bulk")
async def translate_bulk_text(
    texts: List[str],
    target_lang: str,
    source_lang: str = 'auto',
    db: Session = Depends(get_db)
):
    """Translate multiple texts at once"""
    try:
        translated = TranslationService.translate_bulk(
            texts=texts,
            target_lang=target_lang,
            source_lang=source_lang,
            db=db
        )
        
        return {
            "success": True,
            "count": len(texts),
            "translations": [
                {"original": orig, "translated": trans}
                for orig, trans in zip(texts, translated)
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "success": True,
        "languages": TranslationService.SUPPORTED_LANGUAGES,
        "providers": ["mymemory"],
        "free_tier_limits": {
            "mymemory": "5000 requests/day (10000 with email)"
        }
    }

@router.get("/translation/stats")
async def get_translation_stats(db: Session = Depends(get_db)):
    """Get translation cache statistics"""
    stats = TranslationService.get_cache_stats(db)
    return {
        "success": True,
        "stats": stats
    }

@router.post("/translation/detect")
async def detect_text_language(text: str):
    """Detect language of given text"""
    try:
        detected = TranslationService.detect_language(text)
        return {
            "success": True,
            "text": text,
            "detected_language": detected,
            "language_name": TranslationService.SUPPORTED_LANGUAGES.get(detected, "unknown")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== PHASE 1: MESSAGING SERVICE ====================
from services.messaging_service import MessagingService

@router.post("/messaging/sms")
async def send_sms_message(
    phone: str,
    message: str,
    recipient_name: Optional[str] = None,
    language: str = 'en',
    db: Session = Depends(get_db)
):
    """Send SMS message (mock for demo)"""
    messaging = MessagingService(db)
    result = await messaging.send_sms(
        phone=phone,
        message=message,
        recipient_name=recipient_name,
        language=language
    )
    return result

@router.post("/messaging/whatsapp")
async def send_whatsapp_message(
    phone: str,
    message: str,
    recipient_name: Optional[str] = None,
    media_url: Optional[str] = None,
    language: str = 'en',
    db: Session = Depends(get_db)
):
    """Send WhatsApp message (mock for demo)"""
    messaging = MessagingService(db)
    result = await messaging.send_whatsapp(
        phone=phone,
        message=message,
        recipient_name=recipient_name,
        media_url=media_url,
        language=language
    )
    return result

@router.post("/messaging/bulk-alert")
async def send_bulk_alert(
    recipients: List[dict],
    message: str,
    db: Session = Depends(get_db)
):
    """
    Send bulk alerts to multiple recipients
    recipients: [{"phone": "+919876543210", "name": "Name", "language": "hi"}]
    """
    messaging = MessagingService(db)
    result = await messaging.send_bulk_alerts(recipients, message)
    return result

@router.get("/messaging/logs")
async def get_message_logs(
    limit: int = 50,
    phone: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get message logs"""
    messaging = MessagingService(db)
    logs = messaging.get_message_logs(limit, phone, status)
    return {"success": True, "logs": logs, "count": len(logs)}
