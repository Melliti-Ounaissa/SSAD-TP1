from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from backend.auth_service import AuthService
from backend.message_service import MessageService
from backend.crypto_service import CryptoService
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
CORS(app)

app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_dev_secret_key')

auth_service = AuthService()
crypto_service = CryptoService()
message_service = MessageService(crypto_service=crypto_service)


@app.route('/')
def index():
    return render_template('landing.html')


@app.route('/auth')
def auth():
    if 'user' in session:
        return redirect(url_for('home'))
    return render_template('auth.html')


@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('home.html', user=session['user'])


@app.route('/algorithms')
def algorithms():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('algorithms.html', user=session['user'])


@app.route('/messages')
def messages_page():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('messages.html', user=session['user'])


@app.route('/conversation/<int:other_user_id>')
def conversation(other_user_id):
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('conversation.html', user=session['user'], other_user_id=other_user_id)


@app.route('/encryption/<algorithm>')
def encrypt_page(algorithm):
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('encryption.html', user=session['user'], algorithm=algorithm)


@app.route('/logout')
def logout():
    session.pop('user', None)
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

    user_id = session['user']['id']
    users = auth_service.get_all_users_except(user_id)

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


if __name__ == '__main__':
    print("=" * 60)
    print("Cryptography Toolkit - Web Application")
    print("=" * 60)
    print("Server starting on http://localhost:5000")
    print("Open your browser and navigate to: http://localhost:5000")
    print("=" * 60)
    print()
    app.run(debug=True, port=5000, host='0.0.0.0')
