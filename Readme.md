# Cryptography Toolkit - Educational Desktop Application

A Python desktop application demonstrating classical cryptography algorithms with real-time messaging capabilities.

## Features

- User authentication (Sign Up/Sign In)
- Classical cryptography algorithms:
  - Caesar Cipher (shift = 3)
  - Affine Cipher (a=5, b=8)
  - Hill Cipher (3x3 matrix)
  - Playfair Cipher (key="MONARCHY")
- Real-time encrypted messaging between users
- Message history (sent/received)
- Visual encryption/decryption demonstration

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

### 4. Run the Application

**Terminal 1** - Start Flask backend:
```bash
python flask_app_run.py
```

**Terminal 2** - Start PyQt5 desktop app:
```bash
python app.py
```

## Full Documentation

- `SETUP_AND_RUN.md` - Complete setup and usage guide
- `DATABASE_SETUP.md` - Database configuration instructions

## Technology Stack

- **Frontend**: PyQt5
- **Backend**: Flask
- **Database**: Supabase (PostgreSQL)
- **Cryptography**: Custom implementations

## Educational Purpose

This project is designed for learning classical cryptography concepts. It is NOT suitable for production use.
