"""
Dynamic Translation Service with FREE APIs
Uses MyMemory Translation API (5000-10000 requests/day, NO API KEY required)
Falls back to cached translations and offline dictionary
"""

import requests
import hashlib
import logging
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from core.database import get_db
from core.config import settings
from cachetools import TTLCache
from langdetect import detect, LangDetectException

logger = logging.getLogger(__name__)

class TranslationService:
    """
    Free dynamic translation service
    Provider: MyMemory Translation API (no signup required)
    Fallback: Cached translations + static dictionary
    """
    
    SUPPORTED_LANGUAGES = {
        'en': 'english',
        'hi': 'hindi',
        'mr': 'marathi',
        'ta': 'tamil',
        'te': 'telugu',
        'bn': 'bengali'
    }
    
    # In-memory cache (60 minutes TTL)
    _memory_cache = TTLCache(maxsize=1000, ttl=3600)
    
    # Common medical phrases (fallback for offline mode)
    STATIC_PHRASES = {
        'hi': {
            'surge_alert': 'अस्पताल में मरीजों की संख्या बढ़ने की संभावना है',
            'appointment_reminder': 'आपकी अपॉइंटमेंट याद रखें',
            'medicine_reminder': 'अपनी दवा लेने का समय हो गया है',
            'emergency': 'आपातकालीन स्थिति - तुरंत अस्पताल जाएं',
            'symptoms': 'लक्षण',
            'diagnosis': 'निदान',
            'prescription': 'नुस्खा',
            'dashboard': 'डैशबोर्ड',
            'patients': 'मरीज़',
            'doctor': 'डॉक्टर',
            'hospital': 'अस्पताल'
        },
        'mr': {
            'surge_alert': 'रुग्णालयात रुग्णांची संख्या वाढण्याची शक्यता आहे',
            'appointment_reminder': 'तुमची भेट लक्षात ठेवा',
            'medicine_reminder': 'तुमचे औषध घेण्याची वेळ झाली आहे',
            'emergency': 'आणीबाणीची परिस्थिती - त्वरित रुग्णालयात जा',
            'symptoms': 'लक्षणे',
            'diagnosis': 'निदान',
            'prescription': 'औषध पत्रक',
            'dashboard': 'डॅशबोर्ड',
            'patients': 'रुग्ण',
            'doctor': 'डॉक्टर',
            'hospital': 'रुग्णालय'
        },
        'ta': {
            'symptoms': 'அறிகுறிகள்',
            'diagnosis': 'நோய் கண்டறிதல்',
            'prescription': 'மருந்து பரிந்துரை',
            'dashboard': 'டாஷ்போர்டு',
            'patients': 'நோயாளிகள்',
            'doctor': 'மருத்துவர்',
            'hospital': 'மருத்துவமனை'
        }
    }
    
    @classmethod
    def _generate_cache_key(cls, text: str, source_lang: str, target_lang: str) -> str:
        """Generate unique cache key for translation"""
        combined = f"{text}:{source_lang}:{target_lang}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    @classmethod
    def _get_from_db_cache(cls, text: str, source_lang: str, target_lang: str, db: Session) -> Optional[str]:
        """Get translation from database cache"""
        try:
            result = db.execute(
                """
                SELECT translated_text FROM translation_cache 
                WHERE source_text = :text 
                AND source_lang = :source 
                AND target_lang = :target
                AND created_at > NOW() - INTERVAL '7 days'
                LIMIT 1
                """,
                {'text': text, 'source': source_lang, 'target': target_lang}
            ).fetchone()
            
            if result:
                logger.info(f"Translation cache HIT (DB): {text[:50]}")
                return result[0]
        except Exception as e:
            logger.error(f"DB cache read error: {e}")
        
        return None
    
    @classmethod
    def _save_to_db_cache(cls, text: str, source_lang: str, target_lang: str, 
                         translated: str, db: Session, provider: str = 'mymemory'):
        """Save translation to database cache"""
        try:
            db.execute(
                """
                INSERT INTO translation_cache (source_text, source_lang, target_lang, translated_text, provider)
                VALUES (:text, :source, :target, :translated, :provider)
                ON CONFLICT (source_text, source_lang, target_lang) 
                DO UPDATE SET translated_text = :translated, created_at = NOW()
                """,
                {
                    'text': text,
                    'source': source_lang,
                    'target': target_lang,
                    'translated': translated,
                    'provider': provider
                }
            )
            db.commit()
            logger.info(f"Translation cached to DB: {text[:50]}")
        except Exception as e:
            logger.error(f"DB cache save error: {e}")
            db.rollback()
    
    @classmethod
    def _translate_via_mymemory(cls, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        Translate using MyMemory API (FREE: 5000 requests/day, no signup)
        With email: 10000 requests/day
        URL: https://mymemory.translated.net/doc/spec.php
        """
        try:
            url = "https://api.mymemory.translated.net/get"
            
            params = {
                'q': text,
                'langpair': f"{source_lang}|{target_lang}",
            }
            
            # Add email for higher rate limit (optional)
            if hasattr(settings, 'TRANSLATION_API_EMAIL') and settings.TRANSLATION_API_EMAIL:
                params['de'] = settings.TRANSLATION_API_EMAIL
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('responseStatus') == 200:
                    translated = data.get('responseData', {}).get('translatedText')
                    
                    if translated and translated.lower() != text.lower():
                        logger.info(f"MyMemory translation: {text[:50]} -> {translated[:50]}")
                        return translated
                else:
                    logger.warning(f"MyMemory API error: {data.get('responseDetails')}")
            else:
                logger.error(f"MyMemory API HTTP {response.status_code}")
                
        except requests.RequestException as e:
            logger.error(f"MyMemory API request failed: {e}")
        except Exception as e:
            logger.error(f"MyMemory translation error: {e}")
        
        return None
    
    @classmethod
    def _check_static_phrase(cls, text: str, target_lang: str) -> Optional[str]:
        """Check if text matches a static pre-translated phrase"""
        text_lower = text.lower().strip()
        phrases = cls.STATIC_PHRASES.get(target_lang, {})
        
        # Exact match
        if text_lower in phrases:
            return phrases[text_lower]
        
        # Partial match (if text contains the key)
        for key, value in phrases.items():
            if key in text_lower:
                return value
        
        return None
    
    @classmethod
    def detect_language(cls, text: str) -> str:
        """Detect language of text"""
        try:
            lang = detect(text)
            # Map ISO codes to our supported languages
            lang_map = {
                'en': 'en',
                'hi': 'hi',
                'mr': 'mr',
                'ta': 'ta',
                'te': 'te',
                'bn': 'bn'
            }
            return lang_map.get(lang, 'en')
        except LangDetectException:
            return 'en'
    
    @classmethod
    def translate(
        cls, 
        text: str, 
        target_lang: str, 
        source_lang: str = 'auto',
        db: Session = None
    ) -> str:
        """
        Dynamic translation with multi-layer fallback:
        1. Memory cache (fast)
        2. Database cache (medium)
        3. Static phrases (offline)
        4. MyMemory API (dynamic)
        5. Original text (ultimate fallback)
        """
        if not text or not text.strip():
            return text
        
        # Auto-detect source language
        if source_lang == 'auto':
            source_lang = cls.detect_language(text)
        
        # No translation needed
        if target_lang == source_lang:
            return text
        
        # Validate target language
        if target_lang not in cls.SUPPORTED_LANGUAGES:
            logger.warning(f"Unsupported language: {target_lang}")
            return text
        
        # Get DB session if not provided
        if db is None:
            db = next(get_db())
        
        # 1. Check memory cache
        cache_key = cls._generate_cache_key(text, source_lang, target_lang)
        if cache_key in cls._memory_cache:
            logger.info(f"Translation cache HIT (memory): {text[:50]}")
            return cls._memory_cache[cache_key]
        
        # 2. Check database cache
        cached = cls._get_from_db_cache(text, source_lang, target_lang, db)
        if cached:
            cls._memory_cache[cache_key] = cached
            return cached
        
        # 3. Check static phrases
        static = cls._check_static_phrase(text, target_lang)
        if static:
            logger.info(f"Translation from static dictionary: {text[:50]}")
            cls._memory_cache[cache_key] = static
            cls._save_to_db_cache(text, source_lang, target_lang, static, db, 'static')
            return static
        
        # 4. Try MyMemory API (dynamic translation)
        translated = cls._translate_via_mymemory(text, source_lang, target_lang)
        
        if translated:
            # Cache successful translation
            cls._memory_cache[cache_key] = translated
            cls._save_to_db_cache(text, source_lang, target_lang, translated, db, 'mymemory')
            return translated
        
        # 5. Ultimate fallback: return original text
        logger.warning(f"Translation failed for: {text[:50]} ({source_lang} -> {target_lang})")
        return text
    
    @classmethod
    def translate_bulk(
        cls, 
        texts: List[str], 
        target_lang: str, 
        source_lang: str = 'auto',
        db: Session = None
    ) -> List[str]:
        """Translate multiple texts (uses caching for efficiency)"""
        return [cls.translate(text, target_lang, source_lang, db) for text in texts]
    
    @classmethod
    def translate_llm_response(
        cls, 
        response: str, 
        target_lang: str,
        db: Session = None
    ) -> str:
        """
        Translate LLM response intelligently
        Preserves formatting and translates sentence by sentence
        """
        if target_lang == 'en':
            return response
        
        # Split by sentences (basic splitting)
        sentences = response.split('. ')
        translated_sentences = []
        
        for sentence in sentences:
            if sentence.strip():
                translated = cls.translate(sentence, target_lang, 'en', db)
                translated_sentences.append(translated)
        
        return '. '.join(translated_sentences)
    
    @classmethod
    def get_cache_stats(cls, db: Session) -> Dict:
        """Get translation cache statistics"""
        try:
            result = db.execute(
                """
                SELECT 
                    COUNT(*) as total_cached,
                    COUNT(DISTINCT target_lang) as languages,
                    provider,
                    COUNT(*) as count
                FROM translation_cache
                GROUP BY provider
                """
            ).fetchall()
            
            stats = {
                'memory_cache_size': len(cls._memory_cache),
                'db_cache_total': 0,
                'by_provider': {}
            }
            
            for row in result:
                stats['db_cache_total'] += row[3]
                stats['by_provider'][row[2]] = row[3]
            
            return stats
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {'error': str(e)}
