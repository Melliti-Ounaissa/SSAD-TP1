from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file, Response
from flask_cors import CORS
from backend.auth_service import AuthService
from backend.message_service import MessageService
from backend.crypto_service import CryptoService
from backend.stego_service import StegoService
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

auth_service = AuthService()
crypto_service = CryptoService()
message_service = MessageService(crypto_service=crypto_service)
stego_service = StegoService()


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


@app.route('/favicon.ico')
def favicon():
    return '', 204


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
        result = stego_service.hide_message_and_save(
            file, secret_message, sender_id, receiver_id, app.config['UPLOAD_FOLDER']
        )
        return jsonify(result), 200
    except Exception as e:
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
        if not os.path.exists(file_path):
            return jsonify({"success": False, "message": "File not found"}), 404
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Check if range header is present
        range_header = request.headers.get('Range', None)
        
        if not range_header:
            # No range requested, send entire file
            with open(file_path, 'rb') as f:
                data = f.read()
            
            response = Response(data, 200, mimetype='audio/wav', direct_passthrough=True)
            response.headers.add('Content-Length', str(file_size))
            response.headers.add('Accept-Ranges', 'bytes')
            return response
        
        # Parse range header
        byte_range = range_header.replace('bytes=', '').split('-')
        start = int(byte_range[0]) if byte_range[0] else 0
        end = int(byte_range[1]) if byte_range[1] else file_size - 1
        
        # Ensure valid range
        if start >= file_size or end >= file_size:
            return Response('Requested Range Not Satisfiable', 416)
        
        length = end - start + 1
        
        # Read the requested range
        with open(file_path, 'rb') as f:
            f.seek(start)
            data = f.read(length)
        
        # Create response with partial content
        response = Response(data, 206, mimetype='audio/wav', direct_passthrough=True)
        response.headers.add('Content-Length', str(length))
        response.headers.add('Content-Range', f'bytes {start}-{end}/{file_size}')
        response.headers.add('Accept-Ranges', 'bytes')
        response.headers.add('Cache-Control', 'no-cache')
        
        return response
        
    except Exception as e:
        print(f"Error serving audio: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("Cryptography Toolkit - Web Application")
    print("=" * 60)
    print("Server starting on http://localhost:5000")
    print("Open your browser and navigate to: http://localhost:5000")
    print("=" * 60)
    print()
    app.run(debug=True, port=5000, host='0.0.0.0')