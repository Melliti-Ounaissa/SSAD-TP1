-- Updated Cryptography Toolkit Database Migration
-- Run this script in your Supabase SQL Editor

-- Drop existing tables if you want to start fresh (CAUTION: This deletes all data)
-- DROP TABLE IF EXISTS messages CASCADE;
-- DROP TABLE IF EXISTS users CASCADE;

-- Create users table with username instead of email
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(50) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Create messages table without content, with algorithm_key
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

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_receiver ON messages(receiver_id);
CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(date_created DESC);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(sender_id, receiver_id, date_created DESC);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can read own profile" ON users;
DROP POLICY IF EXISTS "Users can insert during signup" ON users;
DROP POLICY IF EXISTS "Users can view their sent messages" ON messages;
DROP POLICY IF EXISTS "Users can view their received messages" ON messages;
DROP POLICY IF EXISTS "Users can insert messages they send" ON messages;

-- Users table policies
CREATE POLICY "Users can read all profiles"
  ON users FOR SELECT
  USING (true);

CREATE POLICY "Users can insert during signup"
  ON users FOR INSERT
  WITH CHECK (true);

-- Messages table policies
CREATE POLICY "Users can view messages they are part of"
  ON messages FOR SELECT
  USING (sender_id IN (SELECT id FROM users) OR receiver_id IN (SELECT id FROM users));

CREATE POLICY "Users can insert messages they send"
  ON messages FOR INSERT
  WITH CHECK (sender_id IN (SELECT id FROM users));
