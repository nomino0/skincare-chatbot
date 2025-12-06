"""
Admin routes for professional labeling and data management.
"""
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.sql_models import Scan, ProfessionalLabel
from ..utils.auth_middleware import require_auth, check_admin
import logging

admin_bp = Blueprint('admin', __name__)
logger = logging.getLogger(__name__)

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
