from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import uuid

db = SQLAlchemy()


class ApiKey(db.Model):
    __tablename__ = "api_keys"

    id = db.Column(db.Integer, primary_key=True)
    # Generate a random UUID as the default API key
    key_string = db.Column(
        db.String(128), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<ApiKey {self.key_string}>"
