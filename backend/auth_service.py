from backend.database import get_supabase_client
from backend.password_validator import PasswordValidator
from fonction_de_hachage_lent import slow_hash, verify_password
import sys
import os




sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



class AuthService:
    def __init__(self):
        self.supabase = get_supabase_client()

    def sign_up(self, username, password):
        try:
            # Validate password format
            is_valid, validation_message = PasswordValidator.validate_password(password)
            if not is_valid:
                return {"success": False, "message": "Invalid password format"}

            # Check if user already exists
            existing_user = self.supabase.table('users').select('*').eq('username', username).execute()

            if existing_user.data and len(existing_user.data) > 0:
                return {"success": False, "message": "User already exists"}

            # Hash the password with salt
            password_hash, salt = slow_hash(password, iterations=10000)
            
            # Store username, hash, and salt in database
            result = self.supabase.table('users').insert({
                "username": username,
                "password_hash": password_hash,
                "password_salt": salt
            }).execute()

            if result.data and len(result.data) > 0:
                user = result.data[0]
                # Don't send hash/salt to client
                safe_user = {
                    "id": user["id"],
                    "username": user["username"]
                }
                return {"success": True, "message": "Sign up successful", "user": safe_user}
            else:
                return {"success": False, "message": "Failed to create user"}

        except Exception as e:
            print(f"Sign up error: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}"}

    def sign_in(self, username, password):
        try:
            # Retrieve user with hash and salt
            result = self.supabase.table('users').select('*').eq('username', username).execute()

            if not result.data or len(result.data) == 0:
                return {"success": False, "message": "User not found, try to sign up!"}

            user = result.data[0]
            
            # Verify password using stored hash and salt
            is_valid = verify_password(
                stored_hash_hex=user['password_hash'],
                password=password,
                salt_hex=user['password_salt'],
                iterations=10000
            )

            if is_valid:
                # Don't send hash/salt to client
                safe_user = {
                    "id": user["id"],
                    "username": user["username"]
                }
                return {"success": True, "message": "Sign in successful", "user": safe_user}
            else:
                return {"success": False, "message": "Invalid password"}

        except Exception as e:
            print(f"Sign in error: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}"}

    def get_all_users(self):
        """Get all users including current user"""
        try:
            result = self.supabase.table('users').select('id, username').execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error: {str(e)}")
            return []

    def get_all_users_except(self, user_id):
        """Get all users except specified user (kept for backward compatibility)"""
        try:
            result = self.supabase.table('users').select('id, username').neq('id', user_id).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error: {str(e)}")
            return []