import threading, queue, time
from flask import Blueprint, request, jsonify, current_app
from backend.password_attack_service import PasswordAttackService

attacks_bp = Blueprint("attacks", __name__, url_prefix="/api/attacks")

# Initialize the service (pass your wordlist)
password_attack_service = PasswordAttackService(wordlist_path="worldlist5.txt")


# --- Helper: run any attack with timeout ---
def run_with_timeout(fn, args=(), kwargs=None, timeout=30):
    q = queue.Queue()

    def worker():
        try:
            res = fn(*args, **(kwargs or {}))
            q.put((True, res))
        except Exception as e:
            q.put((False, str(e)))

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    try:
        success, payload = q.get(timeout=timeout)
        if not success:
            raise RuntimeError(payload)
        return payload
    except queue.Empty:
        raise TimeoutError(f"Attack timed out after {timeout}s")


# --- Endpoint: POST /api/attacks/bruteforce ---
@attacks_bp.route("/bruteforce", methods=["POST"])
def run_bruteforce():
    data = request.get_json(force=True)
    target_hash = data.get("target_hash")
    length = int(data.get("length", 0))

    if length not in (5, 6):
        return jsonify({"success": False, "error": "Length must be 5 or 6"}), 400

    timeout = current_app.config.get("ATTACK_TIMEOUT", 300)
    try:
        result = run_with_timeout(
            password_attack_service.brute_force_attack,
            args=(target_hash, None, None, length),
            timeout=timeout
        )
    except TimeoutError as te:
        return jsonify({"success": False, "error": str(te)}), 504
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    return jsonify({"success": True, "result": result})


# --- Endpoint: POST /api/attacks/dictionary ---
@attacks_bp.route("/dictionary", methods=["POST"])
def run_dictionary():
    data = request.get_json(force=True)
    target_hash = data.get("target_hash")
    method = data.get("method", "dictionary3")
    timeout = current_app.config.get("ATTACK_TIMEOUT", 120)

    if method != "dictionary3":
        return jsonify({"success": False, "error": f"Only 'dictionary3' is supported now"}), 400

    try:
        result = run_with_timeout(password_attack_service.dictionary3_attack, args=(target_hash,), timeout=timeout)
    except TimeoutError as te:
        return jsonify({"success": False, "error": str(te)}), 504
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    return jsonify({"success": True, "result": result})
