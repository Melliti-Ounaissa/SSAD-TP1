# Quick Setup Guide - Updated App

## 🚀 3 Steps to Run

### Step 1: Update Database

Go to your Supabase SQL Editor and run:

```sql
-- File: database_migration_updated.sql
```

This will:
- Change email → username
- Remove content field
- Add algorithm_key field

### Step 2: Run the App

```bash
python app.py
```

### Step 3: Open Browser

```
http://localhost:5000
```

You'll see the new landing page!

---

## 🎯 What's New?

### 1. Landing Page (`/`)
- Sign In / Sign Up buttons
- Feature showcase
- Beautiful design

### 2. Custom Encryption Keys
- **Caesar**: Enter shift (1-25)
- **Affine**: Enter a and b values
- **Playfair**: Enter keyword
- **Hill**: Uses default matrix

### 3. Real-Time Chat
- `/messages` → See conversations
- Click conversation → Chat interface
- Messages update every 3 seconds
- Decrypt button to read messages

### 4. Fixed Routes
- ✅ `/logout` works now
- ✅ `/encryption/ceasar` fixed
- ✅ All algorithm routes working

---

## 📱 Quick Test

1. **Sign Up**: Create user with username + password (3/5/6 chars)
2. **Go to Messages**: Click Messages in sidebar
3. **Select Algorithm**: Choose Caesar, enter shift=5
4. **Send Message**: Type "HELLO" → Sends encrypted
5. **View Message**: See encrypted text
6. **Click Decrypt**: See "HELLO" again

---

## 🔑 Password Formats

Choose ONE:
1. **3 chars**: 2, 3, or 4 → e.g., `234`
2. **5 digits**: 0-9 → e.g., `12345`
3. **6 chars**: a-z, A-Z, 0-9, +, * → e.g., `Pass+1`

---

## 🆘 Problems?

**404 errors?**
→ Make sure you're running the NEW `app.py`

**Database errors?**
→ Run `database_migration_updated.sql` in Supabase

**Decryption fails?**
→ Use same key parameters that were used for encryption

---

## 📂 Files Changed

**Must update database**: `database_migration_updated.sql`

**Backend updated**:
- `app.py`
- `backend/auth_service.py`
- `backend/message_service.py`
- `backend/crypto_service.py`

**New templates**:
- `templates/landing.html`
- `templates/conversation.html`

**New JavaScript**:
- `static/js/conversation.js`

**New CSS**:
- `static/css/landing.css`

---

## ✨ Features Summary

✅ Landing page with Sign In/Up buttons
✅ Username instead of email
✅ Custom encryption keys
✅ Real-time chat interface
✅ Decrypt button for received messages
✅ Conversations grouped by user
✅ Messages stored encrypted only
✅ All 404 errors fixed

Ready to go! 🎉
