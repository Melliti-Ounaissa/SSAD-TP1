# Cryptography Toolkit - Educational Web Application

A Python web application demonstrating classical cryptography algorithms with real-time messaging capabilities.

## Features

- User authentication with password validation (3 specific formats)
- Classical cryptography algorithms:
  - Caesar Cipher (shift = 3)
  - Affine Cipher (a=5, b=8)
  - Hill Cipher (3x3 matrix)
  - Playfair Cipher (key="MONARCHY")
- Real-time encrypted messaging between users
- Message history (sent/received)
- Visual encryption/decryption demonstration
- Web-based interface (HTML/CSS/JavaScript)

## Password Requirements

Passwords must follow ONE of these formats:
1. **3 characters**: Each can be 2, 3, or 4 (e.g., `234`, `432`)
2. **5 digits**: 0-9 (e.g., `12345`)
3. **6 characters**: a-z, A-Z, 0-9, +, * (e.g., `q7*88+`)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Database

1. Copy the SQL from `database_migration.sql`
2. Run it in your Supabase SQL Editor
3. See `DATABASE_SETUP.md` for detailed instructions

### 3. Configure Environment

Ensure your `.env` file has:
```
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 4. Run the Web Application

```bash
python run_webapp.py
```

Then open your browser to: **http://localhost:5000**

## Full Documentation

- `WEB_APP_SETUP.md` - Complete web app setup and usage guide
- `DATABASE_SETUP.md` - Database configuration instructions
- `SETUP_AND_RUN.md` - Original desktop app documentation (legacy)

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Flask with session management
- **Database**: Supabase (PostgreSQL)
- **Cryptography**: Custom implementations

## Educational Purpose

This project is designed for learning classical cryptography concepts. It is NOT suitable for production use.
