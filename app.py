# app.py
import os
import json
import time
import traceback
import wave
from os import getenv
from Attacks.parallel_attack import parallel_bruteforce, parallel_dictionary_attack as external_parallel_attack


from dotenv import load_dotenv
from flask import (
    Flask, render_template, request, jsonify, session,
    redirect, url_for, send_file
)
from flask_cors import CORS

from backend.auth_service import AuthService
from backend.message_service import MessageService
from backend.crypto_service import CryptoService
from backend.stego_service import StegoService
from backend.password_attack_service import PasswordAttackService

# Load .env
load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_dev_secret_key')

# Configure upload folder for audio files
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav'}
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure attack-related defaults (can be overridden via app.config or .env)
# e.g. in .env: ATTACK_TIMEOUT=120, ATTACK_MAX_BRUTE_LENGTH=6
app.config['ATTACK_TIMEOUT'] = int(os.getenv('ATTACK_TIMEOUT', '120'))
app.config['ATTACK_MAX_BRUTE_LENGTH'] = int(os.getenv('ATTACK_MAX_BRUTE_LENGTH', '6'))

# Initialize services
auth_service = AuthService()
crypto_service = CryptoService()
message_service = MessageService(crypto_service=crypto_service)
stego_service = StegoService()

# Use the Attacks folder default wordlist for the password attack service
default_wordlist = os.path.join(os.getcwd(), 'Attacks', 'worldlist5.txt')
password_attack_service = PasswordAttackService(wordlist_path=default_wordlist)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------
# Basic pages and endpoints
# ---------------------------

@app.route('/')
def index():
    # Clear session when accessing landing page
    session.clear()
    return render_template('landing.html')


@app.route('/auth')
def auth():
    # Clear session to force fresh login
    session.clear()
    return render_template('auth.html')


@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('auth'))
    return render_template('home.html', user=session['user'])


@app.route('/algorithms')
def algorithms():
    if 'user' not in session:
        return redirect(url_for('auth'))
    return render_template('algorithms.html', user=session['user'])


@app.route('/messages')
def messages_page():
    if 'user' not in session:
        return redirect(url_for('auth'))
    return render_template('messages.html', user=session['user'])


@app.route('/conversation/<int:other_user_id>')
def conversation(other_user_id):
    if 'user' not in session:
        return redirect(url_for('auth'))
    return render_template('conversation.html', user=session['user'], other_user_id=other_user_id)


@app.route('/encryption/<algorithm>')
def encrypt_page(algorithm):
    if 'user' not in session:
        return redirect(url_for('auth'))
    return render_template('encryption.html', user=session['user'], algorithm=algorithm)


@app.route('/steganography')
def steganography_page():
    if 'user' not in session:
        return redirect(url_for('auth'))
    return render_template('steganography.html', user=session['user'])


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# ---------------------------
# Auth API
# ---------------------------

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required"}), 400

    result = auth_service.sign_up(username, password)

    if result['success']:
        session['user'] = result['user']
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@app.route('/api/auth/signin', methods=['POST'])
def signin():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required"}), 400

    result = auth_service.sign_in(username, password)

    if result.get('success'):
        session['user'] = result['user']
        return jsonify(result), 200

    msg = (result.get('message') or '').lower()
    if "verrouill" in msg or "locked" in msg:
        return jsonify(result), 423  # account locked
    return jsonify(result), 401       # bad password


@app.route('/api/users', methods=['GET'])
def get_users():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    users = auth_service.get_all_users()
    return jsonify({"success": True, "users": users}), 200


# ---------------------------
# Messaging & Crypto APIs
# ---------------------------

@app.route('/api/messages/send', methods=['POST'])
def send_message():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    data = request.json
    message_text = data.get('message')
    algo_name = data.get('algo_name')
    receiver_id = data.get('receiver_id')
    key_params = data.get('key_params', {})

    sender_id = session['user']['id']

    if not all([message_text, algo_name, receiver_id]):
        return jsonify({"success": False, "message": "Message, algorithm, and receiver ID are required"}), 400

    try:
        encrypted = crypto_service.encrypt_message(message_text, algo_name, key_params)
        algorithm_key = json.dumps(key_params) if key_params else None

        result = message_service.send_message(
            sender_id,
            receiver_id,
            encrypted,
            algo_name,
            algorithm_key
        )

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/messages/conversation/<int:other_user_id>', methods=['GET'])
def get_conversation(other_user_id):
    if 'user' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    user_id = session['user']['id']
    result = message_service.get_conversation(user_id, other_user_id)
    return jsonify(result), 200


@app.route('/api/messages/all', methods=['GET'])
def get_all_messages():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    user_id = session['user']['id']
    result = message_service.get_all_conversations(user_id)
    return jsonify(result), 200


@app.route('/api/crypto/encrypt', methods=['POST'])
def encrypt():
    data = request.json
    message = data.get('message')
    algorithm = data.get('algorithm')
    key_params = data.get('key_params', {})

    if not message or not algorithm:
        return jsonify({"success": False, "message": "Message and algorithm are required"}), 400

    try:
        encrypted = crypto_service.encrypt_message(message, algorithm, key_params)
        return jsonify({"success": True, "encrypted": encrypted}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/crypto/decrypt', methods=['POST'])
def decrypt():
    data = request.json
    encrypted_message = data.get('encrypted_message')
    algorithm = data.get('algorithm')
    key_params = data.get('key_params', {})

    if not encrypted_message or not algorithm:
        return jsonify({"success": False, "message": "Encrypted message and algorithm are required"}), 400

    try:
        decrypted = crypto_service.decrypt_message(encrypted_message, algorithm, key_params)
        return jsonify({"success": True, "decrypted": decrypted}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ---------------------------
# Steganography endpoints
# ---------------------------

@app.route('/api/stego/send', methods=['POST'])
def send_stego_message():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    if 'audio_file' not in request.files:
        return jsonify({"success": False, "message": "No audio file provided"}), 400

    file = request.files['audio_file']
    secret_message = request.form.get('secret_message')
    receiver_id = request.form.get('receiver_id')

    if not file or not secret_message or not receiver_id:
        return jsonify({"success": False, "message": "Audio file, message, and receiver are required"}), 400
    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"success": False, "message": "Only WAV files are allowed"}), 400

    temp_path = None  # For cleanup

    try:
        sender_id = session['user']['id']

        # Create a temp file
        timestamp = int(time.time() * 1000)  # milliseconds for uniqueness
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f'temp{sender_id}{timestamp}.wav')
        file.save(temp_path)

        # Validate WAV file (with context manager to auto-close)
        try:
            with wave.open(temp_path, 'rb') as wav:
                frames = wav.getnframes()
                rate = wav.getframerate()
                duration = frames / float(rate)
                print(f"Audio file validated: {duration:.2f} seconds, {frames} frames")

                # Check capacity
                message_bits = len(secret_message + "###END###") * 8
                if frames < message_bits:
                    return jsonify({
                        "success": False,
                        "message": f"Audio trop court ! Besoin de {message_bits} échantillons, l'audio en a {frames}."
                    }), 400
        except wave.Error as e:
            return jsonify({"success": False, "message": f"Fichier WAV invalide: {str(e)}"}), 400

        # Small delay on Windows to allow file lock release
        time.sleep(0.1)

        # Process with stego service
        result = stego_service.hide_message_and_save_from_temp(
            temp_path, secret_message, sender_id, receiver_id, app.config['UPLOAD_FOLDER']
        )

        return jsonify(result), 200

    except Exception as e:
        print(f"Error in stego send: {str(e)}")
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        # Cleanup temp file in all cases
        if temp_path and os.path.exists(temp_path):
            try:
                time.sleep(0.2)
                os.remove(temp_path)
                print(f"✅ Fichier temporaire supprimé : {temp_path}")
            except Exception as e:
                print(f"⚠️ Impossible de supprimer le fichier temporaire : {e}")


@app.route('/api/stego/messages', methods=['GET'])
def get_stego_messages():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    user_id = session['user']['id']
    result = stego_service.get_user_messages(user_id)
    return jsonify(result), 200


@app.route('/api/stego/decrypt/<int:message_id>', methods=['GET'])
def decrypt_stego_message(message_id):
    if 'user' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    user_id = session['user']['id']
    result = stego_service.decrypt_message(message_id, user_id, app.config['UPLOAD_FOLDER'])
    return jsonify(result), 200


@app.route('/api/stego/audio/<filename>')
def serve_audio(filename):
    if 'user' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(
                file_path,
                mimetype='audio/wav',
                as_attachment=False,
                download_name=filename,
                conditional=True,
                max_age=0
            )
        else:
            return jsonify({"success": False, "message": "File not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ========================================================================
# ATTACK UI ROUTE (shows/hides attack page based on ALLOW_ATTACKS)
# ========================================================================
@app.route('/attack_auth')
def attack_auth_page():
    """Password attack page (no login required for educational/testing purposes)"""
    session.clear()
    allow = getenv('ALLOW_ATTACKS', 'false').lower() == 'true'
    return render_template('attack_auth.html', allow_attacks=allow)


# Helper: gate attack endpoints (returns a Flask response if blocked, else None)
def attacks_allowed_or_abort():
    if getenv('ALLOW_ATTACKS', 'false').lower() != 'true':
        return jsonify({"success": False, "message": "Attacks disabled on this server."}), 403
    # restrict to localhost to be extra safe
    if request.remote_addr not in ('127.0.0.1', '::1'):
        return jsonify({"success": False, "message": "Attack endpoint only allowed from localhost."}), 403
    return None


# ========================================================================
# PASSWORD ATTACK API (start attack)
# ========================================================================
@app.route('/api/attack_auth/check-user', methods=['POST'])
def check_user_exists_auth():
    data = request.json
    username = data.get('username')

    if not username:
        return jsonify({"success": False, "message": "Username required"}), 400

    try:
        result = auth_service.supabase.table('users').select('id, username').eq('username', username).execute()
        exists = len(result.data) > 0 if result.data else False
        return jsonify({"success": True, "exists": exists, "user": result.data[0] if exists else None}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/attack_auth/start', methods=['POST'])
def start_attack_auth():
    """
    Start a password attack on a user account (safe: only when ALLOW_ATTACKS=true and from localhost)
    Supports:
      - 'dictionary3'  => dictionary3_attack
      - 'bruteforce5'  => brute force 5-char attack (using non-parallel version)
      - 'bruteforce6'  => brute force 6-char attack
    """
    # Safety gate
    blocked = attacks_allowed_or_abort()
    if blocked is not None:
        return blocked

    data = request.json
    username = data.get('username')
    method = data.get('method')  # 'dictionary3', 'bruteforce5', 'bruteforce6'
    confirm = data.get('confirm', False)

    if not username or not method:
        return jsonify({"success": False, "message": "Username and method required"}), 400
    if not confirm:
        return jsonify({"success": False, "message": "You must set 'confirm': true in the request body to run attacks."}), 400

    try:
        # Get user's stored hash and salt
        result = auth_service.supabase.table('users').select('*').eq('username', username).execute()
        if not result.data:
            return jsonify({"success": False, "message": "User not found"}), 404

        user = result.data[0]
        stored_hash = user.get('password_hash')
        salt = user.get('password_salt')

        print("\n" + "="*60)
        print(f"PASSWORD ATTACK REQUEST: {username} via {method}")
        print("="*60 + "\n")

        attack_result = None

        if method == "dictionary3":
            attack_result = password_attack_service.dictionary3_attack(stored_hash, salt, username)
        elif method == "bruteforce5":
            # The parallel version has internal queueing that continues processing
            # even after finding the password. Sequential version stops immediately.
            attack_result = password_attack_service.brute_force_attack(stored_hash, salt, username, length=5)
        elif method == "bruteforce6":
            attack_result = password_attack_service.brute_force_attack(stored_hash, salt, username, length=6)
        else:
            return jsonify({"success": False, "message": f"Unknown attack method: {method}"}), 400

        attack_result = attack_result or {}
        attempts = attack_result.get('attempts', attack_result.get('processed', 0))
        found = attack_result.get('success', attack_result.get('found', False))
        password = attack_result.get('password')

        response_data = {
            "success": True,
            "message": f"Attack completed with {method} method",
            "found": found,
            "password": password,
            "attempts": attempts,
            "processed": attempts,
            "total": attack_result.get('total', 0),
            "duration": attack_result.get('duration', 0),
            "method": attack_result.get('method', method)
        }

        print(f"[RESULT] Found: {found}, Password: {password}, Attempts: {attempts}, Duration: {response_data['duration']:.3f}s")
        return jsonify(response_data), 200

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print("[ERROR] Password attack failed:\n", error_trace)
        return jsonify({"success": False, "message": f"Attack failed: {str(e)}"}), 500


# ---------------------------
# Run server
# ---------------------------
if __name__ == '__main__':
    print("=" * 60)
    print("Cryptography Toolkit - Web Application")
    print("=" * 60)
    print("Server starting on http://localhost:5000")
    print("Open your browser and navigate to: http://localhost:5000")
    print("=" * 60)
    print("\nAvailable Features:")
    print("  - /auth         : User authentication")
    print("  - /attack_auth  : Password attacks (educational) (only when ALLOW_ATTACKS=true)")
    print("=" * 60)
    print()
    app.run(debug=True, port=5000, host='0.0.0.0')
