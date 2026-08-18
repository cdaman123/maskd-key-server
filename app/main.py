import hmac
import hashlib
import time
import logging
from flask import Flask, request, jsonify
from app.config import Config

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_signature(license_key: str, timestamp_str: str, signature: str) -> bool:
    """
    Verifies the HMAC-SHA256 signature.
    The payload is constructed as: timestamp + ":" + license_key
    """
    if not license_key or not timestamp_str or not signature:
        return False
        
    try:
        timestamp = int(timestamp_str)
        current_time = int(time.time())
        
        # Anti-replay: Check if timestamp is within acceptable drift
        if abs(current_time - timestamp) > Config.MAX_TIMESTAMP_DRIFT:
            logger.warning(f"Timestamp drift exceeded: {timestamp} (current: {current_time})")
            return False
            
        payload = f"{timestamp_str}:{license_key}".encode('utf-8')
        secret = Config.APP_SECRET.encode('utf-8')
        
        expected_signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()
        
        # Use compare_digest to prevent timing attacks
        return hmac.compare_digest(expected_signature, signature)
        
    except ValueError:
        logger.warning("Invalid timestamp format.")
        return False
    except Exception as e:
        logger.error(f"Error during signature verification: {e}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/v1/models/key', methods=['POST'])
def get_model_key():
    """
    Endpoint for the maskd client to fetch the model decryption key.
    Requires proper headers for authentication.
    """
    license_key = request.headers.get('X-License-Key')
    timestamp_str = request.headers.get('X-Timestamp')
    signature = request.headers.get('X-Signature')
    
    if not license_key:
        return jsonify({"error": "Missing License Key"}), 401
        
    # TODO: In production, you would validate the license_key against a database here.
    # if not db.is_valid_license(license_key):
    #     return jsonify({"error": "Invalid License Key"}), 403

    if not verify_signature(license_key, timestamp_str, signature):
        logger.warning(f"Unauthorized key fetch attempt for license: {license_key}")
        return jsonify({"error": "Unauthorized"}), 401
        
    logger.info(f"Serving model key to authorized client with license: {license_key}")
    
    # Return the base64 encoded key
    return jsonify({
        "key": Config.MODEL_DECRYPTION_KEY_B64
    }), 200

if __name__ == '__main__':
    # Run the dev server
    app.run(host='0.0.0.0', port=5000)
