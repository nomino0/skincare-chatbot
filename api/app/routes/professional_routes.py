"""
Professional Portal Routes for dermatologists and skin care professionals.
Provides access to scans for review, labeling, and active learning feedback.
"""

from flask import Blueprint, request, jsonify, current_app, send_file
from datetime import datetime
import logging
import os

professional_bp = Blueprint('professional', __name__)
logger = logging.getLogger(__name__)


@professional_bp.route('/scans', methods=['GET'])
def get_all_scans():
    """
    Get all scans for professional review.
    
    Query params:
    - status: 'pending', 'labeled', 'all' (default: 'pending')
    - limit: number of scans to return (default: 50)
    - offset: pagination offset (default: 0)
    
    Returns:
        List of scans with AI predictions (no user info)
    """
    try:
        from ..database import SessionLocal
        from ..models.sql_models import Scan, ProfessionalLabel
        
        status = request.args.get('status', 'pending')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        db = SessionLocal()
        try:
            query = db.query(Scan)
            
            if status == 'pending':
                # Scans without labels
                query = query.outerjoin(ProfessionalLabel).filter(ProfessionalLabel.id == None)
            elif status == 'labeled':
                # Scans with labels
                query = query.join(ProfessionalLabel)
            # 'all' returns everything
            
            total = query.count()
            scans = query.order_by(Scan.created_at.desc()).offset(offset).limit(limit).all()
            
            result = []
            for scan in scans:
                result.append({
                    'scanId': scan.scan_id,
                    'timestamp': scan.created_at.isoformat() if scan.created_at else None,
                    'imagePath': scan.image_path,
                    'aiPrediction': {
                        'skinType': scan.skin_type_result,
                        'skinIssues': scan.skin_issues_result,
                        'demographics': scan.demographics_result
                    },
                    'hasLabel': scan.professional_label is not None,
                    'label': {
                        'verifiedSkinType': scan.professional_label.verified_skin_type,
                        'verifiedIssues': scan.professional_label.verified_issues,
                        'aiWasCorrect': scan.professional_label.ai_was_correct,
                        'notes': scan.professional_label.notes
                    } if scan.professional_label else None
                })
            
            return jsonify({
                'scans': result,
                'total': total,
                'limit': limit,
                'offset': offset
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error fetching scans: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch scans'}), 500


@professional_bp.route('/scans/<scan_id>', methods=['GET'])
def get_scan_detail(scan_id):
    """
    Get detailed view of a single scan with image.
    
    Returns:
        Scan details including base64 image
    """
    try:
        from ..database import SessionLocal
        from ..models.sql_models import Scan
        import base64
        
        db = SessionLocal()
        try:
            scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()
            
            if not scan:
                return jsonify({'error': 'Scan not found'}), 404
            
            # Read image if exists
            image_base64 = None
            if scan.image_path and os.path.exists(scan.image_path):
                with open(scan.image_path, 'rb') as f:
                    image_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            return jsonify({
                'scanId': scan.scan_id,
                'timestamp': scan.created_at.isoformat() if scan.created_at else None,
                'imageBase64': image_base64,
                'aiPrediction': {
                    'skinType': scan.skin_type_result,
                    'skinIssues': scan.skin_issues_result,
                    'demographics': scan.demographics_result
                },
                'label': {
                    'verifiedSkinType': scan.professional_label.verified_skin_type,
                    'verifiedIssues': scan.professional_label.verified_issues,
                    'aiWasCorrect': scan.professional_label.ai_was_correct,
                    'notes': scan.professional_label.notes
                } if scan.professional_label else None
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error fetching scan: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch scan'}), 500


@professional_bp.route('/scans/<scan_id>/label', methods=['POST'])
def label_scan(scan_id):
    """
    Submit professional label for a scan.
    
    Expected JSON body:
    {
        "verifiedSkinType": "Oily",
        "verifiedIssues": ["Acne", "Redness"],
        "aiWasCorrect": false,
        "notes": "Moderate acne visible"
    }
    """
    try:
        from ..database import SessionLocal
        from ..models.sql_models import Scan, ProfessionalLabel
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        db = SessionLocal()
        try:
            scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()
            
            if not scan:
                return jsonify({'error': 'Scan not found'}), 404
            
            # Check if already labeled
            existing_label = db.query(ProfessionalLabel).filter(
                ProfessionalLabel.scan_id == scan.id
            ).first()
            
            if existing_label:
                # Update existing label
                existing_label.verified_skin_type = data.get('verifiedSkinType')
                existing_label.verified_issues = data.get('verifiedIssues', [])
                existing_label.ai_was_correct = data.get('aiWasCorrect', False)
                existing_label.notes = data.get('notes', '')
                existing_label.updated_at = datetime.utcnow()
            else:
                # Create new label
                label = ProfessionalLabel(
                    scan_id=scan.id,
                    professional_id="professional_1",  # TODO: Get from auth
                    verified_skin_type=data.get('verifiedSkinType'),
                    verified_issues=data.get('verifiedIssues', []),
                    ai_was_correct=data.get('aiWasCorrect', False),
                    notes=data.get('notes', '')
                )
                db.add(label)
            
            db.commit()
            
            logger.info(f"Professional label saved for scan {scan_id}")
            return jsonify({'message': 'Label saved successfully'}), 200
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error labeling scan: {e}", exc_info=True)
        return jsonify({'error': 'Failed to save label'}), 500


@professional_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get statistics about scans and labels for dashboard.
    
    Returns:
        Statistics about AI accuracy, common corrections, etc.
    """
    try:
        from ..database import SessionLocal
        from ..models.sql_models import Scan, ProfessionalLabel
        from sqlalchemy import func
        
        db = SessionLocal()
        try:
            total_scans = db.query(Scan).count()
            labeled_scans = db.query(ProfessionalLabel).count()
            pending_scans = total_scans - labeled_scans
            
            # AI accuracy
            correct_predictions = db.query(ProfessionalLabel).filter(
                ProfessionalLabel.ai_was_correct == True
            ).count()
            
            accuracy = (correct_predictions / labeled_scans * 100) if labeled_scans > 0 else 0
            
            # Skin type distribution (from AI predictions)
            # This is simplified - in production you'd aggregate JSON columns
            
            return jsonify({
                'totalScans': total_scans,
                'labeledScans': labeled_scans,
                'pendingScans': pending_scans,
                'aiAccuracy': round(accuracy, 2),
                'lastUpdated': datetime.utcnow().isoformat()
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error fetching stats: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch stats'}), 500


@professional_bp.route('/export', methods=['GET'])
def export_labeled_data():
    """
    Export labeled data for model retraining.
    
    Returns:
        JSON with all labeled scans for active learning
    """
    try:
        from ..database import SessionLocal
        from ..models.sql_models import Scan, ProfessionalLabel
        
        db = SessionLocal()
        try:
            # Get all labeled scans
            labeled_scans = db.query(Scan).join(ProfessionalLabel).all()
            
            export_data = []
            for scan in labeled_scans:
                export_data.append({
                    'scanId': scan.scan_id,
                    'imagePath': scan.image_path,
                    'aiPrediction': {
                        'skinType': scan.skin_type_result,
                        'skinIssues': scan.skin_issues_result
                    },
                    'professionalLabel': {
                        'skinType': scan.professional_label.verified_skin_type,
                        'issues': scan.professional_label.verified_issues,
                        'aiWasCorrect': scan.professional_label.ai_was_correct
                    },
                    'labeledAt': scan.professional_label.created_at.isoformat()
                })
            
            return jsonify({
                'data': export_data,
                'count': len(export_data),
                'exportedAt': datetime.utcnow().isoformat()
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error exporting data: {e}", exc_info=True)
        return jsonify({'error': 'Failed to export data'}), 500
