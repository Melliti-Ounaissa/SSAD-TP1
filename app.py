from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from backend.auth_service import AuthService
from backend.message_service import MessageService
from backend.crypto_service import CryptoService
import os                              
from dotenv import load_dotenv

# --- App Initialization and Configuration ---

load_dotenv() # Load .env variables

# Initialize the Flask application
# We specify the template and static folders relative to this root file.
app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
# Enable Cross-Origin Resource Sharing (CORS) for the app
CORS(app)

# SET SECRET KEY for session management (REQUIRED for 'session' variable)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_dev_secret_key')

# --- Service Instantiation ---\

# Create instances of your service classes to handle business logic
auth_service = AuthService()
crypto_service = CryptoService()
# PASS crypto_service to MessageService for server-side decryption
message_service = MessageService(crypto_service=crypto_service) 


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


@app.route('/messages')
def messages():
    """Displays the message inbox/outbox."""
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('messages.html', user=session['user'])


@app.route('/encrypt/<algorithm>')
def encrypt_page(algorithm):
    """Renders the encryption page for a specific algorithm."""
    if 'user' not in session:
        return redirect(url_for('index'))
    # You might want to validate the algorithm here
    return render_template('encryption.html', user=session['user'], algorithm=algorithm)


# --- API Routes (Authentication) ---

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """API endpoint for user sign up."""
    data = request.json
    username = data.get('username') # CHANGED email to username
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required"}), 400

    result = auth_service.sign_up(username, password) # CHANGED email to username

    if result['success']:
        # Set user session upon successful sign up
        session['user'] = result['user']
        return jsonify(result), 200
    else:
        return jsonify(result), 400

@app.route('/api/auth/signin', methods=['POST'])
def signin():
    """API endpoint for user sign in."""
    data = request.json
    username = data.get('username') # CHANGED email to username
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required"}), 400

    result = auth_service.sign_in(username, password) # CHANGED email to username

    if result['success']:
        # Set user session upon successful sign in
        session['user'] = result['user']
        return jsonify(result), 200
    else:
        return jsonify(result), 400

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """API endpoint for user logout."""
    session.pop('user', None)
    return jsonify({"success": True, "message": "Logout successful"}), 200

@app.route('/api/users', methods=['GET'])
def get_users():
    """API endpoint to get all users for recipient selection."""
    if 'user' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    user_id = session['user']['id']
    users = auth_service.get_all_users_except(user_id)

    return jsonify({"success": True, "users": users}), 200

# --- API Routes (Messaging) ---

@app.route('/api/messages/send', methods=['POST'])
def send_message():
    """API endpoint for sending a new message."""
    if 'user' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    data = request.json
    # Frontend must now send 'encrypted' message content, 'content' is removed
    encrypted = data.get('encrypted')
    algo_name = data.get('algo_name')
    receiver_id = data.get('receiver_id')
    
    sender_id = session['user']['id']

    if not all([encrypted, algo_name, receiver_id]):
        return jsonify({"success": False, "message": "Encrypted message, algorithm, and receiver ID are required"}), 400

    # Removed 'content' from the call
    result = message_service.send_message(sender_id, receiver_id, encrypted, algo_name)

    return jsonify(result), 200


@app.route('/api/messages/sent/<int:user_id>', methods=['GET'])
def get_sent_messages(user_id):
    """API endpoint to get sent messages for a user."""
    # Basic check to ensure user is logged in and requesting their own messages
    if 'user' not in session or session['user']['id'] != user_id:
        return jsonify({"success": False, "message": "Unauthorized or Invalid User ID"}), 401

    result = message_service.get_sent_messages(user_id)
    return jsonify(result), 200


@app.route('/api/messages/received/<int:user_id>', methods=['GET'])
def get_received_messages(user_id):
    """API endpoint to get received messages for a user."""
    # Basic check to ensure user is logged in and requesting their own messages
    if 'user' not in session or session['user']['id'] != user_id:
        return jsonify({"success": False, "message": "Unauthorized or Invalid User ID"}), 401

    result = message_service.get_received_messages(user_id)
    return jsonify(result), 200

# --- API Routes (Cryptography) ---

@app.route('/api/crypto/encrypt', methods=['POST'])
def encrypt():
    """API endpoint for encrypting a message with a chosen algorithm."""
    data = request.json
    message = data.get('message')
    algorithm = data.get('algorithm')
    
    # Assuming key/shift parameters are passed in 'data' as well
    
    if not message or not algorithm:
        return jsonify({"success": False, "message": "Message and algorithm are required"}), 400

    try:
        # Assuming crypto_service.encrypt_message handles all parameters including keys
        encrypted = crypto_service.encrypt_message(message, algorithm, data) 
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
        # Assuming crypto_service.decrypt_message handles all parameters including keys
        decrypted = crypto_service.decrypt_message(encrypted_message, algorithm, data)
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