# Cryptography Toolkit - Setup and Run Instructions

## Project Overview

This is an educational desktop application demonstrating classical cryptography algorithms (Caesar, Affine, Hill, Playfair) with a messaging system to show encryption/decryption in action.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Supabase account and project

## Installation Steps

### 1. Clone or Download the Project

Make sure you have all project files in your working directory.

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Supabase Database

Follow the instructions in `DATABASE_SETUP.md` to create the necessary database tables in your Supabase project.

### 5. Configure Environment Variables

Make sure your `.env` file contains your Supabase credentials:

```
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

You can find these values in your Supabase project dashboard under Settings > API.

## Running the Application

### Step 1: Start the Flask Backend Server

Open a terminal and run:

```bash
python backend/flask_app.py
```

The Flask server will start on `http://localhost:5000`

### Step 2: Start the PyQt5 Desktop Application

Open a **new terminal** (keep the Flask server running) and run:

```bash
python app.py
```

Or alternatively:

```bash
python main.py
```

The desktop application window will open.

## Using the Application

### 1. Authentication

- **Sign Up**: Enter email and password, click "Sign Up" to create a new account
- **Sign In**: Enter existing credentials and click "Sign In"

### 2. Home Page

After login, you'll see two main options:
- **Messages**: View sent and received messages
- **Algorithmes de Cryptage**: Test encryption algorithms
- **Attaques**: (Coming soon)

### 3. Testing Encryption Algorithms

1. Click "Algorithmes de Cryptage"
2. Choose an algorithm (Ceasar, Affine, Hill, or Playfair)
3. Enter your message in the "votre message" field
4. Select a recipient from the dropdown
5. Click "Envoyer" (Send)
6. You'll see:
   - The encrypted message in the top "message chiffré" field
   - The original message in the receiver's "message reçu" field

### 4. Viewing Messages

1. Click "Messages" from the sidebar
2. See two lists:
   - **Messages Envoyés** (Sent): Messages you've sent
   - **Messages Reçus** (Received): Messages sent to you
3. The list auto-refreshes every 3 seconds to show new messages

## Algorithm Default Parameters

- **Caesar Cipher**: Shift = 3
- **Affine Cipher**: a = 5, b = 8
- **Hill Cipher**: 3x3 matrix [[6,24,1], [13,16,10], [20,17,15]]
- **Playfair Cipher**: Key = "MONARCHY"

## Troubleshooting

### "Connection error" when logging in

- Make sure Flask server is running on port 5000
- Check that your `.env` file has correct Supabase credentials
- Verify the database tables are created in Supabase

### "Could not load users" error

- Ensure database tables are properly set up
- Check Supabase connection in `.env`
- Verify RLS policies are created

### PyQt5 won't start

- Make sure you've installed all requirements: `pip install -r requirements.txt`
- On Linux, you may need to install additional Qt dependencies

### Flask server errors

- Check Python version (3.8+)
- Verify all packages are installed
- Check `.env` file exists and is properly formatted

## Project Structure

```
project/
├── backend/
│   ├── auth_service.py       # Authentication logic
│   ├── message_service.py    # Message handling
│   ├── crypto_service.py     # Encryption wrapper
│   ├── database.py           # Supabase client
│   └── flask_app.py          # Flask API server
├── crypto_algos/
│   └── algos/
│       ├── ceasare.py        # Caesar cipher
│       ├── affine.py         # Affine cipher
│       ├── hill.py           # Hill cipher
│       └── playfair.py       # Playfair cipher
├── ui/
│   ├── auth_window.py        # Login/Signup UI
│   ├── home_window.py        # Home page UI
│   ├── algorithms_window.py # Algorithm selection UI
│   ├── encryption_window.py # Encryption demo UI
│   └── messages_window.py    # Messages inbox UI
├── main.py                   # Main application entry
├── app.py                    # Alternative entry point
├── requirements.txt          # Python dependencies
└── .env                      # Environment variables
```

## Notes

- This is an educational project for demonstrating classical cryptography
- Passwords are stored in plain text (NOT suitable for production use)
- Real-time updates use polling (every 3 seconds) for messages
- All encryption uses default parameters for consistency
