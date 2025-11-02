# backend/password_attack_service.py

import itertools
import string
from fonction_de_hachage_lent import verify_password

class PasswordAttackService:
    def __init__(self):
        self.common_passwords = [
            # 3-character passwords (2,3,4)
            "234", "243", "324", "342", "423", "432",
            "233", "244", "322", "344", "422", "433",
            "222", "333", "444", "223", "224", "332",
            "334", "442", "443", "232", "323", "343",
            "434", "242", "424", "244", "422", "233",
            # 5-digit passwords
            "12345", "11111", "00000", "54321", "13579",
            "22222", "33333", "44444", "55555", "66666",
            "77777", "88888", "99999", "10101", "12121",
            "12321", "11223", "99889", "10001", "20002",
            # 6-character passwords - COMPREHENSIVE LIST
            "123456", "abcdef", "qwerty", "password", "admin12",
            "q7*88+", "test12", "secret", "hello1", "welcome",
            "letmein", "monkey", "dragon", "master", "123123",
            "qwertz", "asdfgh", "zxcvbn", "passwd", "123qwe",
            "azouz*", "azerty", "star**", "hello*", "test**",
            "pass**", "admin*", "user**", "login*", "access",
            "system", "server", "client", "network", "python",
            "flask*", "webapp", "secure", "crypto", "encode",
            "decode", "hidden", "shadow", "silent", "random"
        ]
        
        # Load additional passwords from dictionary files
        self.load_dictionary_passwords()
    
    def load_dictionary_passwords(self):
        """Load additional passwords from dictionary files"""
        try:
            # Load from keys.txt for more variety
            with open('keys.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip()
                    if 3 <= len(word) <= 6:
                        # Add the word itself
                        self.common_passwords.append(word.lower())
                        # For 3-character words, add permutations
                        if len(word) == 3:
                            self.common_passwords.append(''.join(sorted(word.lower())))
        except FileNotFoundError:
            print("keys.txt not found, using built-in dictionary only")
    
    def dictionary_attack(self, stored_hash, salt, username=None):
        """Comprehensive dictionary attack with smart patterns"""
        print(f"Starting comprehensive dictionary attack on hash: {stored_hash[:20]}...")
        
        attempts = 0
        found_password = None
        
        # Remove duplicates
        unique_passwords = list(set(self.common_passwords))
        
        # Add username-based patterns if username provided
        if username:
            username_patterns = self.generate_username_patterns(username)
            unique_passwords.extend(username_patterns)
        
        print(f"Testing {len(unique_passwords)} unique passwords...")
        
        for password in unique_passwords:
            attempts += 1
            
            # Skip passwords that don't match our format constraints
            if not self.is_valid_password_format(password):
                continue
                
            print(f"Trying password #{attempts}: {password}")
            
            # Verify if this password matches the stored hash
            is_valid = verify_password(stored_hash, password, salt, iterations=10000)
            
            if is_valid:
                print(f"✅ Password found: {password}")
                found_password = password
                break
        
        return {
            "success": found_password is not None,
            "password": found_password,
            "attempts": attempts,
            "method": "dictionary"
        }
    
    def brute_force_attack(self, stored_hash, salt, username=None):
        """Comprehensive brute force attack with all strategies combined"""
        print(f"Starting comprehensive brute force attack on hash: {stored_hash[:20]}...")
        
        attempts = 0
        found_password = None
        
        # STRATEGY 1: Complete 3-character passwords (only 2,3,4)
        print("Strategy 1: Testing ALL 3-character passwords (2,3,4)...")
        three_char_combinations = list(itertools.product("234", repeat=3))
        
        for combo in three_char_combinations:
            password = ''.join(combo)
            attempts += 1
            
            if attempts % 50 == 0:
                print(f"Attempt #{attempts}: {password}")
            
            is_valid = verify_password(stored_hash, password, salt, iterations=10000)
            
            if is_valid:
                print(f"✅ Password found: {password}")
                found_password = password
                break
        
        if found_password:
            return {
                "success": True,
                "password": found_password,
                "attempts": attempts,
                "method": "bruteforce"
            }
        
        # STRATEGY 2: Comprehensive 5-digit patterns
        print("Strategy 2: Testing comprehensive 5-digit passwords...")
        digit_patterns = self.generate_5_digit_patterns()
        
        for password in digit_patterns:
            attempts += 1
            
            if attempts % 100 == 0:
                print(f"Attempt #{attempts}: {password}")
            
            is_valid = verify_password(stored_hash, password, salt, iterations=10000)
            
            if is_valid:
                print(f"✅ Password found: {password}")
                found_password = password
                break
        
        if found_password:
            return {
                "success": True,
                "password": found_password,
                "attempts": attempts,
                "method": "bruteforce"
            }
        
        # STRATEGY 3: Common 6-char patterns with special characters
        print("Strategy 3: Testing common 6-char patterns...")
        common_six_char = self.generate_6_char_common_patterns(username)
        
        for password in common_six_char:
            attempts += 1
            
            if attempts % 100 == 0:
                print(f"Attempt #{attempts}: {password}")
            
            is_valid = verify_password(stored_hash, password, salt, iterations=10000)
            
            if is_valid:
                print(f"✅ Password found: {password}")
                found_password = password
                break
        
        if found_password:
            return {
                "success": True,
                "password": found_password,
                "attempts": attempts,
                "method": "bruteforce"
            }
        
        # STRATEGY 4: Username-based 6-char patterns (if username provided)
        if username:
            print("Strategy 4: Testing username-based 6-char patterns...")
            username_patterns = self.generate_username_6char_patterns(username)
            
            for password in username_patterns:
                attempts += 1
                
                if attempts % 100 == 0:
                    print(f"Attempt #{attempts}: {password}")
                
                is_valid = verify_password(stored_hash, password, salt, iterations=10000)
                
                if is_valid:
                    print(f"✅ Password found: {password}")
                    found_password = password
                    break
            
            if found_password:
                return {
                    "success": True,
                    "password": found_password,
                    "attempts": attempts,
                    "method": "bruteforce"
                }
        
        # STRATEGY 5: Systematic generation with special characters
        print("Strategy 5: Systematic generation with special characters...")
        systematic_passwords = self.generate_systematic_6char_patterns()
        
        for password in systematic_passwords:
            attempts += 1
            
            if attempts % 500 == 0:
                print(f"Attempt #{attempts}: {password}")
            
            is_valid = verify_password(stored_hash, password, salt, iterations=10000)
            
            if is_valid:
                print(f"✅ Password found: {password}")
                found_password = password
                break
        
        return {
            "success": found_password is not None,
            "password": found_password,
            "attempts": attempts,
            "method": "bruteforce"
        }
    
    def generate_5_digit_patterns(self):
        """Generate comprehensive 5-digit patterns"""
        patterns = set()
        
        # All repeating patterns
        for digit in "0123456789":
            patterns.add(digit * 5)
        
        # Sequential patterns
        patterns.update(["12345", "54321", "13579", "02468", "98765"])
        
        # Common patterns
        patterns.update([
            "11111", "22222", "33333", "44444", "55555",
            "00000", "99999", "10101", "12121", "12321",
            "11223", "99889", "10001", "20002", "30003"
        ])
        
        # Palindromes
        for i in "0123456789":
            for j in "0123456789":
                patterns.add(i + j + "0" + j + i)
                patterns.add(i + j + j + j + i)
        
        return list(patterns)
    
    def generate_6_char_common_patterns(self, username=None):
        """Generate common 6-character patterns"""
        patterns = [
            "123456", "qwerty", "password", "abcdef", "123abc",
            "qwe123", "pass12", "test12", "hello1", "welcome",
            "q7*88+", "admin1", "letmein", "monkey", "dragon",
            "master", "123123", "qwertz", "asdfgh", "zxcvbn",
            "azouz*", "azerty", "star**", "hello*", "test**",
            "pass**", "admin*", "user**", "login*", "access",
            "system", "server", "client", "network", "python"
        ]
        
        # Add username variations if provided
        if username:
            username_lower = username.lower()
            if len(username_lower) >= 3:
                base = username_lower[:3]
                patterns.extend([
                    base + "***", base + "**+", base + "*+*",
                    base + "+**", base + "+++", base + "123"
                ])
            if len(username_lower) >= 4:
                base = username_lower[:4]
                patterns.extend([
                    base + "**", base + "*+", base + "+*", base + "++"
                ])
            if len(username_lower) >= 5:
                base = username_lower[:5]
                patterns.extend([
                    base + "*", base + "+", base + "1"
                ])
        
        return list(set(patterns))
    
    def generate_username_6char_patterns(self, username):
        """Generate username-based 6-character patterns"""
        patterns = []
        username_lower = username.lower()
        
        # Use first 3-5 characters of username with special chars
        for length in [3, 4, 5]:
            if len(username_lower) >= length:
                base = username_lower[:length]
                remaining = 6 - length
                
                if remaining > 0:
                    # Generate combinations of * and + to fill remaining positions
                    for combo in itertools.product("*+", repeat=remaining):
                        patterns.append(base + ''.join(combo))
                
                # Also try with numbers
                if remaining == 1:
                    for digit in "1234567890":
                        patterns.append(base + digit)
                elif remaining == 2:
                    for digit1 in "1234567890":
                        for digit2 in "1234567890":
                            patterns.append(base + digit1 + digit2)
        
        return list(set(patterns))
    
    def generate_systematic_6char_patterns(self):
        """Generate systematic 6-character patterns (limited for performance)"""
        patterns = []
        chars = "abcdefghijklmnopqrstuvwxyz*+"
        
        # Generate passwords with exactly one special character
        for special_pos in range(6):
            for letter_combo in itertools.product("abcdefghijklmnopqrstuvwxyz", repeat=5):
                if len(patterns) >= 1000:  # Limit for performance
                    break
                password_chars = list(letter_combo)
                password_chars.insert(special_pos, '*')
                patterns.append(''.join(password_chars))
        
        # Generate passwords with two special characters
        for pos1 in range(6):
            for pos2 in range(pos1 + 1, 6):
                for letter_combo in itertools.product("abcdefghijklmnopqrstuvwxyz", repeat=4):
                    if len(patterns) >= 2000:  # Limit for performance
                        break
                    password_chars = list(letter_combo)
                    # Insert two special characters
                    for i, pos in enumerate(sorted([pos1, pos2])):
                        password_chars.insert(pos + i, '*')
                    patterns.append(''.join(password_chars))
        
        return patterns[:3000]  # Return first 3000 patterns
    
    def generate_username_patterns(self, username):
        """Generate password patterns based on username"""
        patterns = []
        base = username.lower()
        
        # For 6-character passwords
        if len(base) >= 3:
            patterns.extend([
                base[:3] + "***", base[:3] + "**+", base[:3] + "*+*",
                base[:3] + "+**", base[:3] + "+++", base[:3] + "123"
            ])
        
        if len(base) >= 4:
            patterns.extend([
                base[:4] + "**", base[:4] + "*+", base[:4] + "+*", 
                base[:4] + "++", base[:4] + "12"
            ])
        
        if len(base) >= 5:
            patterns.extend([
                base[:5] + "*", base[:5] + "+", base[:5] + "1"
            ])
        
        # Full username with special chars if it's 6 chars
        if len(base) == 6:
            patterns.append(base)
            # Try replacing last character with *
            patterns.append(base[:-1] + "*")
            # Try replacing last two characters with **
            patterns.append(base[:-2] + "**")
        
        return patterns
    
    def is_valid_password_format(self, password):
        """Check if password matches one of the valid formats"""
        # Type 1: 3 characters (2, 3, or 4)
        if len(password) == 3:
            return all(char in '234' for char in password)
        
        # Type 2: 5 digits (0-9)
        if len(password) == 5:
            return password.isdigit()
        
        # Type 3: 6 characters (a-z, A-Z, 0-9, +, *)
        if len(password) == 6:
            allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+*')
            return all(char in allowed_chars for char in password)
        
        return False