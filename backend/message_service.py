from .database import get_supabase_client
from datetime import datetime
# from .crypto_service import CryptoService # Assumed this import is available in the real environment

class MessageService:
    # ACCEPT crypto_service in constructor
    def __init__(self, crypto_service):
        self.supabase = get_supabase_client()
        self.crypto_service = crypto_service # STORE crypto_service

    # REMOVE content from parameters, it's not stored
    def send_message(self, sender_id, receiver_id, encrypted, algo_name): 
        try:
            # REMOVE content from insert payload
            result = self.supabase.table('messages').insert({
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "encrypted": encrypted,
                "algo_name": algo_name,
                "date_created": datetime.now().isoformat()
            }).execute()

            if result.data and len(result.data) > 0:
                return {"success": True, "message": "Message sent successfully", "data": result.data[0]}
            else:
                return {"success": False, "message": "Failed to send message"}

        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def _decrypt_messages(self, messages):
        """Helper to decrypt the message content before sending to client."""
        decrypted_messages = []
        for message in messages:
            try:
                # Decrypt the encrypted message using the stored crypto service
                # Note: The decryption function must also take the necessary key/shift parameters if required by the algorithm
                decrypted_content = self.crypto_service.decrypt_message(
                    message['encrypted'], 
                    message['algo_name']
                    # Assuming necessary keys are embedded or handled internally by the crypto service
                )
                # Add the decrypted content back to the message object under the 'content' key 
                message['content'] = decrypted_content
                decrypted_messages.append(message)
            except Exception as e:
                # Log error but return the message with an error content
                print(f"Decryption Error for message ID {message['id']}: {e}")
                message['content'] = f"Decryption Error: {e}"
                decrypted_messages.append(message)
        return decrypted_messages


    def get_sent_messages(self, user_id):
        try:
            # Select username instead of email for the receiver (users!messages_receiver_id_fkey)
            # Content is removed from select as it no longer exists in the table.
            result = self.supabase.table('messages').select(
                'id, date_created, encrypted, algo_name, sender_id, receiver_id, users!messages_receiver_id_fkey(username)' # CHANGED 'content' removal, 'email' to 'username'
            ).eq('sender_id', user_id).order('date_created', desc=True).execute()

            if result.data:
                # Decrypt messages before returning
                return {"success": True, "messages": self._decrypt_messages(result.data)}
            
            return {"success": True, "messages": []}
            
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def get_received_messages(self, user_id):
        try:
            # Select username instead of email for the sender (users!messages_sender_id_fkey)
            # Content is removed from select as it no longer exists in the table.
            result = self.supabase.table('messages').select(
                'id, date_created, encrypted, algo_name, sender_id, receiver_id, users!messages_sender_id_fkey(username)' # CHANGED 'content' removal, 'email' to 'username'
            ).eq('receiver_id', user_id).order('date_created', desc=True).execute()

            if result.data:
                # Decrypt messages before returning
                return {"success": True, "messages": self._decrypt_messages(result.data)}
            
            return {"success": True, "messages": []}

        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def subscribe_to_messages(self, user_id, callback):
        # NOTE: This implementation assumes the crypto_service and decryption keys are available 
        # for real-time processing as well.
        try:
            # Helper to handle decryption of a single new message
            def decrypt_and_callback(new_message):
                 # Temporarily wrap in a list to use _decrypt_messages helper
                decrypted_list = self._decrypt_messages([new_message]) 
                if decrypted_list:
                    callback(decrypted_list[0])

            def handle_message(payload):
                if payload['eventType'] == 'INSERT':
                    new_message = payload['new']
                    if new_message['receiver_id'] == user_id:
                        decrypt_and_callback(new_message)

            subscription = self.supabase.table('messages').on('INSERT', handle_message).subscribe()
            return subscription
        except Exception as e:
            print(f"Subscription Error: {str(e)}")
            return None
