from celery import shared_task
from flask import current_app
import logging
from .models.sql_models import User
from .database import SessionLocal
from .utils.scan_utils import save_scan_to_db

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def analyze_skin_task(self, image_data, user_id=None):
    """
    Background task for skin analysis.
    """
    try:
        # Get services
        analysis_service = current_app.services.get('analysis_service')
        if not analysis_service:
            raise Exception("Analysis service not initialized")
            
        # Perform analysis
        results = analysis_service.analyze_skin(image_data)
        
        # Check opt-out status
        should_save_data = True
        if user_id and user_id != 'anonymous':
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.firebase_uid == user_id).first()
                if user and user.opt_out_data_collection:
                    should_save_data = False
                    logger.info(f"User {user_id} opted out of data collection. Skipping save.")
            finally:
                db.close()
        
        scan_id = None
        if should_save_data:
            scan_id = save_scan_to_db(image_data, results, user_id)
            if scan_id:
                results['scan_id'] = scan_id
                
        return results
        
    except Exception as e:
        logger.error(f"Task failed: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
        # Re-raise to mark task as failed in Celery
        raise e
