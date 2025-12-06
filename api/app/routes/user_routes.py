"""
User routes for profile and role management.
"""

from flask import Blueprint, request, jsonify, g
from ..utils.auth_middleware import require_auth
from ..database import SessionLocal
from ..models.sql_models import User
import logging

user_bp = Blueprint('user', __name__)
logger = logging.getLogger(__name__)

@user_bp.route('/user/profile', methods=['GET'])
@require_auth
def get_user_profile():
    """
    Get current user profile and role.
    Creates user if not exists.
    """
    try:
        firebase_uid = g.user['uid']
        email = g.user.get('email')
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
            
            if not user:
                # Create new user
                user = User(
                    firebase_uid=firebase_uid,
                    email=email,
                    role='user'  # Default role
                )
                db.add(user)
                db.commit()
                logger.info(f"Created new user: {email}")
            
            return jsonify({
                'uid': user.firebase_uid,
                'email': user.email,
                'role': user.role,
                'optOutDataCollection': bool(user.opt_out_data_collection),
                'createdAt': user.created_at.isoformat() if user.created_at else None
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error fetching user profile: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch profile'}), 500

@user_bp.route('/user/profile', methods=['PUT'])
@require_auth
def update_user_profile():
    """
    Update user profile settings (e.g. opt-out).
    """
    try:
        firebase_uid = g.user['uid']
        data = request.get_json()
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if 'optOutDataCollection' in data:
                user.opt_out_data_collection = 1 if data['optOutDataCollection'] else 0
                
            db.commit()
            return jsonify({
                'message': 'Profile updated',
                'optOutDataCollection': bool(user.opt_out_data_collection)
            }), 200
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error updating profile: {e}", exc_info=True)
        return jsonify({'error': 'Failed to update profile'}), 500


@user_bp.route('/user/role', methods=['POST'])
@require_auth
def update_user_role():
    """
    Update user role (Admin only - simplified for demo).
    In production, this should be strictly protected.
    """
    try:
        from flask import current_app
        # For demo purposes, allow self-promotion if secret key provided
        data = request.get_json()
        secret = data.get('secret')
        new_role = data.get('role')
        
        if not new_role in ['user', 'professional', 'admin']:
            return jsonify({'error': 'Invalid role'}), 400
            
        # Use configured secret
        admin_secret = current_app.config.get('ADMIN_SECRET_KEY')
        if secret != admin_secret:
             return jsonify({'error': 'Unauthorized'}), 403
             
        firebase_uid = g.user['uid']
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
            if user:
                user.role = new_role
                db.commit()
                return jsonify({'message': f'Role updated to {new_role}'}), 200
            return jsonify({'error': 'User not found'}), 404
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error updating role: {e}")
        return jsonify({'error': 'Failed to update role'}), 500
