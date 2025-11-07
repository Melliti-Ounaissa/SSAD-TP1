# debug_attack.py
import time
import hashlib
import os
import sys
import argparse

# --- Target Password Setup (For Simulation ONLY) ---
TARGET_PASSWORD = "44444"
TARGET_HASH = hashlib.sha256(TARGET_PASSWORD.encode()).hexdigest()
# ----------------------------------------------------

def check_password(candidate_password, target_hash):
    candidate_hash = hashlib.sha256(candidate_password.encode()).hexdigest()
    return candidate_hash == target_hash

def load_wordlist(preferred_paths=None):
    if preferred_paths is None:
        preferred_paths = [ os.path.join(os.getcwd(), 'worldlist5.txt') ]

    for path in preferred_paths:
        print(f"[*] Checking for file at: {path}", flush=True)
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    words = [line.rstrip("\n\r") for line in f if line.strip() or line == ""]
                print(f"[*] Loaded wordlist from: {path} ({len(words)} entries)", flush=True)
                return words
            except Exception as e:
                print(f"[!] Error reading wordlist {path}: {e}", flush=True)

    print("[!] No wordlist found. Please provide 'worldlist5.txt' in the workspace.", flush=True)
    return []

def dictionary_and_hybrid_attack(target_hash, debug_max_attempts=None):
    DICTIONARY = load_wordlist()
    if not DICTIONARY:
        return None

    print("\n--- Sample candidates (first 20, shown with repr) ---", flush=True)
    for i, w in enumerate(DICTIONARY[:20], start=1):
        print(f"#{i}: {repr(w)}", flush=True)
    print("--- End sample ---\n", flush=True)

    sample = DICTIONARY[0] if DICTIONARY else "test"
    t0 = time.time()
    check_password(sample, target_hash)
    t_single = time.time() - t0
    print(f"[i] Single check time (micro-benchmark): {t_single:.6f} seconds", flush=True)

    print(f"[*] Starting Dictionary Attack simulation (pure dictionary only)...", flush=True)
    start_time = time.time()
    attempts = 0
    progress_interval = max(1, len(DICTIONARY) // 100 if len(DICTIONARY) < 100000 else 1000)

    for word in DICTIONARY:
        attempts += 1

        if check_password(word, target_hash):
            elapsed = time.time() - start_time
            print(f"\n[+] SUCCESS! Password found: {repr(word)} (Pure Dictionary)", flush=True)
            print(f"[#] Attempts: {attempts}", flush=True)
            print(f"[#] Time taken: {elapsed:.4f} seconds", flush=True)
            return word

        if (attempts <= 20) or (attempts % progress_interval == 0) or (attempts % 1000 == 0):
            elapsed = time.time() - start_time
            print(f"[progress] attempts={attempts}, elapsed={elapsed:.2f}s", flush=True)

        if debug_max_attempts is not None and attempts >= debug_max_attempts:
            print(f"[debug] reached debug_max_attempts={debug_max_attempts}; stopping early.", flush=True)
            break

    elapsed = time.time() - start_time
    print(f"\n[-] FAILED. Password not found after {attempts} attempts.", flush=True)
    print(f"[#] Time taken: {elapsed:.4f} seconds", flush=True)
    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--max", type=int, default=None, help="Optional debug cap on attempts (e.g. --max 1000)")
    args = parser.parse_args()
    dictionary_and_hybrid_attack(TARGET_HASH, debug_max_attempts=args.max)
