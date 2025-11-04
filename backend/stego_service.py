from backend.database import get_supabase_client
from datetime import datetime
import os
import sys
import wave
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from steganography.steganography import hide_in_audio, extract_from_audio, text_to_binary


class StegoService:
    def __init__(self):
        self.supabase = get_supabase_client()

    def analyze_audio_file(self, file_path):
        '''
        Analyze an audio file and return detailed information
        '''
        try:
            with wave.open(file_path, 'rb') as wav:
                n_channels = wav.getnchannels()
                sample_width = wav.getsampwidth()
                framerate = wav.getframerate()
                n_frames = wav.getnframes()
                duration = n_frames / float(framerate)
                
                return {
                    "success": True,
                    "channels": n_channels,
                    "sample_width": sample_width,
                    "framerate": framerate,
                    "n_frames": n_frames,
                    "duration": duration,
                    "capacity_bits": n_frames,
                    "capacity_chars": n_frames // 8
                }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }

    def get_lsb_comparison(self, original_path, stego_path, secret_message):
        '''Compare LSB changes between original and steganographed audio'''
        try:
            # Read original audio (avec fermeture automatique)
            with wave.open(original_path, 'rb') as audio_orig:
                frames_orig = audio_orig.readframes(audio_orig.getnframes())
            audio_data_original = np.frombuffer(frames_orig, dtype=np.int16)

            # Read steganographed audio (avec fermeture automatique)
            with wave.open(stego_path, 'rb') as audio_stego:
                frames_stego = audio_stego.readframes(audio_stego.getnframes())
            audio_data_modified = np.frombuffer(frames_stego, dtype=np.int16)

            # Get binary message
            message_with_end = secret_message + "###END###"
            binary_message = text_to_binary(message_with_end)
            
            # Collect sample data
            samples = []

            for i in range(len(binary_message)):
                original = int(audio_data_original[i])
                modified = int(audio_data_modified[i])
                lsb_before = original & 1
                lsb_after = modified & 1
                message_bit = binary_message[i]
                changed = original != modified

                samples.append({
                    "index": i,
                    "original": original,
                    "modified": modified,
                    "lsb_before": lsb_before,
                    "lsb_after": lsb_after,
                    "message_bit": message_bit,
                    "changed": changed
                })

            # Calculate statistics
            total_changes = sum(1 for i in range(len(binary_message)) 
                            if audio_data_original[i] != audio_data_modified[i])

            return {
                "success": True,
                "samples": samples,
                "binary_message": binary_message,
                "message_length_bits": len(binary_message),
                "total_changes": total_changes,
                "change_percentage": (total_changes / len(binary_message)) * 100
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": str(e)
            }

    def hide_message_and_save_from_temp(self, temp_path, secret_message, sender_id, receiver_id, upload_folder):
        '''Hide message in audio from temporary file and save to database'''
        try:
            # Generate unique filename
            import time
            timestamp = int(time.time() * 1000)
            output_filename = f"stego{sender_id}{timestamp}.wav"
            output_path = os.path.join(upload_folder, output_filename)

            # Analyze original audio (avec fermeture automatique)
            original_analysis = self.analyze_audio_file(temp_path)

            # Check message capacity
            message_with_end = secret_message + "###END###"
            binary_message = text_to_binary(message_with_end)
            message_bits = len(binary_message)

            if message_bits > original_analysis['capacity_bits']:
                return {
                    "success": False,
                    "message": f"Message trop long ! Besoin de {message_bits} bits, l'audio a {original_analysis['capacity_bits']} bits."
                }
            
            # Hide message in audio (cette fonction ferme déjà les fichiers correctement)
            hide_in_audio(temp_path, secret_message, output_path)

            # Verify output file was created
            if not os.path.exists(output_path):
                return {"success": False, "message": "Échec de création du fichier stéganographié"}

            # Analyze modified audio
            stego_analysis = self.analyze_audio_file(output_path)

            # Get LSB comparison
            lsb_comparison = self.get_lsb_comparison(temp_path, output_path, secret_message)

            # Save to database
            message_data = {
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "audio_filename": output_filename,
                "date_created": datetime.now().isoformat()
            }

            result = self.supabase.table('stego_messages').insert(message_data).execute()

            if result.data and len(result.data) > 0:
                return {
                    "success": True,
                    "message": "Message stéganographié envoyé avec succès",
                    "data": result.data[0],
                    "analysis": {
                        "original": original_analysis,
                        "modified": stego_analysis,
                        "lsb_comparison": lsb_comparison,
                        "message_hidden": secret_message,
                        "message_length": len(secret_message),
                        "binary_length": message_bits
                    }
                }
            else:
                # Clean up file if database save failed
                if os.path.exists(output_path):
                    os.remove(output_path)
                return {"success": False, "message": "Échec de sauvegarde en base de données"}

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "message": f"Erreur: {str(e)}"}

    def hide_message_and_save(self, audio_file, secret_message, sender_id, receiver_id, upload_folder):
        '''Hide message in audio and save to database (legacy method)'''
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
        '''Get all steganography messages for a user'''
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
        '''Extract hidden message from audio file'''
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