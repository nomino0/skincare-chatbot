"""
History routes for retrieving user scan history.
"""
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.sql_models import Scan, ChatMessage, User
from ..utils.auth_middleware import require_auth
import logging

history_bp = Blueprint('history', __name__)
logger = logging.getLogger(__name__)

@history_bp.route('/history', methods=['GET'])
@require_auth
def get_user_history(current_user):
    """
    Get all scans for the authenticated user.
    
    Returns:
        JSON list of scans with basic info
    """
    try:
        db: Session = next(get_db())
        
        # Get all scans for this user
        scans = db.query(Scan).filter(
            Scan.user_id == current_user['uid']
        ).order_by(Scan.created_at.desc()).all()
        
        result = []
        for scan in scans:
            result.append({
                "scanId": scan.scan_id,
                "timestamp": scan.created_at.isoformat(),
                "skinType": scan.skin_type_result.get('type') if scan.skin_type_result else None,
                "skinIssues": scan.skin_issues_result if scan.skin_issues_result else [],
                "demographics": scan.demographics_result if scan.demographics_result else {}
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error getting user history: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve history'}), 500

@history_bp.route('/history/<scan_id>', methods=['GET'])
@require_auth
def get_scan_details(current_user, scan_id):
    """
    Get details and chat history for a specific scan.
    
    Args:
        scan_id: The scan ID to retrieve
        
    Returns:
        JSON with scan details and chat messages
    """
    try:
        db: Session = next(get_db())
        
        # Get the scan
        scan = db.query(Scan).filter(
            Scan.scan_id == scan_id,
            Scan.user_id == current_user['uid']
        ).first()
        
        if not scan:
            return jsonify({'error': 'Scan not found'}), 404
        
        # Get chat messages
        messages = db.query(ChatMessage).filter(
            ChatMessage.scan_id == scan_id
        ).order_by(ChatMessage.timestamp).all()
        
        result = {
            "scanId": scan.scan_id,
            "timestamp": scan.created_at.isoformat(),
            "skinResults": {
                "skinType": scan.skin_type_result,
                "skinIssues": scan.skin_issues_result,
                "demographics": scan.demographics_result
            },
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in messages
            ]
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error getting scan details: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve scan details'}), 500
