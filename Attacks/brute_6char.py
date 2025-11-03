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

def brute_force_5_digit_password(target_hash):
    """
    Implements the brute force algorithm for 5-digit numerical passwords.
    This simulates iterating from 00000 to 99999.
    """
    PASSWORD_LENGTH = 6
    # The digits '0' through '9'
    CHAR_SET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789*+'
    # Total combinations: 10^5 = 100,000
    
    print(f"[*] Starting Brute Force simulation for {PASSWORD_LENGTH} digit password...")
    
    start_time = time.time()
    attempts = 0

    # Iterating over the product of digits provides the necessary strings
    for combination in product(CHAR_SET, repeat=PASSWORD_LENGTH):
        candidate = "".join(combination)
        attempts += 1

        if check_password(candidate, target_hash):
            end_time = time.time()
            elapsed = end_time - start_time
            print(f"\n[+] SUCCESS! Password found: '{candidate}'")
            print(f"[#] Attempts: {attempts}")
            print(f"[#] Time taken: {elapsed:.4f} seconds")
            return candidate

        # Update progress less often as this loop is much faster
        if attempts % 10000 == 0:
            print(f"    Attempting: {candidate} ({attempts} attempts)", end='\r')

    end_time = time.time()
    elapsed = end_time - start_time
    print(f"\n[-] FAILED. Password not found after {attempts} attempts.")
    print(f"[#] Time taken: {elapsed:.4f} seconds")
    return None

# Execute the simulation
brute_force_5_digit_password(TARGET_HASH)
