# Database Setup Instructions

## Supabase Database Schema

You need to manually set up the database tables in your Supabase dashboard. Follow these steps:

### 1. Access Supabase SQL Editor

1. Go to your Supabase project dashboard
2. Navigate to the SQL Editor section
3. Click "New Query"

### 2. Run the Following SQL Script

Copy and paste the entire SQL script from the database_migration.sql into the SQL editor and execute it.

### 3. Verify Tables Created

After running the script:
1. Go to the "Table Editor" in your Supabase dashboard
2. You should see three tables: `users`  `messages` `stego_messages`
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

### Stego_Messages Table (Steganography)
- `id`: Auto-incrementing integer, primary key
- `date_created` : Timestamp when message was created
-`audio_filename` : Name of the audio file containing the hidden message (max 255 characters)
- `sender_id`: Foreign key to users.id
- `receiver_id`: Foreign key to users.id
- `created_at`: Timestamp when record was created

## Security Notes

- Row Level Security (RLS) is enabled on both tables
- Users can only read/write their own data
- Messages are visible to both sender and receiver
- Passwords are stored in plain text (for educational purposes only - NOT recommended for production)
