import time

import os
from itertools import product
from fonction_de_hachage_lent import verify_password


class PasswordAttackService:
    def __init__(self, wordlist_path='wordlist.txt'):
        self.wordlist_path = wordlist_path
        self.progress_callback = None  # add callback for progress updates

    # ---------------------------
    # Dictionary attack: 3-char only
    # ---------------------------
    def dictionary3_attack(self, stored_hash, salt, username):
        """Dictionary attack for 3 character passwords only."""
        print(f"\n[*] Starting Dictionary 3-char Attack for user: {username}")
        start_time = time.time()
        attempts = 0

        wordlist_path = os.path.join('Attacks', 'worldlist3.txt')
        if not os.path.exists(wordlist_path):
            print(f"[!] Wordlist not found: {wordlist_path}")
            return {"success": False, "attempts": 0, "duration": 0, "method": "dictionary3"}

        with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            words = [line.strip() for line in f if line.strip()]

        for password in words:
            attempts += 1
            if verify_password(stored_hash, password, salt):
                elapsed = time.time() - start_time
                print(f"[+] SUCCESS! Password found: '{password}' after {attempts} attempts")
                return {
                    "success": True,
                    "found": True,
                    "password": password,
                    "attempts": attempts,
                    "processed": attempts,
                    "total": len(words),
                    "duration": elapsed,
                    "method": "dictionary3"
                }

        elapsed = time.time() - start_time
        print(f"[-] FAILED. Password not found after {attempts} attempts.")
        return {
            "success": False,
            "found": False,
            "attempts": attempts,
            "processed": attempts,
            "total": len(words),
            "duration": elapsed,
            "method": "dictionary3"
        }
    # ---------------------------
    # Brute force attack (5 or 6 chars)
    # ---------------------------
    def brute_force_attack(self, stored_hash, salt, username, length=5):
        """
        Brute force attack for passwords of specified length (5 or 6 chars)
        5-char: digits only (0-9) = 10 characters, 100,000 combinations
        6-char: a-z, A-Z, 0-9, +, * = 64 characters, 68 billion combinations
        
        CRITICAL: Breaks immediately when password is found - NO CONTINUED PROCESSING
        """
        print(f"\n[*] Starting Brute Force Attack ({length}-char) for user: {username}")
        
        if length == 5:
            CHAR_SET = '0123456789'  # 5-char passwords are digits only
        else:  # length == 6
            CHAR_SET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789*+'
        
        total_combinations = len(CHAR_SET) ** length
        print(f"[*] Character set: {CHAR_SET}")
        print(f"[*] Total combinations: {total_combinations:,}")

        attempts = 0
        start_time = time.time()

        for combination in product(CHAR_SET, repeat=length):
            candidate = ''.join(combination)
            attempts += 1

            if verify_password(stored_hash, candidate, salt):
                elapsed = time.time() - start_time
                print(f"[+] SUCCESS! Password found: '{candidate}' after {attempts} attempts in {elapsed:.3f}s")
                if self.progress_callback:
                    self.progress_callback({
                        "status": "found",
                        "attempts": attempts,
                        "processed": attempts,
                        "total": total_combinations,
                        "percentage": 100,
                        "password": candidate
                    })
                return {
                    "success": True,
                    "found": True,
                    "password": candidate,
                    "attempts": attempts,
                    "processed": attempts,
                    "total": total_combinations,
                    "duration": elapsed,
                    "method": f"bruteforce_{length}char"
                }

            if attempts % 1000 == 0:
                elapsed = time.time() - start_time
                rate = attempts / elapsed if elapsed > 0 else 0
                percentage = int((attempts / total_combinations) * 100)
                progress_msg = f"    Progress: {candidate} ({attempts:,}/{total_combinations:,} | {percentage}% | {rate:.0f} attempts/sec)"
                print(progress_msg)
                if self.progress_callback:
                    self.progress_callback({
                        "status": "progress",
                        "attempts": attempts,
                        "processed": attempts,
                        "total": total_combinations,
                        "percentage": percentage,
                        "candidate": candidate,
                        "rate": rate
                    })

        elapsed = time.time() - start_time
        print(f"[-] FAILED. Password not found after {attempts:,} attempts in {elapsed:.3f}s")
        return {
            "success": False,
            "found": False,
            "attempts": attempts,
            "processed": attempts,
            "total": total_combinations,
            "duration": elapsed,
            "method": f"bruteforce_{length}char"
        }

    # ---------------------------
    # Smart attack: dict3 first, then brute force 5 and 6
    # ---------------------------
    def smart_attack(self, stored_hash, salt, username):
        """
        Smart attack that tries dictionary3 first, then brute force 5-char and 6-char
        """
        print(f"\n[*] Starting Smart Attack for user: {username}")

        # Try dictionary3 first
        result = self.dictionary3_attack(stored_hash, salt, username)
        if result["success"]:
            return result

        # If failed, try brute force for 5-char then 6-char passwords
        for length in [5, 6]:
            result = self.brute_force_attack(stored_hash, salt, username, length=length)
            if result["success"]:
                return result

        return {
            "success": False,
            "found": False,
            "attempts": result.get("attempts", 0),
            "duration": result.get("duration", 0),
            "method": "smart_attack"
        }
