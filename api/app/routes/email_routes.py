"""
Email routes for sending analysis results.
"""

import logging
from flask import Blueprint, request, jsonify, current_app

logger = logging.getLogger(__name__)

email_bp = Blueprint('email', __name__)


@email_bp.route('/send-analysis-results', methods=['POST'])
def send_analysis_results():
    """
    Send skin analysis results via email.
    
    Expected JSON payload:
    {
        "email": "user@example.com",
        "user_name": "John Doe",
        "analysis_data": {
            "skin_type": "Oily",
            "skin_issues": ["Acne", "Large pores"],
            "demographics": {...},
            "confidence_scores": {...},
            "timestamp": "2024-01-01T12:00:00Z"
        },
        "recommendations": [
            {
                "name": "Product Name",
                "brand": "Brand",
                "price": 25.99,
                "description": "Product description"
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['email', 'user_name', 'analysis_data']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        email = data['email']
        user_name = data['user_name']
        analysis_data = data['analysis_data']
        recommendations = data.get('recommendations', [])
        
        logger.info(f"Sending analysis results to: {email}")
        
        # Get email service
        email_service = current_app.services['email_service']
        
        # Send email
        success = email_service.send_analysis_results(
            email=email,
            user_name=user_name,
            analysis_data=analysis_data,
            recommendations=recommendations
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Analysis results sent successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send email'
            }), 500
        
    except Exception as e:
        logger.error(f"Error sending analysis results: {e}")
        return jsonify({'error': 'Failed to send analysis results'}), 500


@email_bp.route('/send-recommendations', methods=['POST'])
def send_recommendations():
    """
    Send product recommendations via email.
    
    Expected JSON payload:
    {
        "email": "user@example.com",
        "user_name": "John Doe",
        "skin_type": "Oily",
        "skin_issues": ["Acne", "Large pores"],
        "recommendations": [
            {
                "name": "Product Name",
                "brand": "Brand",
                "price": 25.99,
                "description": "Product description",
                "image_url": "https://..."
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['email', 'user_name', 'recommendations']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        email = data['email']
        user_name = data['user_name']
        skin_type = data.get('skin_type', 'Unknown')
        skin_issues = data.get('skin_issues', [])
        recommendations = data['recommendations']
        
        logger.info(f"Sending product recommendations to: {email}")
        
        # Get email service
        email_service = current_app.services['email_service']
        
        # Send email
        success = email_service.send_product_recommendations(
            email=email,
            user_name=user_name,
            skin_type=skin_type,
            skin_issues=skin_issues,
            recommendations=recommendations
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Product recommendations sent successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send email'
            }), 500
        
    except Exception as e:
        logger.error(f"Error sending product recommendations: {e}")
        return jsonify({'error': 'Failed to send product recommendations'}), 500


@email_bp.route('/send-custom-email', methods=['POST'])
def send_custom_email():
    """
    Send a custom email.
    
    Expected JSON payload:
    {
        "email": "user@example.com",
        "subject": "Email Subject",
        "message": "Email body content",
        "is_html": false
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['email', 'subject', 'message']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        email = data['email']
        subject = data['subject']
        message = data['message']
        is_html = data.get('is_html', False)
        
        logger.info(f"Sending custom email to: {email}")
        
        # Get email service
        email_service = current_app.services['email_service']
        
        # Send email
        success = email_service.send_custom_email(
            email=email,
            subject=subject,
            message=message,
            is_html=is_html
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Email sent successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send email'
            }), 500
        
    except Exception as e:
        logger.error(f"Error sending custom email: {e}")
        return jsonify({'error': 'Failed to send email'}), 500


@email_bp.route('/test-email', methods=['POST'])
def test_email():
    """
    Test email configuration by sending a test email.
    
    Expected JSON payload:
    {
        "email": "test@example.com"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({'error': 'Email address is required'}), 400
        
        email = data['email']
        
        logger.info(f"Sending test email to: {email}")
        
        # Get email service
        email_service = current_app.services['email_service']
        
        # Send test email
        success = email_service.send_test_email(email)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Test email sent successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send test email'
            }), 500
        
    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        return jsonify({'error': 'Failed to send test email'}), 500
