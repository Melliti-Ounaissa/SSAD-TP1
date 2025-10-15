from backend.database import get_supabase_client
from datetime import datetime


class MessageService:
    def __init__(self):
        self.supabase = get_supabase_client()

    def send_message(self, sender_id, receiver_id, content, encrypted, algo_name):
        try:
            result = self.supabase.table('messages').insert({
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "content": content,
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

    def get_sent_messages(self, user_id):
        try:
            result = self.supabase.table('messages').select(
                'id, date_created, content, encrypted, algo_name, sender_id, receiver_id, users!messages_receiver_id_fkey(email)'
            ).eq('sender_id', user_id).order('date_created', desc=True).execute()

            return {"success": True, "messages": result.data}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def get_received_messages(self, user_id):
        try:
            result = self.supabase.table('messages').select(
                'id, date_created, content, encrypted, algo_name, sender_id, receiver_id, users!messages_sender_id_fkey(email)'
            ).eq('receiver_id', user_id).order('date_created', desc=True).execute()

            return {"success": True, "messages": result.data}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def subscribe_to_messages(self, user_id, callback):
        try:
            def handle_message(payload):
                if payload['eventType'] == 'INSERT':
                    new_message = payload['new']
                    if new_message['receiver_id'] == user_id:
                        callback(new_message)

            subscription = self.supabase.table('messages').on('INSERT', handle_message).subscribe()
            return subscription
        except Exception as e:
            print(f"Subscription error: {str(e)}")
            return None
