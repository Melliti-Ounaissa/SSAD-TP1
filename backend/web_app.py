import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from backend.auth_service import AuthService
from backend.message_service import MessageService
from backend.crypto_service import CryptoService

app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')
app.secret_key = 'your-secret-key-here-change-in-production'
CORS(app)

auth_service = AuthService()
message_service = MessageService()
crypto_service = CryptoService()


@app.route('/')
def index():
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


@app.route('/encryption/<algorithm>')
def encryption(algorithm):
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('encryption.html', user=session['user'], algorithm=algorithm)


@app.route('/messages')
def messages():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('messages.html', user=session['user'])


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400

    result = auth_service.sign_up(email, password)

    if result['success']:
        session['user'] = result['user']

    return jsonify(result), 200 if result['success'] else 400


@app.route('/api/auth/signin', methods=['POST'])
def signin():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400

    result = auth_service.sign_in(email, password)

    if result['success']:
        session['user'] = result['user']

    return jsonify(result), 200 if result['success'] else 400


@app.route('/api/users/<int:user_id>/others', methods=['GET'])
def get_other_users(user_id):
    result = auth_service.get_all_users_except(user_id)
    return jsonify(result), 200 if result['success'] else 400


@app.route('/api/messages/send', methods=['POST'])
def send_message():
    data = request.json
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')
    content = data.get('content')
    algo_name = data.get('algo_name')

    if not all([sender_id, receiver_id, content, algo_name]):
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    try:
        encrypted = crypto_service.encrypt_message(content, algo_name)
        result = message_service.send_message(sender_id, receiver_id, content, encrypted, algo_name)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/messages/sent/<int:user_id>', methods=['GET'])
def get_sent_messages(user_id):
    result = message_service.get_sent_messages(user_id)
    return jsonify(result), 200 if result['success'] else 400


@app.route('/api/messages/received/<int:user_id>', methods=['GET'])
def get_received_messages(user_id):
    result = message_service.get_received_messages(user_id)
    return jsonify(result), 200 if result['success'] else 400


@app.route('/api/crypto/encrypt', methods=['POST'])
def encrypt():
    data = request.json
    message = data.get('message')
    algorithm = data.get('algorithm')

    if not message or not algorithm:
        return jsonify({"success": False, "message": "Message and algorithm are required"}), 400

    try:
        encrypted = crypto_service.encrypt_message(message, algorithm)
        return jsonify({"success": True, "encrypted": encrypted}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/crypto/decrypt', methods=['POST'])
def decrypt():
    data = request.json
    encrypted_message = data.get('encrypted_message')
    algorithm = data.get('algorithm')

    if not encrypted_message or not algorithm:
        return jsonify({"success": False, "message": "Encrypted message and algorithm are required"}), 400

    try:
        decrypted = crypto_service.decrypt_message(encrypted_message, algorithm)
        return jsonify({"success": True, "decrypted": decrypted}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
