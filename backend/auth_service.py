from backend.database import get_supabase_client
from backend.password_validator import PasswordValidator


class AuthService:
    def __init__(self):
        self.supabase = get_supabase_client()

    def sign_up(self, username, password):
        try:
            is_valid, validation_message = PasswordValidator.validate_password(password)
            if not is_valid:
                return {"success": False, "message": "Invalid password"}

            existing_user = self.supabase.table('users').select('*').eq('username', username).execute()

            if existing_user.data and len(existing_user.data) > 0:
                return {"success": False, "message": "User already exists"}

            result = self.supabase.table('users').insert({
                "username": username,
                "password": password
            }).execute()

            if result.data and len(result.data) > 0:
                user = result.data[0]
                return {"success": True, "message": "Sign up successful", "user": user}
            else:
                return {"success": False, "message": "Failed to create user"}

        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def sign_in(self, username, password):
        try:
            result = self.supabase.table('users').select('*').eq('username', username).eq('password', password).execute()

            if result.data and len(result.data) > 0:
                user = result.data[0]
                return {"success": True, "message": "Sign in successful", "user": user}
            else:
                return {"success": False, "message": "User not found, try to sign up!"}

        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def get_all_users_except(self, user_id):
        try:
            result = self.supabase.table('users').select('id, username').neq('id', user_id).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error: {str(e)}")
            return []
