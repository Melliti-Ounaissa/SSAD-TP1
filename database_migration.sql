-- Combined Cryptography Toolkit & Steganography Database Migration Script
-- Run this script in your Supabase SQL Editor

--------------------------------------
-- 1. Table Creation and Updates
--------------------------------------

-- Drop existing tables if you want to start fresh (CAUTION: This deletes all data)
-- Use these only if you are certain you want to wipe existing data
-- DROP TABLE IF EXISTS stego_messages CASCADE;
-- DROP TABLE IF EXISTS messages CASCADE;
-- DROP TABLE IF EXISTS users CASCADE;

-- Create users table with username
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Add updated password fields and drop old 'password' column (from scripts 3 & 4)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS password_hash VARCHAR(16),
ADD COLUMN IF NOT EXISTS password_salt VARCHAR(32),
ADD COLUMN failed_attempts INTEGER DEFAULT 0 NOT NULL,
ADD COLUMN locked_until TIMESTAMPTZ NULL;

ALTER TABLE users DROP COLUMN IF EXISTS password;

-- Create messages table (from script 1)
CREATE TABLE IF NOT EXISTS messages (
  id SERIAL PRIMARY KEY,
  date_created TIMESTAMPTZ DEFAULT now(),
  encrypted VARCHAR(500) NOT NULL,
  algo_name VARCHAR(10) NOT NULL,
  algorithm_key VARCHAR(100),
  sender_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  receiver_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Create stego_messages table (from script 2)
CREATE TABLE IF NOT EXISTS stego_messages (
  id SERIAL PRIMARY KEY,
  date_created TIMESTAMPTZ DEFAULT now(),
  audio_filename VARCHAR(255) NOT NULL,
  sender_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  receiver_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT now()
);


--------------------------------------
-- 2. Indexes for Performance
--------------------------------------

-- Indexes for messages table
CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_receiver ON messages(receiver_id);
CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(date_created DESC);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(sender_id, receiver_id, date_created DESC);

-- Indexes for stego_messages table
CREATE INDEX IF NOT EXISTS idx_stego_messages_sender ON stego_messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_stego_messages_receiver ON stego_messages(receiver_id);
CREATE INDEX IF NOT EXISTS idx_stego_messages_created ON stego_messages(date_created DESC);


--------------------------------------
-- 3. Enable Row Level Security (RLS)
--------------------------------------

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE stego_messages ENABLE ROW LEVEL SECURITY;


--------------------------------------
-- 4. RLS Policy Management
--------------------------------------

-- Drop existing policies if they exist (from scripts 1, 2, 5)
DROP POLICY IF EXISTS "Users can read own profile" ON users;
DROP POLICY IF EXISTS "Users can insert during signup" ON users;
DROP POLICY IF EXISTS "Users can view their sent messages" ON messages;
DROP POLICY IF EXISTS "Users can view their received messages" ON messages;
DROP POLICY IF EXISTS "Users can insert messages they send" ON messages;
DROP POLICY IF EXISTS "Users can view stego messages they are part of" ON stego_messages;
DROP POLICY IF EXISTS "Users can insert stego messages they send" ON stego_messages;
DROP POLICY IF EXISTS "allow updates for lockout" ON users;


-- Policies for the users table
CREATE POLICY "Users can read all profiles"
  ON users FOR SELECT
  USING (true);

CREATE POLICY "Users can insert during signup"
  ON users FOR INSERT
  WITH CHECK (true);

-- Policy for login/lockout updates (from script 5)
-- Note: This broad policy may need refinement based on your final application logic
CREATE POLICY "allow updates for lockout"
ON public.users
FOR UPDATE
TO public, anon
USING (true)
WITH CHECK (true);


-- Policies for the messages table
CREATE POLICY "Users can view messages they are part of"
  ON messages FOR SELECT
  -- Assuming the RLS check should use auth.uid() or similar for actual session users
  -- The original script's check (sender_id IN (SELECT id FROM users) OR receiver_id IN (SELECT id FROM users))
  -- is usually an RLS anti-pattern as it grants access to ALL users who exist.
  -- For a typical Supabase setup, you'd use:
  -- USING (auth.uid() = sender_id OR auth.uid() = receiver_id);
  -- Keeping the original check to match the request's logic:
  USING (sender_id IN (SELECT id FROM users) OR receiver_id IN (SELECT id FROM users));

CREATE POLICY "Users can insert messages they send"
  ON messages FOR INSERT
  -- Keeping the original check to match the request's logic:
  WITH CHECK (sender_id IN (SELECT id FROM users));
  -- For a typical Supabase setup, you'd use:
  -- WITH CHECK (auth.uid() = sender_id);


-- Policies for the stego_messages table
CREATE POLICY "Users can view stego messages they are part of"
  ON stego_messages FOR SELECT
  -- Keeping the original check to match the request's logic:
  USING (sender_id IN (SELECT id FROM users) OR receiver_id IN (SELECT id FROM users));

CREATE POLICY "Users can insert stego messages they send"
  ON stego_messages FOR INSERT
  -- Keeping the original check to match the request's logic:
  WITH CHECK (sender_id IN (SELECT id FROM users));