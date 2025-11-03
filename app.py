from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_cors import CORS
from backend.auth_service import AuthService
from backend.message_service import MessageService
from backend.crypto_service import CryptoService
from backend.stego_service import StegoService
from backend.password_attack_service import PasswordAttackService
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
CORS(app)

app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_dev_secret_key')

# Configure upload folder for audio files
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav'}
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize services
auth_service = AuthService()
crypto_service = CryptoService()
message_service = MessageService(crypto_service=crypto_service)
stego_service = StegoService()
password_attack_service = PasswordAttackService(wordlist_path='wordlist.txt')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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

    if result['success']:
        session['user'] = result['user']
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@app.route('/api/users', methods=['GET'])
def get_users():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    users = auth_service.get_all_users()
    return jsonify({"success": True, "users": users}), 200


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

    try:
        sender_id = session['user']['id']
        
        # Validate WAV file before processing
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f'temp_{sender_id}.wav')
        file.save(temp_path)
        
        # Check if it's a valid WAV file
        try:
            import wave
            with wave.open(temp_path, 'rb') as wav:
                frames = wav.getnframes()
                rate = wav.getframerate()
                duration = frames / float(rate)
                print(f"Audio file validated: {duration:.2f} seconds, {frames} frames")
                
                # Ensure audio is long enough for message
                message_bits = len(secret_message + "###END###") * 8
                if frames < message_bits:
                    os.remove(temp_path)
                    return jsonify({
                        "success": False, 
                        "message": f"Audio too short! Need at least {message_bits} samples for this message. Audio has {frames} samples."
                    }), 400
        except wave.Error as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return jsonify({"success": False, "message": f"Invalid WAV file: {str(e)}"}), 400
        
        # Process with steganography
        result = stego_service.hide_message_and_save_from_temp(
            temp_path, secret_message, sender_id, receiver_id, app.config['UPLOAD_FOLDER']
        )
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return jsonify(result), 200
    except Exception as e:
        print(f"Error in stego send: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


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


# ============================================================================
# PASSWORD ATTACK ROUTES (Authentication Attacks)
# ============================================================================

@app.route('/attack_auth')
def attack_auth_page():
    """Password attack page (no login required for educational/testing purposes)"""
    # Clear session for attack mode - don't require login
    session.clear()
    return render_template('attack_auth.html')


@app.route('/api/attack_auth/check-user', methods=['POST'])
def check_user_exists_auth():
    """Check if a username exists in the database"""
    data = request.json
    username = data.get('username')
    
    if not username:
        return jsonify({"success": False, "message": "Username required"}), 400
    
    try:
        # Check if user exists
        result = auth_service.supabase.table('users').select('id, username').eq('username', username).execute()
        
        exists = len(result.data) > 0 if result.data else False
        
        return jsonify({
            "success": True, 
            "exists": exists,
            "user": result.data[0] if exists else None
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/attack_auth/start', methods=['POST'])
def start_attack_auth():
    """
    Start a password attack on a user account
    - Dictionary attack: for 3 and 5 character passwords
    - Brute force attack: for 6 character passwords
    """
    data = request.json
    username = data.get('username')
    method = data.get('method')  # 'dictionary' or 'bruteforce'
    
    if not username or not method:
        return jsonify({"success": False, "message": "Username and method required"}), 400
    
    try:
        # Get user's password hash for verification
        result = auth_service.supabase.table('users').select('*').eq('username', username).execute()
        
        if not result.data:
            return jsonify({"success": False, "message": "User not found"}), 404
        
        user = result.data[0]
        stored_hash = user['password_hash']
        salt = user['password_salt']
        
        print(f"\n{'='*80}")
        print(f"PASSWORD ATTACK REQUEST")
        print(f"{'='*80}")
        print(f"Username: {username}")
        print(f"Method: {method}")
        print(f"Hash: {stored_hash[:40]}...")
        print(f"Salt: {salt}")
        print(f"{'='*80}\n")
        
        # Start attack based on method
        # In app.py, inside the /api/attack_auth route handler

# ... existing code to retrieve user data, stored_hash, salt, and username ...
    
        method = data.get('method')
        attack_result = {}
        
        if method == 'dictionary3':
            # New method for 3-character dictionary
            attack_result = password_attack_service.dictionary3_attack(stored_hash, salt, username)
        elif method == 'dictionary5':
            # New method for 5-character dictionary
            attack_result = password_attack_service.dictionary5_attack(stored_hash, salt, username)
        elif method == 'bruteforce':
            # Existing brute-force method
            attack_result = password_attack_service.brute_force_6char_attack(stored_hash, salt, username)
        # You might want to remove or update the old combined 'dictionary' case if it exists:
        elif method == 'dictionary':
            # This is the old, combined attack. Consider removing it or using dictionary3_attack/dictionary5_attack here if you need it as a fallback.
            attack_result = password_attack_service.dictionary_attack(stored_hash, salt, username)
        else:
            # Handle unknown methods
            return jsonify({"success": False, "message": "Unknown attack method specified."}), 400


        response_data = {
            "success": True,
            "message": f"Attack completed with {method} method",
            "found": attack_result["success"],
            "password": attack_result.get("password"),
            "attempts": attack_result["attempts"],
            "duration": attack_result.get("duration", 0),
            "method": attack_result["method"]
        }
        
        print(f"\n{'='*80}")
        print(f"PASSWORD ATTACK RESULT")
        print(f"{'='*80}")
        print(f"Found: {response_data['found']}")
        if response_data['found']:
            print(f"Password: {response_data['password']}")
        print(f"Attempts: {response_data['attempts']}")
        print(f"Duration: {response_data['duration']:.3f}s")
        print(f"{'='*80}\n")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"\n{'='*80}")
        print(f"ERROR IN PASSWORD ATTACK")
        print(f"{'='*80}")
        print(error_trace)
        print(f"{'='*80}\n")
        
        return jsonify({
            "success": False, 
            "message": f"Attack failed: {str(e)}"
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("Cryptography Toolkit - Web Application")
    print("=" * 60)
    print("Server starting on http://localhost:5000")
    print("Open your browser and navigate to: http://localhost:5000")
    print("=" * 60)
    print("\nAvailable Features:")
    print("  - /auth         : User authentication")
    print("  - /attack_auth  : Password attacks (educational)")
    print("=" * 60)
    print()
    app.run(debug=True, port=5000, host='0.0.0.0')