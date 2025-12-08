import os
import json
import logging

logger = logging.getLogger(__name__)

def setup_firebase_credentials():
    """
    Setup Firebase credentials from environment variable if file doesn't exist.
    This is useful for cloud deployments where we can't easily mount files.
    """
    cred_path = os.environ.get('FIREBASE_ADMIN_CREDENTIALS', 'serviceAccountKey.json')
    
    # If file exists, we're good
    if os.path.exists(cred_path):
        return

    # If not, check if we have the JSON content in an env var
    cred_json = os.environ.get('FIREBASE_CREDENTIALS_JSON')
    if cred_json:
        try:
            # Validate JSON
            json.loads(cred_json)
            
            # Write to file
            with open(cred_path, 'w') as f:
                f.write(cred_json)
            logger.info(f"Created {cred_path} from FIREBASE_CREDENTIALS_JSON")
        except Exception as e:
            logger.error(f"Failed to create credentials file: {e}")
