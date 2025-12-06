"""
Firebase authentication middleware.
"""
from functools import wraps
from flask import request, jsonify
import firebase_admin
from firebase_admin import credentials, auth
import os
import logging

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
_firebase_initialized = False

def init_firebase_admin():
    """Initialize Firebase Admin SDK."""
    global _firebase_initialized
    
    if _firebase_initialized:
        return
    
    try:
        # Check if credentials file exists
        cred_path = os.environ.get('FIREBASE_ADMIN_CREDENTIALS')
        
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin initialized with credentials file")
        else:
            # Try to initialize with default credentials
            firebase_admin.initialize_app()
            logger.info("Firebase Admin initialized with default credentials")
        
        _firebase_initialized = True
    except Exception as e:
        logger.warning(f"Firebase Admin initialization failed: {e}")
        logger.warning("Authentication will not work properly")

def require_auth(f):
    """
    Decorator to require Firebase authentication.
    Extracts and verifies the Firebase ID token from the Authorization header.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get the token from the Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'No authorization header'}), 401
        
        # Extract the token (format: "Bearer <token>")
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({'error': 'Invalid authorization header format'}), 401
        
        # Verify the token
        try:
            if not _firebase_initialized:
                init_firebase_admin()
            
            decoded_token = auth.verify_id_token(token)
            current_user = {
                'uid': decoded_token['uid'],
                'email': decoded_token.get('email'),
                'email_verified': decoded_token.get('email_verified', False)
            }
            
            # Pass the user info to the route
            return f(current_user, *args, **kwargs)
            
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return jsonify({'error': 'Invalid or expired token'}), 401
    
    return decorated_function

def check_admin(current_user):
    """
    Check if the current user is an admin.
    For now, this is a simple whitelist. In production, use custom claims.
    """
    admin_emails = os.environ.get('ADMIN_EMAILS', '').split(',')
    return current_user.get('email') in admin_emails
