import time
import hashlib
import os
import sys

# --- Target Password Setup (For Simulation ONLY) ---
# A common dictionary word with a simple modification (capital 'P', 'o' -> '0')
TARGET_PASSWORD = "444"
TARGET_HASH = hashlib.sha256(TARGET_PASSWORD.encode()).hexdigest()
# ----------------------------------------------------

def check_password(candidate_password, target_hash):
    """
    Simulates the authentication check.
    """
    candidate_hash = hashlib.sha256(candidate_password.encode()).hexdigest()
    return candidate_hash == target_hash

def load_wordlist(preferred_paths=None):
    """
    Load a wordlist from disk. Tries a list of candidate paths and returns
    the first one found as a list of stripped lines.

    Preference order defaults to ['worldlist.txt', 'password/wordlist.txt']
    to accommodate the user's requested filename and the existing workspace.
    """
    if preferred_paths is None:
        preferred_paths = [
            os.path.join(os.getcwd(), 'worldlist3.txt'),

        ]

    for path in preferred_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    words = [line.strip() for line in f if line.strip()]
                print(f"[*] Loaded wordlist from: {path} ({len(words)} entries)")
                return words
            except Exception as e:
                print(f"[!] Error reading wordlist {path}: {e}")

    # If we reach here, no wordlist was found
    print("[!] No wordlist found. Please provide 'worldlist.txt' or 'password/wordlist.txt' in the workspace.")
    return []

def dictionary_and_hybrid_attack(target_hash):
    """
    Implements a pure dictionary attack that reads candidates from an
    external wordlist on disk. All hybrid/modification rules have been
    removed per user request.
    """
    DICTIONARY = load_wordlist()

    if not DICTIONARY:
        return None

    print(f"[*] Starting Dictionary Attack simulation (pure dictionary only)...")
    start_time = time.time()
    attempts = 0

    print("\n--- Phase 1: Pure Dictionary Test ---")
    for word in DICTIONARY:
        attempts += 1
        if check_password(word, target_hash):
            end_time = time.time()
            elapsed = end_time - start_time
            print(f"\n[+] SUCCESS! Password found: '{word}' (Pure Dictionary)")
            print(f"[#] Attempts: {attempts}")
            print(f"[#] Time taken: {elapsed:.4f} seconds")
            return word

        # Optional: Print progress every 1000 attempts to avoid flooding
        if attempts % 1000 == 0:
            print(f"    Tested {attempts} candidates...", end='\r')

    end_time = time.time()
    elapsed = end_time - start_time
    print(f"\n[-] FAILED. Password not found after {attempts} attempts.")
    print(f"[#] Time taken: {elapsed:.4f} seconds")
    return None

# Execute the simulation
dictionary_and_hybrid_attack(TARGET_HASH)
