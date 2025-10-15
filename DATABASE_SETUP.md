# Database Setup Instructions

## Supabase Database Schema

You need to manually set up the database tables in your Supabase dashboard. Follow these steps:

### 1. Access Supabase SQL Editor

1. Go to your Supabase project dashboard
2. Navigate to the SQL Editor section
3. Click "New Query"

### 2. Run the Following SQL Script

Copy and paste this entire SQL script into the SQL editor and execute it:

```sql
-- Create users table with integer ID
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(50) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Create messages table with integer ID
CREATE TABLE IF NOT EXISTS messages (
  id SERIAL PRIMARY KEY,
  date_created TIMESTAMPTZ DEFAULT now(),
  content VARCHAR(200) NOT NULL,
  encrypted VARCHAR(200) NOT NULL,
  algo_name VARCHAR(10) NOT NULL,
  sender_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  receiver_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_receiver ON messages(receiver_id);
CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(date_created DESC);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Users table policies
CREATE POLICY "Users can read own profile"
  ON users FOR SELECT
  USING (true);

CREATE POLICY "Users can insert during signup"
  ON users FOR INSERT
  WITH CHECK (true);

-- Messages table policies
CREATE POLICY "Users can view their sent messages"
  ON messages FOR SELECT
  USING (sender_id IN (SELECT id FROM users));

CREATE POLICY "Users can view their received messages"
  ON messages FOR SELECT
  USING (receiver_id IN (SELECT id FROM users));

CREATE POLICY "Users can insert messages they send"
  ON messages FOR INSERT
  WITH CHECK (sender_id IN (SELECT id FROM users));
```

### 3. Verify Tables Created

After running the script:
1. Go to the "Table Editor" in your Supabase dashboard
2. You should see two tables: `users` and `messages`
3. Click on each table to verify the columns are created correctly

### 4. Update Environment Variables

Make sure your `.env` file contains the correct Supabase credentials:

```
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## Database Schema Details

### Users Table
- `id`: Auto-incrementing integer, primary key
- `email`: User email (max 50 characters), unique
- `password`: User password (max 50 characters)
- `created_at`: Timestamp when user was created

### Messages Table
- `id`: Auto-incrementing integer, primary key
- `date_created`: Timestamp when message was created
- `content`: Original message content (max 200 characters)
- `encrypted`: Encrypted message content (max 200 characters)
- `algo_name`: Algorithm used (max 10 characters): ceasar, affine, hill, playfair
- `sender_id`: Foreign key to users.id
- `receiver_id`: Foreign key to users.id
- `created_at`: Timestamp when record was created

## Security Notes

- Row Level Security (RLS) is enabled on both tables
- Users can only read/write their own data
- Messages are visible to both sender and receiver
- Passwords are stored in plain text (for educational purposes only - NOT recommended for production)
