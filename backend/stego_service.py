from backend.database import get_supabase_client
from datetime import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from steganography.steganography import hide_in_audio, extract_from_audio


class StegoService:
    def __init__(self):
        self.supabase = get_supabase_client()

    def hide_message_and_save_from_temp(self, temp_path, secret_message, sender_id, receiver_id, upload_folder):
        """Hide message in audio from temporary file and save to database"""
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            output_filename = f"stego_{sender_id}_{timestamp}.wav"
            output_path = os.path.join(upload_folder, output_filename)

            # Hide message in audio
            hide_in_audio(temp_path, secret_message, output_path)

            # Verify output file was created and is valid
            if not os.path.exists(output_path):
                return {"success": False, "message": "Failed to create steganography file"}
            
            # Verify output file integrity
            import wave
            try:
                with wave.open(output_path, 'rb') as wav:
                    frames = wav.getnframes()
                    if frames == 0:
                        os.remove(output_path)
                        return {"success": False, "message": "Generated audio file is empty"}
            except Exception as e:
                if os.path.exists(output_path):
                    os.remove(output_path)
                return {"success": False, "message": f"Generated audio file is corrupted: {str(e)}"}

            # Save to database
            message_data = {
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "audio_filename": output_filename,
                "date_created": datetime.now().isoformat()
            }

            result = self.supabase.table('stego_messages').insert(message_data).execute()

            if result.data and len(result.data) > 0:
                return {"success": True, "message": "Steganography message sent successfully", "data": result.data[0]}
            else:
                # Clean up file if database save failed
                if os.path.exists(output_path):
                    os.remove(output_path)
                return {"success": False, "message": "Failed to save message to database"}

        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def hide_message_and_save(self, audio_file, secret_message, sender_id, receiver_id, upload_folder):
        """Hide message in audio and save to database (legacy method)"""
        try:
            # Generate unique filenames
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            input_filename = f"original_{sender_id}_{timestamp}.wav"
            output_filename = f"stego_{sender_id}_{timestamp}.wav"
            
            input_path = os.path.join(upload_folder, input_filename)
            output_path = os.path.join(upload_folder, output_filename)

            # Save uploaded file
            audio_file.save(input_path)

            # Hide message in audio
            hide_in_audio(input_path, secret_message, output_path)

            # Save to database
            message_data = {
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "audio_filename": output_filename,
                "date_created": datetime.now().isoformat()
            }

            result = self.supabase.table('stego_messages').insert(message_data).execute()

            # Clean up original file
            if os.path.exists(input_path):
                os.remove(input_path)

            if result.data and len(result.data) > 0:
                return {"success": True, "message": "Steganography message sent successfully", "data": result.data[0]}
            else:
                return {"success": False, "message": "Failed to save message"}

        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def get_user_messages(self, user_id):
        """Get all steganography messages for a user"""
        try:
            result = self.supabase.table('stego_messages').select(
                '''
                id,
                date_created,
                audio_filename,
                sender_id,
                receiver_id,
                sender:users!stego_messages_sender_id_fkey(id, username),
                receiver:users!stego_messages_receiver_id_fkey(id, username)
                '''
            ).or_(
                f'sender_id.eq.{user_id},receiver_id.eq.{user_id}'
            ).order('date_created', desc=True).execute()

            return {"success": True, "messages": result.data if result.data else []}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def decrypt_message(self, message_id, user_id, upload_folder):
        """Extract hidden message from audio file"""
        try:
            # Get message from database
            result = self.supabase.table('stego_messages').select('*').eq('id', message_id).execute()

            if not result.data or len(result.data) == 0:
                return {"success": False, "message": "Message not found"}

            message = result.data[0]

            # Verify user is receiver
            if message['receiver_id'] != user_id:
                return {"success": False, "message": "Unauthorized"}

            # Extract message from audio
            audio_path = os.path.join(upload_folder, message['audio_filename'])
            
            if not os.path.exists(audio_path):
                return {"success": False, "message": "Audio file not found"}

            hidden_message = extract_from_audio(audio_path)

            return {"success": True, "decrypted_message": hidden_message}

        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}