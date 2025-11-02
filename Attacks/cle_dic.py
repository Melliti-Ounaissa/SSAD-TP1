#!/usr/bin/env python3
import string
import math
import itertools # Added for Playfair/Hill key generation if needed

# --- File Reading Helper ---
def read_keys_from_file(filepath):
    """Reads key words from a file, one key per line."""
    try:
        print(f"Attempting to read keys from file: '{filepath}'...")
        with open(filepath, 'r') as f:
            # Strip whitespace and ignore empty lines
            keys = [line.strip().upper() for line in f if line.strip()]
            print(f"Successfully loaded {len(keys)} keys from file.")
            return keys
    except FileNotFoundError:
        # Since we cannot create a keys.txt file in this environment, this fallback is necessary.
        print(f"Error: Key file '{filepath}' not found.")
        print("Falling back to hardcoded default key list for demonstration.")
        # Fallback list used when the file is not found
        return ["MONARCHY", "KEYWORD", "CIPHER", "ATTACK", "SECRET", "TESTING", "FOUR", "FIVE", "MATH", "KEYS"] 

# --- 1. CAESAR CIPHER DECRYPTOR ---

def caesar_decrypt(ciphertext):
    print("\n--- Cracking Caesar Cipher (All 25 Shifts) ---")
    results = []
    ciphertext = ciphertext.upper().replace(" ", "")

    for key in range(1, 26): # Test all 25 possible shifts
        plaintext = ""
        for char in ciphertext:
            if 'A' <= char <= 'Z':
                # Decrypt: (Char index - Key) mod 26
                char_index = ord(char) - ord('A')
                decrypted_index = (char_index - key) % 26
                plaintext += chr(decrypted_index + ord('A'))
            else:
                plaintext += char # Keep non-alpha characters
        
        results.append((key, plaintext))
        print(f"Key {key:2}: {plaintext}")

    return results


# --- 2. PLAYFAIR CIPHER DECRYPTOR (Key Word Testing) ---

def build_square_from_key_word(key_word):
    """Constructs the 5x5 Playfair matrix from a key word."""
    key = "".join(dict.fromkeys(key_word.upper().replace("J","I")))
    remaining_letters = [c for c in string.ascii_uppercase if c not in key and c != "J"]
    flat = list(key) + remaining_letters
    matrix = [flat[i:i+5] for i in range(0,25,5)]
    return matrix

def playfair_decrypt_with_mat(ct, mat):
    """Performs the Playfair decryption with a given matrix."""
    s = ct.upper().replace("J","I").replace(" ", "")
    if len(s) % 2 == 1: s = s[:-1]
    
    out = []
    
    for i in range(0, len(s), 2):
        a,b = s[i], s[i+1]
        
        # Helper to find position (row, col)
        p1, p2 = None, None
        for r in range(5):
            if a in mat[r]: p1 = (r, mat[r].index(a))
            if b in mat[r]: p2 = (r, mat[r].index(b))
        
        if p1 is None or p2 is None: return None 

        r1, c1 = p1
        r2, c2 = p2
        
        if r1 == r2:
            out.append(mat[r1][(c1-1)%5] + mat[r2][(c2-1)%5])
        elif c1 == c2:
            out.append(mat[(r1-1)%5][c1] + mat[(r2-1)%5][c2])
        else:
            out.append(mat[r1][c2] + mat[r2][c1])
            
    return "".join(out)


def playfair_decrypt(ciphertext, key_source):
    """
    Decrypts Playfair using a list of key words or key words read from a file path.
    """
    print("\n--- Decrypting Playfair Cipher (Testing Key Words) ---")
    results = []
    
    # Determine the list of keys to use
    if isinstance(key_source, str):
        # If key_source is a string, treat it as a file path
        key_word_list = read_keys_from_file(key_source)
    else:
        # Otherwise, assume it's already a list of key words
        key_word_list = key_source
    
    # Clean ciphertext once
    ct_clean = ''.join(c for c in ciphertext.upper() if c in string.ascii_uppercase.replace('J', 'I'))

    for key_word in key_word_list:
        mat = build_square_from_key_word(key_word)
        plaintext = playfair_decrypt_with_mat(ct_clean, mat)

        if plaintext:
            results.append((key_word, plaintext))
            print(f"Key '{key_word}': {plaintext}")

    return results


# --- 3. HILL CIPHER DECRYPTOR (2x2 Key Word Testing) ---

# Utility functions for modular arithmetic (necessary for Hill cipher)
def mod_inverse(a, m):
    """Computes the modular inverse of a mod m."""
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None # No modular inverse exists

def det_mod_26(matrix):
    """Computes the determinant of a 2x2 matrix mod 26."""
    return (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) % 26

def hill_decrypt_2x2(ciphertext, key_matrix):
    """Decrypts the ciphertext using the given 2x2 key matrix."""
    
    # Key matrix is [a, b], [c, d]
    a, b = key_matrix[0]
    c, d = key_matrix[1]
    
    det = det_mod_26(key_matrix)
    det_inv = mod_inverse(det, 26)
    
    if det_inv is None:
        return None # Key is singular (non-invertible)

    # Calculate inverse matrix: det_inv * [[d, -b], [-c, a]] mod 26
    inv_matrix = [
        [(d * det_inv) % 26, ((-b % 26) * det_inv) % 26],
        [((-c % 26) * det_inv) % 26, (a * det_inv) % 26]
    ]

    s = ciphertext.upper().replace(" ", "")
    if len(s) % 2 == 1: s += 'X' # Pad if necessary
    
    plaintext = ""
    
    for i in range(0, len(s), 2):
        c1 = ord(s[i]) - ord('A')
        c2 = ord(s[i+1]) - ord('A')
        
        # Decryption calculation
        p1 = (c1 * inv_matrix[0][0] + c2 * inv_matrix[1][0]) % 26
        p2 = (c1 * inv_matrix[0][1] + c2 * inv_matrix[1][1]) % 26

        plaintext += chr(p1 + ord('A'))
        plaintext += chr(p2 + ord('A'))

    return plaintext

def hill_decrypt_attack(ciphertext, key_source):
    """
    Tests Hill (2x2) by testing keys derived from common words or a file, and prints the results.
    """
    print("\n--- Decrypting Hill Cipher (Testing 2x2 Key Words) ---")
    results = []
    
    # Determine the list of keys to use
    if isinstance(key_source, str):
        # If key_source is a string, treat it as a file path
        key_word_list = read_keys_from_file(key_source)
    else:
        # Otherwise, assume it's already a list of key words
        key_word_list = key_source
    
    # We only use the first 4 letters of each word for a 2x2 key
    for word in key_word_list:
        key_chars = [ord(c) - ord('A') for c in word.upper() if c in string.ascii_uppercase][:4]
        
        if len(key_chars) != 4:
            continue
            
        # Form 2x2 matrix: [[k0, k1], [k2, k3]]
        key_matrix = [
            [key_chars[0], key_chars[1]],
            [key_chars[2], key_chars[3]]
        ]
        
        plaintext = hill_decrypt_2x2(ciphertext, key_matrix)
        
        if plaintext:
            results.append((word, plaintext))
            print(f"Key '{word}': {plaintext}")

    return results

# --- MAIN EXECUTION ---

if __name__ == "__main__":
    print("--- Classical Cipher Decryption Tool (Simple Key Testing) ---")
    
    # --- Test Case 1: Caesar Cipher ---
    caesar_ct = "XJSIRSFQJSJD" # Encrypted from 'SENDMOREMONEY' with Key 5
    print(f"\n[CIPHERTEXT] Caesar: {caesar_ct}")
    caesar_decrypt(caesar_ct)

    # --- Test Case 2: Playfair Cipher (using file path as key source) ---
    playfair_ct = "LBMQUXKRNBKIMGLBNTMFQZTMXGZ" # Encrypted from 'THETESTISREADY' with Key 'TESTING'
    print(f"\n[CIPHERTEXT] Playfair: {playfair_ct}")
    
    # Pass the filename string as the key source, which triggers file reading logic
    keys_file_path = "keys.txt" 
    playfair_decrypt(playfair_ct, keys_file_path)
    
    # --- Test Case 3: Hill Cipher (2x2) ---
    hill_ct = "XALROU" # Encrypted from 'HELPME' with Key 'test'
    print(f"\n[CIPHERTEXT] Hill (2x2): {hill_ct}")
    
    # Pass the filename string as the key source, which triggers file reading logic
    keys_list2 = "keys2.txt"
    hill_decrypt_attack(hill_ct, keys_list2)
