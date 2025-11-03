import time
import hashlib
import os
from itertools import product
from fonction_de_hachage_lent import verify_password


class PasswordAttackService:
    def __init__(self, wordlist_path='wordlist.txt'):
        self.wordlist_path = wordlist_path
        self.worldlist3_path = 'Attacks/worldlist3.txt'
        self.worldlist5_path = 'Attacks/worldlist5.txt'
    
    def load_wordlist(self, filepath):
        """Load wordlist from file"""
        if not os.path.exists(filepath):
            print(f"[!] Wordlist not found: {filepath}")
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                words = [line.strip() for line in f if line.strip()]
            print(f"[*] Loaded wordlist from: {filepath} ({len(words)} entries)")
            return words
        except Exception as e:
            print(f"[!] Error reading wordlist {filepath}: {e}")
            return []
    
    def dictionary_attack(self, stored_hash, salt, username):
        """
        Dictionary attack for 3 and 5 character passwords
        """
        print(f"\n[*] Starting Dictionary Attack for user: {username}")
        start_time = time.time()
        attempts = 0
        
        # Try 3-character dictionary first
        print("[*] Phase 1: Testing 3-character passwords...")
        wordlist_3 = self.load_wordlist(self.worldlist3_path)
        
        for password in wordlist_3:
            attempts += 1
            if verify_password(stored_hash, password, salt, iterations=10000):
                elapsed = time.time() - start_time
                print(f"\n[+] SUCCESS! Password found: '{password}'")
                print(f"[#] Attempts: {attempts}")
                print(f"[#] Time taken: {elapsed:.4f} seconds")
                return {
                    "success": True,
                    "password": password,
                    "attempts": attempts,
                    "duration": elapsed,
                    "method": "dictionary_3char"
                }
            
            if attempts % 100 == 0:
                print(f"    Tested {attempts} passwords...", end='\r')
        
        # Try 5-digit dictionary
        print("\n[*] Phase 2: Testing 5-digit passwords...")
        wordlist_5 = self.load_wordlist(self.worldlist5_path)
        
        for password in wordlist_5:
            attempts += 1
            if verify_password(stored_hash, password, salt, iterations=10000):
                elapsed = time.time() - start_time
                print(f"\n[+] SUCCESS! Password found: '{password}'")
                print(f"[#] Attempts: {attempts}")
                print(f"[#] Time taken: {elapsed:.4f} seconds")
                return {
                    "success": True,
                    "password": password,
                    "attempts": attempts,
                    "duration": elapsed,
                    "method": "dictionary_5digit"
                }
            
            if attempts % 1000 == 0:
                print(f"    Tested {attempts} passwords...", end='\r')
        
        elapsed = time.time() - start_time
        print(f"\n[-] FAILED. Password not found after {attempts} attempts.")
        print(f"[#] Time taken: {elapsed:.4f} seconds")
        
        return {
            "success": False,
            "attempts": attempts,
            "duration": elapsed,
            "method": "dictionary"
        }
        
    def dictionary3_attack(self, stored_hash, salt, username):
        """
        Dictionary attack for 3 character passwords only.
        """
        print(f"\n[*] Starting Dictionary 3-char Attack for user: {username}")
        start_time = time.time()
        attempts = 0
        
        WORDS = self.load_wordlist(self.worldlist3_path)
        
        for password in WORDS:
            attempts += 1
            # BUG 1 FIX: Swapped arguments
            if verify_password(stored_hash, password, salt):
                elapsed = time.time() - start_time
                print(f"[+] SUCCESS! Password found: '{password}' (Method: dictionary3)")
                print(f"[#] Attempts: {attempts}")
                print(f"[#] Time taken: {elapsed:.4f} seconds")
                return {
                    "success": True,
                    "password": password,
                    "attempts": attempts,
                    "duration": elapsed,
                    "method": "dictionary3"
                }

        elapsed = time.time() - start_time
        print(f"\n[-] FAILED. Password not found after {attempts:,} attempts. (Method: dictionary3)")
        return {
            "success": False,
            "attempts": attempts,
            "duration": elapsed,
            "method": "dictionary3"
        }

    def dictionary5_attack(self, stored_hash, salt, username):
        """
        Dictionary attack for 5 character passwords only.
        """
        print(f"\n[*] Starting Dictionary 5-char Attack for user: {username}")
        start_time = time.time()
        attempts = 0
        
        WORDS = self.load_wordlist(self.worldlist5_path)
        
        for password in WORDS:
            attempts += 1
            # BUG 1 FIX: Swapped arguments
            if verify_password(stored_hash, password, salt):
                elapsed = time.time() - start_time
                print(f"[+] SUCCESS! Password found: '{password}' (Method: dictionary5)")
                print(f"[#] Attempts: {attempts}")
                print(f"[#] Time taken: {elapsed:.4f} seconds")
                return {
                    "success": True,
                    "password": password,
                    "attempts": attempts,
                    "duration": elapsed,
                    "method": "dictionary5"
                }

        elapsed = time.time() - start_time
        print(f"\n[-] FAILED. Password not found after {attempts:,} attempts. (Method: dictionary5)")
        return {
            "success": False,
            "attempts": attempts,
            "duration": elapsed,
            "method": "dictionary5"
        }
    
    # BUG 2 FIX: Renamed function
    def brute_force_6char_attack(self, stored_hash, salt, username):
        """
        Brute force attack for 6-character passwords
        Uses the character set: a-z, A-Z, 0-9, +, *
        """
        print(f"\n[*] Starting Brute Force Attack for user: {username}")
        PASSWORD_LENGTH = 6
        CHAR_SET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789*+'
        
        print(f"[*] Character set: {CHAR_SET}")
        print(f"[*] Password length: {PASSWORD_LENGTH}")
        print(f"[*] Total combinations: {len(CHAR_SET) ** PASSWORD_LENGTH:,}")
        
        start_time = time.time()
        attempts = 0
        
        for combination in product(CHAR_SET, repeat=PASSWORD_LENGTH):
            candidate = "".join(combination)
            attempts += 1
            
            if verify_password(stored_hash, candidate, salt, iterations=10000):
                elapsed = time.time() - start_time
                print(f"\n[+] SUCCESS! Password found: '{candidate}'")
                print(f"[#] Attempts: {attempts}")
                print(f"[#] Time taken: {elapsed:.4f} seconds")
                return {
                    "success": True,
                    "password": candidate,
                    "attempts": attempts,
                    "duration": elapsed,
                    "method": "bruteforce_6char"
                }
            
            # Update progress less frequently
            if attempts % 10000 == 0:
                elapsed = time.time() - start_time
                rate = attempts / elapsed if elapsed > 0 else 0
                print(f"    Attempting: {candidate} ({attempts:,} attempts, {rate:.0f} attempts/sec)", end='\r')
        
        elapsed = time.time() - start_time
        print(f"\n[-] FAILED. Password not found after {attempts:,} attempts.")
        print(f"[#] Time taken: {elapsed:.4f} seconds")
        
        return {
            "success": False,
            "attempts": attempts,
            "duration": elapsed,
            "method": "bruteforce"
        }
    
    def smart_attack(self, stored_hash, salt, username):
        """
        Smart attack that tries dictionary first, then brute force
        """
        print(f"\n[*] Starting Smart Attack for user: {username}")
        
        # Try dictionary attack first (faster for 3 and 5 char passwords)
        result = self.dictionary_attack(stored_hash, salt, username)
        
        if result["success"]:
            return result
        
        # If dictionary fails, try brute force for 6-char passwords
        print("\n[*] Dictionary attack failed. Trying brute force for 6-character passwords...")
        return self.brute_force_6char_attack(stored_hash, salt, username)