from backend.database import get_supabase_client
from backend.password_validator import PasswordValidator
from fonction_de_hachage_lent import slow_hash, verify_password
from datetime import datetime, timedelta, timezone
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

LOCK_DURATION = timedelta(minutes=10)  # durée du blocage
MAX_FAILED = 3
HASH_ITERATIONS = 10000

def _utc_now():
    return datetime.now(timezone.utc)

def _to_iso_z(dt):
    if dt is None: return None
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def _parse_iso_to_dt(s):
    if not s: return None
    try:
        return datetime.fromisoformat(s.replace("Z","+00:00")).astimezone(timezone.utc)
    except:
        return None

class AuthService:
    def __init__(self):
        self.supabase = get_supabase_client()

    def sign_up(self, username, password):
        ok, _ = PasswordValidator.validate_password(password)
        if not ok:
            return {"success": False, "message": "Invalid password format"}

        if self.supabase.table('users').select('id').eq('username', username).execute().data:
            return {"success": False, "message": "User already exists"}

        password_hash, salt = slow_hash(password, iterations=HASH_ITERATIONS)
        r = self.supabase.table('users').insert({
            "username": username,
            "password_hash": password_hash,
            "password_salt": salt,
            "failed_attempts": 0,
            "locked_until": None
        }).execute()
        if r.data:
            u = r.data[0]
            return {"success": True, "message": "Sign up successful", "user": {"id": u["id"], "username": u["username"]}}
        return {"success": False, "message": "Failed to create user"}

    def get_all_users(self):
        '''Retrieves all users\' public information (id, username).'''
        try:
            result = self.supabase.table('users').select('id, username').execute()
            
            return result.data if result.data else [] 
            
        except Exception as e:
            print(f"Error fetching all users: {str(e)}")
            return []

    def sign_in(self, username, password):
        r = self.supabase.table('users').select('*').eq('username', username).execute()
        if not r.data:
            return {"success": False, "message": "Nom d\'utilisateur ou mot de passe incorrect."}

        user = r.data[0]
        locked_until = _parse_iso_to_dt(user.get("locked_until"))
        if locked_until and _utc_now() < locked_until:
            mins = int((locked_until - _utc_now()).total_seconds() // 60) + 1
            return {"success": False, "message": f"Compte verrouillé. Réessayez dans ~{mins} minute(s)."}

        ok = verify_password(
            stored_hash_hex=user["password_hash"],
            password=password,
            salt_hex=user["password_salt"],
            iterations=HASH_ITERATIONS
        )

        if ok:
            self.supabase.table("users").update({"failed_attempts": 0, "locked_until": None}).eq("id", user["id"]).execute()
            return {"success": True, "message": "Connexion réussie", "user": {"id": user["id"], "username": user["username"]}}

        # mauvais mot de passe -> incrément
        fails = (user.get("failed_attempts") or 0) + 1
        update = {"failed_attempts": fails}
        if fails >= MAX_FAILED:
            update["locked_until"] = _to_iso_z(_utc_now() + LOCK_DURATION)
        self.supabase.table("users").update(update).eq("id", user["id"]).execute()

        if fails >= MAX_FAILED:
            return {"success": False, "message": f"Compte verrouillé après {MAX_FAILED} échecs. Attendez {int(LOCK_DURATION.total_seconds()/60)} min."}
        return {"success": False, "message": f"Mot de passe incorrect. Il vous reste {MAX_FAILED - fails} tentative(s)."}