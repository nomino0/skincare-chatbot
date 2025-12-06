"""
Analysis routes for skin analysis API endpoints.
"""

from flask import Blueprint, request, jsonify, current_app, g
import logging

analysis_bp = Blueprint('analysis', __name__)
logger = logging.getLogger(__name__)


@analysis_bp.route('/analyze', methods=['POST'])
def analyze_skin():
    """
    Analyze skin from uploaded image.
    
    Expected JSON body:
    {
        "image": "base64_encoded_image_data",
        "use_groq": boolean (optional, default: false)
    }
    
    Returns:
        JSON with skin analysis results
    """
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Get services from app context
        analysis_service = current_app.services.get('analysis_service')
        
        if not analysis_service:
            logger.error("Analysis service not available")
            return jsonify({'error': 'Analysis service not available'}), 500
        
        # Perform analysis
        use_groq = data.get('use_groq', False)
        result = analysis_service.analyze_skin(data['image'], use_groq=use_groq)
        
        if 'error' in result:
            return jsonify(result), 400
            
        # Optionally save scan to database (check opt-out)
        try:
            from ..utils.scan_utils import save_scan_to_db
            from ..database import SessionLocal
            from ..models.sql_models import User
            
            user_id = None
            should_save = True
            
            if hasattr(g, 'user') and g.user:
                user_id = g.user.get('uid')
                # Check if user opted out
                db = SessionLocal()
                try:
                    user = db.query(User).filter(User.firebase_uid == user_id).first()
                    if user and user.opt_out_data_collection == 1:
                        should_save = False
                        logger.info(f"User {user_id} opted out of data collection")
                finally:
                    db.close()
            
            if should_save:
                # Save scan to database (save_scan_to_db handles image saving internally)
                scan_id = save_scan_to_db(
                    image_data=data['image'],
                    results=result,
                    user_id=user_id or 'anonymous'
                )
                    
        except Exception as e:
            logger.warning(f"Failed to save scan data: {e}")
            # Don't fail the request if saving fails
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error analyzing skin: {e}", exc_info=True)
        return jsonify({'error': 'Analysis failed', 'message': str(e)}), 500
