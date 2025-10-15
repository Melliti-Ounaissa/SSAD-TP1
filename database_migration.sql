-- Cryptography Toolkit Database Migration
-- Run this script in your Supabase SQL Editor

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
