# Cryptography Toolkit - Web Application Setup

## Overview

This is the web-based version of the Cryptography Toolkit, featuring:
- HTML/CSS frontend (no desktop framework required)
- Flask backend with session management
- Password validation with three specific formats
- Real-time message updates
- Classical cryptography algorithms demonstration

## Password Requirements

When signing up, passwords must follow ONE of these formats:

1. **Type 1**: 3 characters, each can be 2, 3, or 4
   - Examples: `234`, `432`, `444`, `222`, `323`

2. **Type 2**: 5 digits, each can be 0-9
   - Examples: `12345`, `98765`, `00000`

3. **Type 3**: 6 characters, using a-z, A-Z, 0-9, +, *
   - Examples: `q7*88+`, `Abc123`, `Pass+1`

Any other password format will show "Invalid password" and prevent user creation.

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Database

Run the SQL script in your Supabase dashboard:

```bash
# The SQL is in database_migration.sql
```

See `DATABASE_SETUP.md` for detailed instructions.

### 3. Configure Environment

Ensure your `.env` file contains:

```
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## Running the Web Application

### Start the Server

```bash
python run_webapp.py
```

The server will start on `http://localhost:5000`

### Access the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

## Using the Application

### 1. Authentication

**Sign Up:**
- Enter your email
- Enter a password following one of the three formats
- Click "Sign Up"
- If password is invalid, you'll see "Invalid password"
- If successful, you'll be redirected to the home page

**Sign In:**
- Enter your existing email and password
- Click "Sign In"
- If credentials are wrong, you'll see "User not found, try to sign up!"

### 2. Navigation

The left sidebar (blue gradient) contains:
- **Back arrow (←)**: Returns to home page
- **Messages**: View sent and received messages
- **Algorithmes de Cryptage**: Choose encryption algorithm
- **Attaques**: Coming soon

### 3. Testing Encryption

1. Click "Algorithmes de Cryptage"
2. Choose an algorithm: Ceasar, PlayFair, Affine, or Hill
3. On the encryption page:
   - Top box shows the encrypted message
   - Left side (💻): Enter your message
   - Right side (💻): Shows the decrypted message (what receiver sees)
   - Select a recipient from the dropdown
   - Click "Envoyer" to send

### 4. Viewing Messages

1. Click "Messages" in the sidebar
2. Two columns display:
   - **Messages Envoyés** (Sent): Your sent messages
   - **Messages Reçus** (Received): Messages you received
3. Each message card shows:
   - Sender/Recipient email
   - Algorithm used
   - Date and time
   - Original message content
   - Encrypted form

Messages auto-refresh every 3 seconds.

## Project Structure

```
project/
├── backend/
│   ├── auth_service.py          # Authentication with password validation
│   ├── message_service.py       # Message handling
│   ├── crypto_service.py        # Encryption algorithms
│   ├── database.py              # Supabase connection
│   ├── password_validator.py    # Password format validation
│   └── web_app.py               # Flask web application
├── templates/
│   ├── auth.html                # Login/signup page
│   ├── home.html                # Home page
│   ├── algorithms.html          # Algorithm selection
│   ├── encryption.html          # Encryption demonstration
│   └── messages.html            # Message inbox
├── static/
│   ├── css/
│   │   ├── auth.css            # Authentication page styles
│   │   └── main.css            # Main application styles
│   └── js/
│       ├── auth.js             # Authentication logic
│       ├── encryption.js       # Encryption page logic
│       └── messages.js         # Messages page logic
├── crypto_algos/
│   └── algos/
│       ├── ceasare.py          # Caesar cipher
│       ├── affine.py           # Affine cipher
│       ├── hill.py             # Hill cipher
│       └── playfair.py         # Playfair cipher
├── run_webapp.py               # Web app entry point
└── requirements.txt            # Python dependencies
```

## Algorithm Parameters

- **Caesar**: Shift = 3
- **Affine**: a = 5, b = 8
- **Hill**: 3x3 matrix [[6,24,1], [13,16,10], [20,17,15]]
- **Playfair**: Key = "MONARCHY"

## Features

### Password Validation
- Client-side validation (JavaScript)
- Server-side validation (Python)
- Clear error messages
- Prevents invalid user creation

### Session Management
- Flask sessions for user authentication
- Automatic redirect to login if not authenticated
- Logout functionality

### Real-time Updates
- Messages refresh every 3 seconds
- No manual page refresh needed

### Responsive Design
- Sidebar navigation
- Clean, modern interface
- Based on provided UI mockups

## Troubleshooting

### "Invalid password" error
- Ensure your password matches ONE of the three formats exactly
- Check character count (3, 5, or 6)
- Verify allowed characters for each type

### "User not found, try to sign up!"
- Email or password is incorrect
- Try signing up if you don't have an account

### Cannot connect to server
- Ensure Flask server is running
- Check that port 5000 is not in use
- Verify `.env` file exists with correct credentials

### Database errors
- Verify Supabase tables are created
- Check `.env` credentials
- Review `DATABASE_SETUP.md`

## Differences from Desktop App

| Feature | Desktop App | Web App |
|---------|-------------|---------|
| Frontend | PyQt5 | HTML/CSS/JavaScript |
| Access | Single machine | Any browser |
| Installation | Python + PyQt5 | Python + Flask only |
| UI Updates | Qt signals | AJAX requests |
| Sessions | In-memory | Flask sessions |
| Password Rules | None | Three specific formats |

## Security Notes

- Passwords stored in plain text (educational purposes only)
- Not suitable for production use
- Use HTTPS in production
- Change Flask secret key in production
- Implement proper password hashing for real applications

## Browser Compatibility

Tested and working on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
