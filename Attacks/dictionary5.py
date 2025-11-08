import time
import hashlib
from itertools import product

# --- Target Password Setup (For Simulation ONLY) ---
TARGET_PASSWORD = "00000"

TARGET_HASH = hashlib.sha256(TARGET_PASSWORD.encode()).hexdigest()
# ----------------------------------------------------

def check_password(candidate_password, target_hash):
    """
    Simulates the authentication check.
    """
    candidate_hash = hashlib.sha256(candidate_password.encode()).hexdigest()
    return candidate_hash == target_hash

def brute_force_5_char_password(target_hash):
    """
    Implements the brute force algorithm for 5-character passwords.
    Character set: 0-9 (10 characters)
    Total combinations: 10^5 = 100,000
    """
    PASSWORD_LENGTH = 5
    CHAR_SET = '0123456789'
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

        # Print every 100 attempts BEFORE checking password
        if attempts % 100 == 0 or attempts <= 10:
            elapsed = time.time() - start_time
            rate = attempts / elapsed if elapsed > 0 else 0
            print(f"    Attempting: {candidate} ({attempts:,} attempts, {rate:.0f} attempts/sec)")

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

brute_force_5_char_password(TARGET_HASH)

