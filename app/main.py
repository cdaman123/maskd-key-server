import hmac
import hashlib
import time
import logging
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

from app.config import Config
from app.models import db, ApiKey

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Database
db.init_app(app)

# Setup Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Simple fixed User for Admin Panel
class AdminUser(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id == "admin":
        return AdminUser(user_id)
    return None

# Secure the Admin Panel
class SecuredModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

class SecuredAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

# Initialize Admin Panel
admin = Admin(app, name='Maskd Key Server', template_mode='bootstrap4', index_view=SecuredAdminIndexView())
admin.add_view(SecuredModelView(ApiKey, db.session, name="API Keys"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))
    
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
            user = AdminUser("admin")
            login_user(user)
            return redirect(url_for('admin.index'))
        else:
            error = "Invalid credentials"
            
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

def verify_signature(license_key: str, timestamp_str: str, signature: str) -> bool:
    """Verifies the HMAC-SHA256 signature."""
    if not license_key or not timestamp_str or not signature:
        return False
        
    try:
        timestamp = int(timestamp_str)
        current_time = int(time.time())
        
        # Anti-replay
        if abs(current_time - timestamp) > Config.MAX_TIMESTAMP_DRIFT:
            logger.warning(f"Timestamp drift exceeded: {timestamp} (current: {current_time})")
            return False
            
        payload = f"{timestamp_str}:{license_key}".encode('utf-8')
        secret = Config.APP_SECRET.encode('utf-8')
        
        expected_signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    except Exception as e:
        logger.error(f"Error during signature verification: {e}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/v1/models/key', methods=['POST'])
def get_model_key():
    """Endpoint for the maskd client to fetch the model decryption key."""
    license_key = request.headers.get('X-License-Key')
    timestamp_str = request.headers.get('X-Timestamp')
    signature = request.headers.get('X-Signature')
    
    if not license_key:
        return jsonify({"error": "Missing License Key"}), 401
        
    # Database check for valid License Key
    valid_key = db.session.query(ApiKey).filter_by(key_string=license_key).first()
    if not valid_key:
        logger.warning(f"Failed key fetch attempt: Unknown License Key '{license_key}'")
        return jsonify({"error": "Invalid License Key"}), 403

    # Cryptographic check
    if not verify_signature(license_key, timestamp_str, signature):
        logger.warning(f"Unauthorized key fetch attempt for valid license: {license_key} (Bad Signature)")
        return jsonify({"error": "Unauthorized"}), 401
        
    logger.info(f"Serving model key to authorized client with license: {license_key}")
    
    return jsonify({
        "key": Config.MODEL_DECRYPTION_KEY_B64
    }), 200

# Create DB tables before first request
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
