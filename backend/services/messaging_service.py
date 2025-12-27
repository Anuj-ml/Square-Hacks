"""
Mock SMS/WhatsApp service (FREE - no API required)
Logs all messages to database for demo purposes
In production: Replace with Twilio/WhatsApp Business API
"""

import asyncio
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from core.database import get_db
from services.translation_service import TranslationService
import logging

logger = logging.getLogger(__name__)

class MessagingService:
    """
    Mock messaging service for SMS and WhatsApp
    FREE tier - no actual sending, just logging for demo
    """
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
    
    async def send_sms(
        self,
        phone: str,
        message: str,
        recipient_name: Optional[str] = None,
        message_type: str = 'alert',
        language: str = 'en'
    ) -> Dict:
        """Mock SMS sending - logs to database"""
        # Translate message if needed (using dynamic translation)
        if language != 'en':
            message = TranslationService.translate(message, language, 'en', self.db)
        
        # Log to database
        try:
            self.db.execute(
                """
                INSERT INTO sms_logs 
                (recipient_phone, recipient_name, message, language, type, channel, status, sent_at)
                VALUES (:phone, :name, :message, :lang, :type, 'sms', 'sent_mock', NOW())
                """,
                {
                    'phone': phone,
                    'name': recipient_name,
                    'message': message,
                    'lang': language,
                    'type': message_type
                }
            )
            self.db.commit()
            
            # Print to console for demo visibility
            print(f"\n📱 SMS SENT")
            print(f"To: {phone} ({recipient_name or 'Unknown'})")
            print(f"Message: {message}")
            print(f"Language: {language}\n")
            
            return {
                'success': True,
                'message_id': f'mock_sms_{int(datetime.now().timestamp())}',
                'phone': phone,
                'status': 'sent_mock'
            }
            
        except Exception as e:
            logger.error(f"SMS logging error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def send_whatsapp(
        self,
        phone: str,
        message: str,
        recipient_name: Optional[str] = None,
        media_url: Optional[str] = None,
        language: str = 'en'
    ) -> Dict:
        """Mock WhatsApp sending - logs to database"""
        # Translate message (dynamic)
        if language != 'en':
            message = TranslationService.translate(message, language, 'en', self.db)
        
        # Append media info to message
        if media_url:
            message = f"{message}\n[Media: {media_url}]"
        
        try:
            self.db.execute(
                """
                INSERT INTO sms_logs 
                (recipient_phone, recipient_name, message, language, type, channel, status, sent_at)
                VALUES (:phone, :name, :message, :lang, 'whatsapp', 'whatsapp', 'sent_mock', NOW())
                """,
                {
                    'phone': phone,
                    'name': recipient_name,
                    'message': message,
                    'lang': language
                }
            )
            self.db.commit()
            
            print(f"\n💬 WhatsApp SENT")
            print(f"To: {phone} ({recipient_name or 'Unknown'})")
            print(f"Message: {message}")
            print(f"Language: {language}\n")
            
            return {
                'success': True,
                'message_id': f'mock_wa_{int(datetime.now().timestamp())}',
                'phone': phone,
                'status': 'sent_mock'
            }
            
        except Exception as e:
            logger.error(f"WhatsApp logging error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def send_bulk_alerts(
        self,
        recipients: List[Dict[str, str]],
        message: str,
        message_type: str = 'bulk_alert'
    ) -> Dict:
        """Send alerts to multiple recipients"""
        results = []
        failed = 0
        
        for recipient in recipients:
            phone = recipient.get('phone')
            name = recipient.get('name')
            language = recipient.get('language', 'en')
            
            try:
                result = await self.send_sms(
                    phone=phone,
                    message=message,
                    recipient_name=name,
                    message_type=message_type,
                    language=language
                )
                results.append(result)
                
                if not result.get('success'):
                    failed += 1
                
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Bulk alert error for {phone}: {e}")
                failed += 1
        
        return {
            'success': True,
            'total': len(recipients),
            'sent': len(results) - failed,
            'failed': failed,
            'results': results
        }
    
    def get_message_logs(
        self,
        limit: int = 50,
        phone: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Get recent message logs"""
        query = "SELECT * FROM sms_logs WHERE 1=1"
        params = {}
        
        if phone:
            query += " AND recipient_phone = :phone"
            params['phone'] = phone
        
        if status:
            query += " AND status = :status"
            params['status'] = status
        
        query += " ORDER BY sent_at DESC LIMIT :limit"
        params['limit'] = limit
        
        result = self.db.execute(query, params)
        return [dict(row) for row in result]
