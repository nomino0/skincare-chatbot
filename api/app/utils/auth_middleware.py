"""
Firebase authentication middleware.
"""
from functools import wraps
from flask import request, jsonify, current_app
import firebase_admin
from firebase_admin import credentials, auth
import os
import logging
import jwt

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
            # Explicitly set project ID if available in env
            project_id = os.environ.get('NEXT_PUBLIC_FIREBASE_PROJECT_ID') or os.environ.get('GOOGLE_CLOUD_PROJECT')
            if project_id:
                firebase_admin.initialize_app(options={'projectId': project_id})
                logger.info(f"Firebase Admin initialized with project ID: {project_id}")
            else:
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
                'email_verified': decoded_token.get('email_verified', False),
                'role': decoded_token.get('role')
            }
            
            # Pass the user info to the route
            return f(current_user, *args, **kwargs)
            
        except Exception as e:
            # DEVELOPMENT FALLBACK: If verification fails due to missing credentials,
            # and we are in development mode, decode without verification.
            # THIS IS INSECURE AND SHOULD NEVER BE USED IN PRODUCTION.
            error_msg = str(e)
            
            # Check if we are in development mode
            # We check Flask config AND environment variables to be sure
            is_dev = (
                current_app.config.get('ENV') == 'development' or 
                current_app.config.get('DEBUG') == True or
                os.environ.get('FLASK_ENV') == 'development'
            )
            
            # We also check if the error is related to credentials
            is_cred_error = "default credentials" in error_msg or "project ID" in error_msg or "certificate" in error_msg
            
            if is_dev and is_cred_error:
                try:
                    logger.warning("DEVELOPMENT MODE: Bypassing signature verification due to missing credentials.")
                    logger.warning(f"Original error: {error_msg}")
                    
                    # Decode without verification
                    decoded_token = jwt.decode(token, options={"verify_signature": False})
                    
                    current_user = {
                        'uid': decoded_token['user_id'], # Firebase uses user_id in payload
                        'email': decoded_token.get('email'),
                        'email_verified': decoded_token.get('email_verified', False)
                    }
                    return f(current_user, *args, **kwargs)
                except Exception as decode_error:
                    logger.error(f"Fallback decoding failed: {decode_error}")
            
            logger.error(f"Token verification failed: {e}")
            return jsonify({'error': 'Invalid or expired token'}), 401
    
    return decorated_function

def check_admin(current_user):
    """
    Check if the current user is an admin.
    Checks environment variables whitelist and custom claims.
    """
    # Check env vars
    admin_emails = [e.strip() for e in os.environ.get('ADMIN_EMAILS', '').split(',') if e.strip()]
    if os.environ.get('ADMIN_EMAIL'):
        admin_emails.append(os.environ.get('ADMIN_EMAIL'))
    
    if current_user.get('email') in admin_emails:
        logger.info(f"Admin access granted via whitelist: {current_user.get('email')}")
        return True
        
    # Check role claim
    if current_user.get('role') == 'admin':
        logger.info(f"Admin access granted via role claim: {current_user.get('email')}")
        return True
        
    logger.warning(f"Admin access denied for: {current_user.get('email')}")
    return False
