import time
import os
from itertools import product
from fonction_de_hachage_lent import verify_password


class PasswordAttackService:
    def __init__(self, wordlist_path='wordlist.txt'):
        self.wordlist_path = wordlist_path
        self.progress_callback = None
        self.verbose = True  # Added verbose mode for detailed output

    def _print_header(self, title):
        """Print a formatted header for attack methods"""
        print("\n" + "="*80)
        print(f"  {title}")
        print("="*80)

    def _print_attempt(self, attempt_num, candidate, elapsed, rate, percentage=None):
        """New method to print detailed attempt information"""
        if percentage:
            print(f"  Attempt #{attempt_num:,} | Candidate: '{candidate}' | Progress: {percentage}% | Rate: {rate:.0f} pwd/sec | Time: {elapsed:.2f}s")
        else:
            print(f"  Attempt #{attempt_num:,} | Candidate: '{candidate}' | Rate: {rate:.0f} pwd/sec | Time: {elapsed:.2f}s")

    def _print_statistics(self, result):
        """New method to print final statistics"""
        print("\n" + "-"*80)
        print("  ATTACK STATISTICS")
        print("-"*80)
        print(f"  Method: {result['method']}")
        print(f"  Total Attempts: {result.get('attempts', 0):,}")
        print(f"  Total Processed: {result.get('processed', 0):,}")
        if result.get('total'):
            print(f"  Total Combinations: {result['total']:,}")
        print(f"  Duration: {result['duration']:.4f} seconds")
        print(f"  Success: {'✓ YES' if result['success'] else '✗ NO'}")
        if result.get('found'):
            print(f"  Password Found: '{result['password']}'")
        if result.get('attempts') > 0:
            avg_rate = result['attempts'] / result['duration'] if result['duration'] > 0 else 0
            print(f"  Average Rate: {avg_rate:.0f} attempts/second")
        print("-"*80 + "\n")

    # ---------------------------
    # Dictionary attack: 3-char only
    # ---------------------------
    def dictionary3_attack(self, stored_hash, salt, username):
        """Dictionary attack for 3 character passwords only."""
        self._print_header(f"DICTIONARY ATTACK (3-char) - User: {username}")
        start_time = time.time()
        attempts = 0

        wordlist_path = os.path.join('Attacks', 'worldlist3.txt')
        if not os.path.exists(wordlist_path):
            print(f"[!] Wordlist not found: {wordlist_path}")
            return {"success": False, "attempts": 0, "duration": 0, "method": "dictionary3"}

        with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            words = [line.strip() for line in f if line.strip()]

        print(f"\n  Wordlist loaded: {len(words):,} entries")
        print(f"  Starting attack...\n")

        for password in words:
            attempts += 1
            elapsed = time.time() - start_time
            rate = attempts / elapsed if elapsed > 0 else 0
            
            # Print first 10, then every 10 attempts
            if attempts <= 10 or attempts % 10 == 0:
                self._print_attempt(attempts, password, elapsed, rate)
            
            if verify_password(stored_hash, password, salt):
                elapsed = time.time() - start_time
                print(f"\n  ✓ SUCCESS! Password found: '{password}' after {attempts:,} attempts\n")
                result = {
                    "success": True,
                    "found": True,
                    "password": password,
                    "attempts": attempts,
                    "processed": attempts,
                    "total": len(words),
                    "duration": elapsed,
                    "method": "dictionary3"
                }
                self._print_statistics(result)
                return result
                elapsed = time.time() - start_time
                print(f"\n  ✗ FAILED. Password not found after {attempts:,} attempts.\n")
                result = {
                    "success": False,
                    "found": False,
                    "attempts": attempts,
                    "processed": attempts,
                    "total": len(words),
                    "duration": elapsed,
                    "method": "dictionary3"
                }
                self._print_statistics(result)
                return result

    # ---------------------------
    # Brute force attack (5 or 6 chars)
    # ---------------------------
    def brute_force_attack(self, stored_hash, salt, username, length=5):
        """
        Brute force attack for passwords of specified length (5 or 6 chars)
        5-char: digits only (0-9) = 10 characters, 100,000 combinations
        6-char: a-z, A-Z, 0-9, +, * = 64 characters, 68 billion combinations
        """
        self._print_header(f"BRUTE FORCE ATTACK ({length}-char) - User: {username}")
        
        if length == 5:
            CHAR_SET = '0123456789'
        else:
            CHAR_SET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789*+'
        
        total_combinations = len(CHAR_SET) ** length
        print(f"\n  Character set: {CHAR_SET}")
        print(f"  Character set size: {len(CHAR_SET)}")
        print(f"  Total combinations: {total_combinations:,}")
        print(f"  Starting attack...\n")

        attempts = 0
        start_time = time.time()

        for combination in product(CHAR_SET, repeat=length):
            candidate = ''.join(combination)
            attempts += 1

            elapsed = time.time() - start_time
            rate = attempts / elapsed if elapsed > 0 else 0
            percentage = int((attempts / total_combinations) * 100)

            # CORRECT - Inside the loop
            if attempts <= 10 or attempts % 100 == 0:
                self._print_attempt(attempts, candidate, elapsed, rate, percentage)

            if verify_password(stored_hash, candidate, salt):
                elapsed = time.time() - start_time
                print(f"\n  ✓ SUCCESS! Password found: '{candidate}' after {attempts:,} attempts\n")
                result = {
                    "success": True,
                    "found": True,
                    "password": candidate,
                    "attempts": attempts,
                    "processed": attempts,
                    "total": total_combinations,
                    "duration": elapsed,
                    "method": f"bruteforce_{length}char"
                }
                self._print_statistics(result)
                if self.progress_callback:
                    self.progress_callback({
                        "status": "found",
                        "attempts": attempts,
                        "processed": attempts,
                        "total": total_combinations,
                        "percentage": 100,
                        "password": candidate
                    })
                return result

        elapsed = time.time() - start_time
        print(f"\n  ✗ FAILED. Password not found after {attempts:,} attempts.\n")
        result = {
            "success": False,
            "found": False,
            "attempts": attempts,
            "processed": attempts,
            "total": total_combinations,
            "duration": elapsed,
            "method": f"bruteforce_{length}char"
        }
        self._print_statistics(result)
        return result

    # ---------------------------
    # Smart attack: dict3 first, then brute force 5 and 6
    # ---------------------------
    def smart_attack(self, stored_hash, salt, username):
        """
        Smart attack that tries dictionary3 first, then brute force 5-char and 6-char
        """
        self._print_header(f"SMART ATTACK (Sequential) - User: {username}")
        print(f"\n  Phase 1: Dictionary 3-char attack")
        print(f"  Phase 2: Brute force 5-char attack")
        print(f"  Phase 3: Brute force 6-char attack\n")

        # Try dictionary3 first
        result = self.dictionary3_attack(stored_hash, salt, username)
        if result["success"]:
            return result

        # If failed, try brute force for 5-char then 6-char passwords
        for length in [5, 6]:
            result = self.brute_force_attack(stored_hash, salt, username, length=length)
            if result["success"]:
                return result

        print(f"\n  ✗ SMART ATTACK FAILED - All phases exhausted\n")
        return {
            "success": False,
            "found": False,
            "attempts": result.get("attempts", 0),
            "duration": result.get("duration", 0),
            "method": "smart_attack"
        }
