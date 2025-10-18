from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from backend.auth_service import AuthService
from backend.message_service import MessageService
from backend.crypto_service import CryptoService
import os                              
from dotenv import load_dotenv

# --- App Initialization and Configuration ---

# Initialize the Flask application
# We specify the template and static folders relative to this root file.
app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
# Enable Cross-Origin Resource Sharing (CORS) for the app
CORS(app)

app.secret_key = os.getenv('FLASK_SECRET_KEY')
# --- Service Instantiation ---

# Create instances of your service classes to handle business logic
auth_service = AuthService()
message_service = MessageService()
crypto_service = CryptoService()


# --- Frontend Routes (Serving HTML Pages) ---

@app.route('/')
def index():
    """Renders the main authentication page or redirects if logged in."""
    if 'user' in session:
        return redirect(url_for('home'))
    return render_template('auth.html')


@app.route('/home')
def home():
    """Renders the user's home page."""
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('home.html', user=session['user'])


@app.route('/algorithms')
def algorithms():
    """Displays the list of available cryptographic algorithms."""
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('algorithms.html', user=session['user'])


@app.route('/encryption/<algorithm>')
def encryption(algorithm):
    """Page for performing encryption/decryption with a specific algorithm."""
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('encryption.html', user=session['user'], algorithm=algorithm)


@app.route('/messages')
def messages():
    """Displays the user's sent and received messages."""
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('messages.html', user=session['user'])


@app.route('/logout')
def logout():
    """Logs the user out by clearing the session."""
    session.pop('user', None)
    return redirect(url_for('index'))


# --- API Endpoints ---

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """API endpoint for user registration."""
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
    """API endpoint for user login."""
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
    """API endpoint to fetch all users except the current one."""
    result = auth_service.get_all_users_except(user_id)
    return jsonify(result), 200 if result['success'] else 400


@app.route('/api/messages/send', methods=['POST'])
def send_message():
    """API endpoint to send a message to another user."""
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
    """API endpoint to retrieve messages sent by the user."""
    result = message_service.get_sent_messages(user_id)
    return jsonify(result), 200 if result['success'] else 400


@app.route('/api/messages/received/<int:user_id>', methods=['GET'])
def get_received_messages(user_id):
    """API endpoint to retrieve messages received by the user."""
    result = message_service.get_received_messages(user_id)
    return jsonify(result), 200 if result['success'] else 400


@app.route('/api/crypto/encrypt', methods=['POST'])
def encrypt():
    """API endpoint for encrypting a message with a chosen algorithm."""
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
    """API endpoint for decrypting a message with a chosen algorithm."""
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


# --- Main Execution Block ---

if __name__ == '__main__':
    # This block runs the Flask development server when the script is executed directly.
    # It includes the startup messages from your original run_webapp.py.
    print("=" * 60)
    print("Cryptography Toolkit - Web Application")
    print("=" * 60)
    print("Server starting on http://localhost:5000")
    print("Open your browser and navigate to: http://localhost:5000")
    print("=" * 60)
    print()
    app.run(debug=True, port=5000, host='0.0.0.0')
    
    
    
    
    # -*- coding: utf-8 -*-
"""
Main application file for the Cryptography Toolkit.

This single file initializes the Flask application, defines all web page
and API routes, and includes the script to run the server. This refactors
the logic previously split across web_app.py, flask_app.py, and run_webapp.py.
"""