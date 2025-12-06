import os
import base64
import uuid
import logging
from datetime import datetime
from ..database import SessionLocal
from ..models.sql_models import Scan

logger = logging.getLogger(__name__)

def save_scan_to_db(image_data: str, results: dict, user_id: str = 'anonymous') -> str:
    """
    Save scan to database for professional review.
    
    Args:
        image_data: Base64 encoded image
        results: Analysis results
        user_id: User ID (optional)
        
    Returns:
        scan_id if saved successfully, None otherwise
    """
    try:
        # Generate unique scan ID
        scan_id = f"scan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Save image to disk (for professional review)
        image_path = save_image_to_disk(image_data, scan_id)
        
        # Create scan record
        db = SessionLocal()
        try:
            scan = Scan(
                user_id=user_id,
                scan_id=scan_id,
                image_path=image_path,
                skin_type_result=results.get('skinType'),
                skin_issues_result=results.get('skinIssues', []),
                demographics_result=results.get('demographics')
            )
            db.add(scan)
            db.commit()
            logger.info(f"Saved scan {scan_id} to database")
            return scan_id
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Failed to save scan to database: {e}")
        return None


def save_image_to_disk(image_data: str, scan_id: str) -> str:
    """
    Save base64 image to disk.
    
    Args:
        image_data: Base64 encoded image
        scan_id: Scan identifier
        
    Returns:
        Path to saved image
    """
    try:
        # Create uploads directory if not exists
        # Assuming this file is in api/app/utils/
        upload_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Decode and save image
        image_bytes = base64.b64decode(image_data)
        image_path = os.path.join(upload_dir, f"{scan_id}.jpg")
        
        with open(image_path, 'wb') as f:
            f.write(image_bytes)
        
        return image_path
        
    except Exception as e:
        logger.error(f"Failed to save image: {e}")
        return None
