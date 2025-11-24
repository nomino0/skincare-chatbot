"""
Analysis routes for skin analysis API endpoints.
"""

from flask import Blueprint, request, jsonify, current_app
import logging

analysis_bp = Blueprint('analysis', __name__)
logger = logging.getLogger(__name__)


@analysis_bp.route('/analyze', methods=['POST'])
def analyze_skin():
    """
    Analyze skin from uploaded image.
    
    Expected JSON body:
    {
        "image": "base64_encoded_image_data"
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
            logger.error("Analysis service not initialized")
            return jsonify({'error': 'Analysis service unavailable'}), 503
        
        # Process the image
        image_data = data['image']
        
        # Perform analysis
        results = analysis_service.analyze_skin(image_data)
        
        return jsonify(results), 200
        
    except Exception as e:
        logger.error(f"Error in skin analysis: {e}", exc_info=True)
        return jsonify({'error': 'Failed to analyze skin', 'message': str(e)}), 500
