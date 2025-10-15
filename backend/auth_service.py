from .database import get_supabase_client


class AuthService:
    def __init__(self):
        self.supabase = get_supabase_client()

    def sign_up(self, email, password):
        try:
            existing_user = self.supabase.table('users').select('*').eq('email', email).execute()

            if existing_user.data and len(existing_user.data) > 0:
                return {"success": False, "message": "User already exists"}

            result = self.supabase.table('users').insert({
                "email": email,
                "password": password
            }).execute()

            if result.data and len(result.data) > 0:
                user = result.data[0]
                return {"success": True, "message": "Sign up successful", "user": user}
            else:
                return {"success": False, "message": "Failed to create user"}

        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def sign_in(self, email, password):
        try:
            result = self.supabase.table('users').select('*').eq('email', email).eq('password', password).execute()

            if result.data and len(result.data) > 0:
                user = result.data[0]
                return {"success": True, "message": "Sign in successful", "user": user}
            else:
                return {"success": False, "message": "User not found, try to sign up!"}

        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def get_all_users_except(self, user_id):
        try:
            result = self.supabase.table('users').select('id, email').neq('id', user_id).execute()
            return {"success": True, "users": result.data}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
