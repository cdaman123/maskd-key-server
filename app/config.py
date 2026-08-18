import os
import base64


class Config:
    # Flask Session Secret
    SECRET_KEY = os.environ.get(
        "FLASK_SECRET_KEY", "super-secret-session-key-change-in-prod"
    )

    # The shared secret used to verify the HMAC signature from the client
    APP_SECRET = os.environ.get(
        "APP_SECRET", "default-dev-app-secret-do-not-use-in-prod"
    )

    # The actual AES key for model decryption (base64 encoded)
    MODEL_DECRYPTION_KEY_B64 = os.environ.get(
        "MODEL_DECRYPTION_KEY_B64", "MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY="
    )

    # Max allowed time difference for timestamp validation (seconds)
    MAX_TIMESTAMP_DRIFT = int(os.environ.get("MAX_TIMESTAMP_DRIFT", 30))

    # PostgreSQL Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://maskd_user:maskd_pass@db:5432/maskd_keys"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Admin Panel Credentials
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

    @classmethod
    def get_model_key_bytes(cls) -> bytes:
        return base64.b64decode(cls.MODEL_DECRYPTION_KEY_B64, validate=True)
