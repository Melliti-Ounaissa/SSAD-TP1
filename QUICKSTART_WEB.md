# Quick Start Guide - Web Application

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Setup Database

Go to your Supabase dashboard and run the SQL from `database_migration.sql`

### Step 3: Run the Application

```bash
python run_webapp.py
```

Open your browser to: **http://localhost:5000**

---

## 🔑 Password Rules

Choose ONE format for your password:

| Format | Description | Example |
|--------|-------------|---------|
| Type 1 | 3 chars: 2, 3, or 4 | `234`, `432`, `444` |
| Type 2 | 5 digits: 0-9 | `12345`, `98765` |
| Type 3 | 6 chars: a-z, A-Z, 0-9, +, * | `q7*88+`, `Abc123` |

---

## 📖 Using the App

### Sign Up
1. Enter email
2. Enter password (following one format above)
3. Click "Sign Up"
4. You'll be redirected to home page

### Send Encrypted Messages
1. Click "Algorithmes de Cryptage"
2. Choose: Ceasar, PlayFair, Affine, or Hill
3. Type your message
4. Select recipient
5. Click "Envoyer"
6. See encrypted and decrypted forms!

### View Messages
1. Click "Messages"
2. See two lists:
   - **Messages Envoyés**: Your sent messages
   - **Messages Reçus**: Messages to you
3. Auto-refreshes every 3 seconds

---

## 📁 Project Structure

```
project/
├── backend/           # Flask server + business logic
│   ├── web_app.py            # Main Flask app
│   ├── password_validator.py # Password rules
│   └── ...
├── templates/         # HTML pages
├── static/
│   ├── css/          # Stylesheets
│   └── js/           # JavaScript
├── crypto_algos/     # Encryption algorithms
└── run_webapp.py     # Entry point
```

---

## 🎨 Features

✅ Password validation (3 formats)
✅ Real-time messages (updates every 3s)
✅ 4 classical encryption algorithms
✅ Visual encryption demo
✅ Clean web interface
✅ Session management

---

## 🐛 Troubleshooting

**"Invalid password"**
→ Check password format (3, 5, or 6 characters)

**"User not found"**
→ Sign up first or check credentials

**Can't connect to server**
→ Ensure Flask is running on port 5000

**Database errors**
→ Check Supabase setup and `.env` file

---

## 📚 More Info

- **Full Guide**: `WEB_APP_SETUP.md`
- **Database**: `DATABASE_SETUP.md`
- **Legacy Desktop App**: `SETUP_AND_RUN.md`

---

## ⚠️ Educational Use Only

This project demonstrates cryptography concepts. Do NOT use in production!
- Plain text passwords (no hashing)
- No HTTPS requirement
- Simple session management
