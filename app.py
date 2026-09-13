from flask import Flask, render_template, request, jsonify, session
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from models.password_analyzer import PasswordAnalyzer
from models.ml_trainer import MLTrainer
from utils.validators import validate_password_input
import hashlib
import secrets
import re
from datetime import datetime
import joblib  # Add this line!

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
CORS(app)

analyzer = PasswordAnalyzer()

# Load ML model
try:
    ml_trainer = MLTrainer()
    ml_trainer.model = joblib.load('models/password_model.pkl')
    print("✅ ML model loaded successfully")
except Exception as e:
    print(f"⚠️ ML model not loaded: {e}")
    ml_trainer = None


app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
CORS(app)

# Initialize the password analyzer
analyzer = PasswordAnalyzer()


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze_password():
    try:
        data = request.get_json()
        password = data.get('password', '')

        if not validate_password_input(password):
            return jsonify({'error': 'Invalid password input'}), 400

        result = analyzer.analyze_password(password)

        # Add ML prediction
        if ml_trainer and ml_trainer.model is not None:
            try:
                ml_result = ml_trainer.predict(password)
                result['ml_prediction'] = ml_result
                result['ml_strength'] = ml_result['label']
                result['ml_confidence'] = ml_result['confidence']
            except Exception as e:
                result['ml_prediction'] = {'error': str(e)}

        result['breach_check'] = check_breach_status(password)
        result['hash'] = hash_password(password)

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        # Get comprehensive analysis

        result = analyzer.analyze_password(password)

        # Add additional security checks
        result['breach_check'] = check_breach_status(password)
        result['hash'] = hash_password(password)

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/generate', methods=['POST'])
def generate_password():
    """
    Generate a strong password
    """
    try:
        data = request.get_json()
        length = data.get('length', 16)

        # Generate strong password
        alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-='
        password = ''.join(secrets.choice(alphabet) for _ in range(length))

        return jsonify({
            'password': password,
            'strength': 'strong'
        })

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/check_breach', methods=['POST'])
def check_breach():
    """
    Check if password has been breached using Have I Been Pwned API
    """
    try:
        data = request.get_json()
        password = data.get('password', '')

        # Simple hash-based check (without sending actual password)
        sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix = sha1[:5]
        suffix = sha1[5:]

        # In production, you'd make an actual API call here
        # For demo, we'll return mock data
        return jsonify({
            'breached': False,
            'count': 0,
            'prefix': prefix,
            'suffix': suffix
        })

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


def hash_password(password):
    """Hash password for storage demonstration"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256()
    hash_obj.update((salt + password).encode())
    return {
        'algorithm': 'SHA-256',
        'hash': hash_obj.hexdigest(),
        'salt': salt
    }


def check_breach_status(password):
    """Check if password appears in breach database"""
    # In production, implement actual API call
    return {
        'checked': True,
        'breached': False,
        'message': 'No breaches found for this password'
    }


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)
