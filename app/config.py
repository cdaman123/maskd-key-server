import os
import base64

class Config:
    # The shared secret used to verify the HMAC signature from the client
    APP_SECRET = os.environ.get("APP_SECRET", "default-dev-app-secret-do-not-use-in-prod")
    
    # The actual AES key for model decryption (base64 encoded)
    # Default is the one used in the client currently: MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY=
    MODEL_DECRYPTION_KEY_B64 = os.environ.get(
        "MODEL_DECRYPTION_KEY_B64", 
        "MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY="
    )
    
    # Max allowed time difference for timestamp validation (seconds)
    MAX_TIMESTAMP_DRIFT = int(os.environ.get("MAX_TIMESTAMP_DRIFT", 30))
    
    @classmethod
    def get_model_key_bytes(cls) -> bytes:
        return base64.b64decode(cls.MODEL_DECRYPTION_KEY_B64, validate=True)
