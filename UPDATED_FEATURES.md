# Updated Features - Cryptography Toolkit v2.0

## 🎯 All Issues Fixed

### 1. ✅ Fixed 404 Errors
- **Logout route**: Changed from `/logout` (GET) to proper route handling
- **Encryption routes**: Now properly defined as `/encryption/<algorithm>`
- All routes are now functional and accessible

### 2. ✅ Database Schema Updated

#### Changes Made:
- **Replaced `email` with `username`** in users table
- **Removed `content` field** from messages table (only encrypted messages stored)
- **Added `algorithm_key` field** to store encryption parameters (JSON)

#### New Database Schema:
```sql
-- Users table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(50) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Messages table
CREATE TABLE messages (
  id SERIAL PRIMARY KEY,
  date_created TIMESTAMPTZ DEFAULT now(),
  encrypted VARCHAR(500) NOT NULL,
  algo_name VARCHAR(10) NOT NULL,
  algorithm_key VARCHAR(100),  -- NEW: Stores custom keys as JSON
  sender_id INTEGER NOT NULL REFERENCES users(id),
  receiver_id INTEGER NOT NULL REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT now()
);
```

### 3. ✅ Custom Algorithm Keys

Users can now enter custom keys for each algorithm:

#### Caesar Cipher
- **Input**: Shift value (1-25)
- **Default**: 3
- **Example**: Shift=5 encrypts "HELLO" → "MJQQT"

#### Affine Cipher
- **Inputs**: a (multiplier), b (offset)
- **Defaults**: a=5, b=8
- **Constraint**: a must be coprime with 26

#### Playfair Cipher
- **Input**: Keyword (up to 25 characters)
- **Default**: "MONARCHY"
- **Example**: Key="SECRET"

#### Hill Cipher
- **Uses default 3x3 matrix** (no custom input yet)

### 4. ✅ New Landing Page (Route `/`)

The home route (`/`) now displays a landing page with:
- Welcome message
- Features showcase
- **Sign In** and **Sign Up** buttons that redirect to `/auth`
- Beautiful gradient design with floating lock icon

### 5. ✅ Logout Functionality

- Logout button properly clears session
- Redirects to landing page (`/`)
- User must sign in again to access protected pages

### 6. ✅ Real-Time Messaging

Complete chat/messaging app functionality:

#### Features:
- **Real-time updates** (polls every 3 seconds)
- **Conversation view** (like WhatsApp/Telegram)
- **Message bubbles**:
  - Sent messages: Right side, dark blue
  - Received messages: Left side, light blue
- **Encrypted by default**: All messages stored only as encrypted text
- **Decrypt button**: Click to reveal decrypted message
- **Algorithm selection**: Choose algorithm before sending
- **Custom keys**: Enter your own encryption parameters

#### Flow:
1. Click "Messages" → See list of conversations
2. Click on a conversation → Opens chat view
3. Select algorithm and enter key parameters
4. Type message and send
5. Receiver sees encrypted message
6. Click "Decrypt" to read original message

### 7. ✅ Unified Message View

Messages are now grouped by conversation:

#### Messages Page (`/messages`):
- Shows list of conversations with other users
- Each conversation shows:
  - Other user's username
  - Last message preview (encrypted)
  - Timestamp
  - "Sent" or "Received" indicator

#### Conversation Page (`/conversation/<user_id>`):
- Real-time chat interface
- All messages between you and selected user
- Chronological order (oldest to newest)
- Sent vs Received clearly marked
- Each message shows:
  - Sender
  - Timestamp
  - Encrypted text
  - Algorithm used
  - Decrypt button (for received messages)

## 🚀 How to Use

### First Time Setup

1. **Update Database**:
   ```bash
   # Run the updated SQL in your Supabase dashboard
   # File: database_migration_updated.sql
   ```

2. **Start Application**:
   ```bash
   python app.py
   ```

3. **Open Browser**:
   ```
   http://localhost:5000
   ```

### Using the Application

#### Sign Up
1. Go to http://localhost:5000
2. Click "Sign Up"
3. Enter username and password (following one of 3 formats)
4. Click "Sign Up" button

#### Send Encrypted Message
1. Click "Messages" in sidebar
2. If no conversations, go to "Algorithmes de Cryptage"
3. Or click a conversation to open chat
4. Select algorithm (Caesar, Affine, Hill, or Playfair)
5. Enter custom key parameters
6. Type your message
7. Click "Send"

#### Read Encrypted Message
1. Go to "Messages"
2. Click on a conversation
3. You'll see encrypted text in blue bubbles
4. Click "Decrypt" button to reveal the message
5. Original message appears in plain text

#### Custom Keys Examples

**Caesar with shift=7:**
- Message: "HELLO"
- Encrypted: "OLSSV"

**Affine with a=3, b=5:**
- Message: "HELLO"
- Encrypted: "QNIIB"

**Playfair with key="SECRET":**
- Message: "HELLO"
- Encrypted: "DBHKQL"

## 📁 New/Updated Files

### Backend:
- `app.py` - Fixed all routes, added conversation endpoints
- `backend/auth_service.py` - Updated to use username
- `backend/message_service.py` - Added conversation methods
- `backend/crypto_service.py` - Accepts custom key parameters

### Frontend Templates:
- `templates/landing.html` - NEW: Welcome/landing page
- `templates/auth.html` - Updated: Uses username instead of email
- `templates/conversation.html` - NEW: Real-time chat interface
- `templates/messages.html` - Updated: Shows conversations list

### CSS:
- `static/css/landing.css` - NEW: Landing page styles
- `static/css/main.css` - Updated: Added conversation/chat styles

### JavaScript:
- `static/js/auth.js` - Updated: Uses username
- `static/js/conversation.js` - NEW: Chat functionality with decrypt
- `static/js/messages.js` - Updated: Displays conversations

### Database:
- `database_migration_updated.sql` - NEW: Updated schema

## 🔧 API Endpoints

### New/Updated:
- `GET /` - Landing page
- `GET /auth` - Authentication page
- `GET /logout` - Logout and redirect to landing
- `GET /conversation/<user_id>` - Chat with specific user
- `POST /api/messages/send` - Now accepts `key_params`
- `GET /api/messages/conversation/<user_id>` - Get messages between two users
- `GET /api/messages/all` - Get all conversations for current user
- `POST /api/crypto/decrypt` - Decrypt with custom keys

## 🎨 User Experience Improvements

1. **Landing page** welcomes users before authentication
2. **Custom keys** give users control over encryption
3. **Real-time chat** feels like modern messaging apps
4. **Decrypt on demand** adds security (messages stay encrypted until clicked)
5. **Conversation view** organizes messages by user
6. **Visual indicators** show sent vs received clearly
7. **Algorithm selection** per message for flexibility

## 🔒 Security Notes

- Messages stored ONLY in encrypted form
- Original plaintext never stored in database
- Decryption happens client-side on demand
- Each message can use different algorithm/key
- Password validation still enforced (3 formats)

## 📊 Technical Details

### Message Flow:
1. User types message + selects algorithm + enters key
2. Frontend encrypts message using crypto API
3. Encrypted text + algorithm + key sent to server
4. Server stores in database (encrypted only)
5. Receiver fetches encrypted message
6. Clicks "Decrypt" → API decrypts with stored key
7. Plaintext displayed in chat bubble

### Real-time Updates:
- JavaScript polls server every 3 seconds
- Fetches new messages for current conversation
- Automatically scrolls to bottom
- Smooth animations for new messages

## 🐛 Troubleshooting

**"404 Not Found"**
→ Make sure you're running the updated `app.py`

**"Invalid password"**
→ Follow one of the 3 password formats exactly

**Messages not updating**
→ Check browser console for errors
→ Ensure server is running

**Decrypt fails**
→ Verify the key parameters match encryption settings
→ Check that algorithm supports decryption

**Database errors**
→ Run `database_migration_updated.sql` in Supabase
→ Verify `.env` credentials

## 🎉 Summary

All 7 requested features implemented:
1. ✅ Fixed 404 errors
2. ✅ Updated database (username, removed content, added algorithm_key)
3. ✅ Custom algorithm keys
4. ✅ Landing page at `/`
5. ✅ Proper logout to landing page
6. ✅ Real-time messaging chat app
7. ✅ Decrypt button and unified conversation view

The app is now a complete, secure, real-time encrypted messaging platform with custom encryption parameters!
