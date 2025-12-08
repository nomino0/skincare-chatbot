"""
Admin routes for professional labeling and data management.
"""
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.sql_models import Scan, ProfessionalLabel, User
from ..utils.auth_middleware import require_auth, check_admin
import logging
from firebase_admin import auth
import json
import os

admin_bp = Blueprint('admin', __name__)
logger = logging.getLogger(__name__)

@admin_bp.route('/admin/stats', methods=['GET'])
@require_auth
def get_admin_stats(current_user):
    """
    Get dashboard statistics.
    """
    if not check_admin(current_user):
        return jsonify({'error': 'Unauthorized'}), 403
        
    try:
        db: Session = next(get_db())
        
        # Database Stats
        total_users = db.query(User).count()
        total_scans = db.query(Scan).count()
        total_professionals = db.query(User).filter(User.role == 'professional').count()
        labeled_scans = db.query(ProfessionalLabel).count()
        
        # Model Metrics
        metrics = {}
        metrics_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'metrics.json')
        if os.path.exists(metrics_path):
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)
                
        # Model Params
        params = {}
        # params_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'params.yaml')
        # if os.path.exists(params_path):
        #     with open(params_path, 'r') as f:
        #         # params = yaml.safe_load(f)
        #         pass

        return jsonify({
            'users': {
                'total': total_users,
                'professionals': total_professionals
            },
            'scans': {
                'total': total_scans,
                'labeled': labeled_scans
            },
            'model': {
                'metrics': metrics,
                'params': params,
                'version': 'v1.0.0' # Placeholder, could be read from a version file
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve stats'}), 500

@admin_bp.route('/admin/create-professional', methods=['POST'])
@require_auth
def create_professional(current_user):
    """
    Create a new professional account.
    Only accessible to admins.
    """
    if not check_admin(current_user):
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        display_name = data.get('displayName')
        
        if not email or not password or not display_name:
            return jsonify({'error': 'Missing required fields'}), 400

        # Create user in Firebase
        try:
            user = auth.create_user(
                email=email,
                password=password,
                display_name=display_name
            )
        except Exception as e:
            error_msg = str(e)
            if "default credentials" in error_msg or "credential" in error_msg.lower():
                logger.error("Firebase Admin SDK missing service account credentials.")
                return jsonify({
                    'error': 'Server configuration error: Missing Firebase Service Account credentials. Please ask the administrator to configure FIREBASE_ADMIN_CREDENTIALS.'
                }), 500
            return jsonify({'error': f'Firebase error: {error_msg}'}), 400

        # Set custom claims
        auth.set_custom_user_claims(user.uid, {'role': 'professional'})
        
        # Add to SQL database
        db: Session = next(get_db())
        
        # Check if user exists in DB
        existing_user = db.query(User).filter(User.firebase_uid == user.uid).first()
        if not existing_user:
            new_user = User(
                firebase_uid=user.uid,
                email=email,
                role='professional'
            )
            db.add(new_user)
            db.commit()
        
        return jsonify({'message': 'Professional account created successfully', 'uid': user.uid}), 201

    except Exception as e:
        logger.error(f"Error creating professional: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/submissions', methods=['GET'])
@require_auth
def get_submissions(current_user):
    """
    Get all scans for professional labeling.
    Only accessible to admins.
    
    Query params:
        status: 'pending' or 'labeled'
        limit: Number of results (default 50)
    """
    if not check_admin(current_user):
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        db: Session = next(get_db())
        
        status = request.args.get('status', 'pending')
        limit = int(request.args.get('limit', 50))
        
        query = db.query(Scan)
        
        if status == 'pending':
            # Get scans without labels
            query = query.outerjoin(ProfessionalLabel).filter(
                ProfessionalLabel.id == None
            )
        elif status == 'labeled':
            # Get scans with labels
            query = query.join(ProfessionalLabel)
        
        scans = query.order_by(Scan.created_at.desc()).limit(limit).all()
        
        result = []
        for scan in scans:
            result.append({
                "scanId": scan.scan_id,
                "userId": scan.user_id,
                "timestamp": scan.created_at.isoformat(),
                "imagePath": scan.image_path,
                "prediction": {
                    "skinType": scan.skin_type_result,
                    "skinIssues": scan.skin_issues_result,
                    "demographics": scan.demographics_result
                },
                "hasLabel": scan.professional_label is not None
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error getting submissions: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve submissions'}), 500

@admin_bp.route('/admin/label', methods=['POST'])
@require_auth
def submit_label(current_user):
    """
    Submit a professional label for a scan.
    Only accessible to admins.
    
    Expected JSON:
    {
        "scanId": "...",
        "verifiedSkinType": "Oily",
        "verifiedIssues": ["Acne", "Redness"],
        "notes": "..."
    }
    """
    if not check_admin(current_user):
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        
        if not data or 'scanId' not in data:
            return jsonify({'error': 'Missing scanId'}), 400
        
        db: Session = next(get_db())
        
        # Check if scan exists
        scan = db.query(Scan).filter(Scan.scan_id == data['scanId']).first()
        if not scan:
            return jsonify({'error': 'Scan not found'}), 404
        
        # Check if label already exists
        existing_label = db.query(ProfessionalLabel).filter(
            ProfessionalLabel.scan_id == data['scanId']
        ).first()
        
        if existing_label:
            # Update existing label
            existing_label.verified_skin_type = data.get('verifiedSkinType')
            existing_label.verified_issues = data.get('verifiedIssues', [])
            existing_label.notes = data.get('notes', '')
            existing_label.labeled_by = current_user['uid']
        else:
            # Create new label
            new_label = ProfessionalLabel(
                scan_id=data['scanId'],
                verified_skin_type=data.get('verifiedSkinType'),
                verified_issues=data.get('verifiedIssues', []),
                notes=data.get('notes', ''),
                labeled_by=current_user['uid']
            )
            db.add(new_label)
        
        db.commit()
        
        return jsonify({'message': 'Label submitted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error submitting label: {e}", exc_info=True)
        return jsonify({'error': 'Failed to submit label'}), 500

@admin_bp.route('/admin/users', methods=['GET'])
@require_auth
def get_users(current_user):
    """
    Get all users.
    Only accessible to admins.
    """
    if not check_admin(current_user):
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        from ..models.sql_models import User
        db: Session = next(get_db())
        
        users = db.query(User).all()
        result = []
        for u in users:
            result.append({
                'uid': u.firebase_uid,
                'email': u.email,
                'role': u.role,
                'optOutDataCollection': bool(u.opt_out_data_collection),
                'createdAt': u.created_at.isoformat() if u.created_at else None
            })
        
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error listing users: {e}", exc_info=True)
        return jsonify({'error': 'Failed to list users'}), 500

@admin_bp.route('/admin/users/role', methods=['POST'])
@require_auth
def admin_update_user_role(current_user):
    """
    Update another user's role.
    Only accessible to admins.
    
    Expected JSON:
    {
        "targetUid": "...",
        "role": "professional"
    }
    """
    if not check_admin(current_user):
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        target_uid = data.get('targetUid')
        new_role = data.get('role')
        
        if not target_uid or not new_role:
             return jsonify({'error': 'Missing targetUid or role'}), 400
             
        if new_role not in ['user', 'professional', 'admin']:
            return jsonify({'error': 'Invalid role'}), 400
            
        from ..models.sql_models import User
        db: Session = next(get_db())
        
        user = db.query(User).filter(User.firebase_uid == target_uid).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        user.role = new_role
        db.commit()
        
        return jsonify({'message': f'Updated user {user.email} role to {new_role}'}), 200
        
    except Exception as e:
        logger.error(f"Error updating user role: {e}", exc_info=True)
        return jsonify({'error': 'Failed to update user role'}), 500
