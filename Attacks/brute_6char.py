import time
import hashlib
from itertools import product

# --- Target Password Setup (For Simulation ONLY) ---
TARGET_PASSWORD = "aaaaaa"
TARGET_HASH = hashlib.sha256(TARGET_PASSWORD.encode()).hexdigest()
# ----------------------------------------------------

def check_password(candidate_password, target_hash):
    """
    Simulates the authentication check.
    """
    candidate_hash = hashlib.sha256(candidate_password.encode()).hexdigest()
    return candidate_hash == target_hash

def brute_force_6_char_password(target_hash):
    """
    Implements the brute force algorithm for 6-character passwords.
    Character set: a-z, A-Z, 0-9, +, * (64 characters)
    Total combinations: 64^6 ≈ 68 billion (very large)
    """
    PASSWORD_LENGTH = 6
    CHAR_SET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789*+'
    TOTAL_COMBOS = len(CHAR_SET) ** PASSWORD_LENGTH
    
    print(f"[*] Starting Brute Force simulation for {PASSWORD_LENGTH} character password...")
    print(f"[*] Character set: {CHAR_SET}")
    print(f"[*] Total combinations: {TOTAL_COMBOS:,}")
    
    start_time = time.time()
    attempts = 0

    # Iterating over the product of characters provides the necessary strings
    for combination in product(CHAR_SET, repeat=PASSWORD_LENGTH):
        candidate = "".join(combination)
        attempts += 1

        # Update progress BEFORE checking password
        if attempts % 10000 == 0 or attempts <= 10:
            elapsed = time.time() - start_time
            rate = attempts / elapsed if elapsed > 0 else 0
            print(f"    Attempting: {candidate} ({attempts:,} attempts, {rate:.0f} attempts/sec)", end='\r')

        if check_password(candidate, target_hash):
            end_time = time.time()
            elapsed = end_time - start_time
            print(f"\n[+] SUCCESS! Password found: '{candidate}'")
            print(f"[#] Attempts: {attempts:,}")
            print(f"[#] Time taken: {elapsed:.4f} seconds")
            return candidate

    end_time = time.time()
    elapsed = end_time - start_time
    print(f"\n[-] FAILED. Password not found after {attempts:,} attempts.")
    print(f"[#] Time taken: {elapsed:.4f} seconds")
    return None

# Execute the simulation
brute_force_6_char_password(TARGET_HASH)
