from backend.database import get_supabase_client
from datetime import datetime


class MessageService:
    def __init__(self, crypto_service=None):
        self.supabase = get_supabase_client()
        self.crypto_service = crypto_service

    def send_message(self, sender_id, receiver_id, encrypted, algo_name, algorithm_key=None):
        try:
            message_data = {
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "encrypted": encrypted,
                "algo_name": algo_name,
                "date_created": datetime.now().isoformat()
            }

            if algorithm_key:
                message_data["algorithm_key"] = algorithm_key

            result = self.supabase.table('messages').insert(message_data).execute()

            if result.data and len(result.data) > 0:
                return {"success": True, "message": "Message sent successfully", "data": result.data[0]}
            else:
                return {"success": False, "message": "Failed to send message"}

        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}"}

    def get_conversation(self, user1_id, user2_id):
        try:
            # Query messages between two users with proper joins
            result = self.supabase.table('messages').select(
                '''
                id,
                date_created,
                encrypted,
                algo_name,
                algorithm_key,
                sender_id,
                receiver_id,
                sender:users!messages_sender_id_fkey(id, username),
                receiver:users!messages_receiver_id_fkey(id, username)
                '''
            ).or_(
                f'and(sender_id.eq.{user1_id},receiver_id.eq.{user2_id}),and(sender_id.eq.{user2_id},receiver_id.eq.{user1_id})'
            ).order('date_created', desc=False).execute()

            messages = result.data if result.data else []
            
            # Debug: Print to console
            print(f"Loading conversation between {user1_id} and {user2_id}")
            print(f"Found {len(messages)} messages")
            
            return {"success": True, "messages": messages}
        except Exception as e:
            print(f"Error loading conversation: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}", "messages": []}

    def get_all_conversations(self, user_id):
        try:
            result = self.supabase.table('messages').select(
                '''
                id,
                date_created,
                encrypted,
                algo_name,
                algorithm_key,
                sender_id,
                receiver_id,
                sender:users!messages_sender_id_fkey(id, username),
                receiver:users!messages_receiver_id_fkey(id, username)
                '''
            ).or_(
                f'sender_id.eq.{user_id},receiver_id.eq.{user_id}'
            ).order('date_created', desc=False).execute()

            return {"success": True, "messages": result.data if result.data else []}
        except Exception as e:
            print(f"Error getting all conversations: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}"}

    def get_sent_messages(self, user_id):
        try:
            result = self.supabase.table('messages').select(
                '''
                id,
                date_created,
                encrypted,
                algo_name,
                algorithm_key,
                sender_id,
                receiver_id,
                receiver:users!messages_receiver_id_fkey(username)
                '''
            ).eq('sender_id', user_id).order('date_created', desc=True).execute()

            return {"success": True, "messages": result.data if result.data else []}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def get_received_messages(self, user_id):
        try:
            result = self.supabase.table('messages').select(
                '''
                id,
                date_created,
                encrypted,
                algo_name,
                algorithm_key,
                sender_id,
                receiver_id,
                sender:users!messages_sender_id_fkey(username)
                '''
            ).eq('receiver_id', user_id).order('date_created', desc=True).execute()

            return {"success": True, "messages": result.data if result.data else []}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}