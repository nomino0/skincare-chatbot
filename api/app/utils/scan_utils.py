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
    Save base64 image to disk or S3/Spaces if configured.
    
    Args:
        image_data: Base64 encoded image
        scan_id: Scan identifier
        
    Returns:
        Path or URL to saved image
    """
    try:
        image_bytes = base64.b64decode(image_data)
        filename = f"{scan_id}.jpg"

        # Check for S3/Spaces configuration
        s3_endpoint = os.environ.get('AWS_ENDPOINT_URL')
        s3_key = os.environ.get('AWS_ACCESS_KEY_ID')
        s3_secret = os.environ.get('AWS_SECRET_ACCESS_KEY')
        s3_bucket = os.environ.get('AWS_BUCKET_NAME')

        if s3_endpoint and s3_key and s3_secret and s3_bucket:
            try:
                import boto3
                s3 = boto3.client(
                    's3',
                    endpoint_url=s3_endpoint,
                    aws_access_key_id=s3_key,
                    aws_secret_access_key=s3_secret
                )
                
                # Upload to 'scans/' folder
                s3_path = f"scans/{filename}"
                s3.put_object(
                    Bucket=s3_bucket,
                    Key=s3_path,
                    Body=image_bytes,
                    ACL='public-read',
                    ContentType='image/jpeg'
                )
                
                # Return the public URL
                # Assuming DigitalOcean Spaces URL format
                region = os.environ.get('AWS_REGION', 'fra1')
                url = f"https://{s3_bucket}.{region}.digitaloceanspaces.com/{s3_path}"
                logger.info(f"Uploaded scan to Spaces: {url}")
                return url
            except Exception as s3_error:
                logger.error(f"S3 upload failed, falling back to local: {s3_error}")

        # Fallback to local disk
        upload_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        image_path = os.path.join(upload_dir, filename)
        
        with open(image_path, 'wb') as f:
            f.write(image_bytes)
        
        return image_path
        
    except Exception as e:
        logger.error(f"Failed to save image: {e}")
        return None
