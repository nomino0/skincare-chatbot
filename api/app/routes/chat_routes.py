"""
Chat routes for AI chatbot API endpoints.
"""

from flask import Blueprint, request, jsonify, current_app
import logging

chat_bp = Blueprint('chat', __name__)
logger = logging.getLogger(__name__)


@chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    Handle chat messages with AI assistant.
    
    Expected JSON body:
    {
        "message": "user message",
        "conversationHistory": [...],
        "skinAnalysis": {...},
        "userLocation": {...}
    }
    
    Returns:
        JSON with AI response
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get services from app context
        chat_service = current_app.services.get('chat_service')
        
        if not chat_service:
            logger.error("Chat service not initialized")
            return jsonify({'error': 'Chat service unavailable'}), 503
        
        # Extract request data
        user_message = data['message']
        conversation_history = data.get('conversationHistory', [])
        skin_analysis = data.get('skinAnalysis')
        user_location = data.get('userLocation')
        
        # Generate response
        response = chat_service.generate_response(
            user_message=user_message,
            conversation_history=conversation_history,
            skin_analysis=skin_analysis,
            user_location=user_location
        )
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in chat: {e}", exc_info=True)
        return jsonify({'error': 'Failed to generate response', 'message': str(e)}), 500
