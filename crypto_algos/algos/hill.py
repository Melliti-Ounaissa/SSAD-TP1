import numpy as np
import math

def char_to_num(char):
    """Convertit un caractère en nombre (A/a=0, ..., Z/z=25, #=26)"""
    if char == '#':
        return 26
    if 'A' <= char <= 'Z':
        return ord(char) - ord('A')
    if 'a' <= char <= 'z':
        return ord(char) - ord('a')
    raise ValueError(f"Unsupported character: {char}")

def num_to_char(num):
    """Convertit un nombre en caractère (0=A, 1=B, ..., 25=Z, 26=#)"""
    if num == 26:
        return '#'
    return chr(int(num) + ord('A'))

def validate_key_matrix(key_matrix, n):
    det = int(round(np.linalg.det(key_matrix)))  # calcule et arrondit le determinant
    det_mod = det % 26
    if det_mod == 0 or math.gcd(det_mod, 26) != 1:
        raise ValueError("Invalid key matrix: Determinant is not invertible modulo 26.")

def generate_key_matrix(key, n):  # crée une matrice de taille nxn
    key = key.upper().replace(" ", "")  # met la clé en majuscule et supprime les espaces
    if len(key) != n * n:
        raise ValueError("Key length must be equal to the square of the matrix size.")

    key_matrix = []
    for i in range(n):
        row = [char_to_num(char) for char in key[i * n:(i + 1) * n]]
        key_matrix.append(row)

    key_matrix = np.array(key_matrix, dtype=int)
    validate_key_matrix(key_matrix, n)
    return key_matrix

def prepare_plaintext(plaintext, n, preserve_case=False):
    if preserve_case:
        processed_text = plaintext.replace(" ", "#")
    else:
        processed_text = plaintext.upper().replace(" ", "#")
    
    if len(processed_text) % n != 0:
        padding = n - (len(processed_text) % n)
        processed_text += '#' * padding
    return processed_text

def hill_encrypt(plaintext, key_matrix, n, preserve_case=False):
    original_case = plaintext if preserve_case else None
    plaintext = prepare_plaintext(plaintext, n, preserve_case)
    ciphertext = ""
    for i in range(0, len(plaintext), n):
        block = [char_to_num(char) for char in plaintext[i:i + n]]
        block = np.array(block).reshape((n, 1))
        encrypted_block = np.dot(key_matrix, block) % 26
        encrypted_block = np.where(encrypted_block < 0, encrypted_block + 26, encrypted_block)
        ciphertext += ''.join(num_to_char(int(num)) for num in encrypted_block.flatten())
    return ciphertext

def hill_decrypt(ciphertext, key_matrix, n):
    det = int(round(np.linalg.det(key_matrix)))
    det_mod = det % 26
    if det_mod < 0:
        det_mod += 26

    det_inv = pow(det_mod, -1, 26)  # inverse multiplicatif modulo 26

    adj_matrix = np.round(np.linalg.inv(key_matrix) * det).astype(int)
    key_matrix_mod_inv = (det_inv * adj_matrix) % 26
    key_matrix_mod_inv = np.where(key_matrix_mod_inv < 0, key_matrix_mod_inv + 26, key_matrix_mod_inv)

    plaintext = ""
    for i in range(0, len(ciphertext), n):
        block = [char_to_num(char) for char in ciphertext[i:i + n]]
        block = np.array(block).reshape((n, 1))
        decrypted_block = np.dot(key_matrix_mod_inv, block) % 26
        decrypted_block = np.where(decrypted_block < 0, decrypted_block + 26, decrypted_block)
        plaintext += ''.join(num_to_char(int(num)) for num in decrypted_block.flatten())
    return plaintext

def restore_spaces(text):
    """Restaure les espaces en remplaçant les '#' par des espaces et supprime le padding"""
    return text.replace('#', ' ').rstrip()

def restore_case(decrypted_text, original_text):
    """Restaure la casse originale du texte déchiffré en respectant les espaces et en enlevant le padding."""
    decrypted_clean = decrypted_text.replace('#', '')  # caractères déchiffrés sans padding/espace
    result = []
    idx = 0

    for ch in original_text:
        if ch == ' ':
            result.append(' ')
        else:
            if idx < len(decrypted_clean):
                decoded_char = decrypted_clean[idx]
                result.append(decoded_char.lower() if ch.islower() else decoded_char.upper())
                idx += 1
            else:
                break

    return ''.join(result).rstrip()

# ... (Toutes vos fonctions se terminent ici, y compris restore_case) ...

# Ce bloc ne s'exécute QUE si vous lancez 'python hill.py' directement
if __name__ == "__main__":
    # Take inputs from the user
    n = int(input("Enter the matrix size (n x n): "))
    key = input(f"Enter the key (length {n*n}): ").strip()
    plaintext = input("Enter the plaintext: ").strip()

    try:
        key_matrix = generate_key_matrix(key, n)

        ciphertext = hill_encrypt(plaintext, key_matrix, n)
        decrypted_text = hill_decrypt(ciphertext, key_matrix, n)

        print("\nKey Matrix:\n", key_matrix)
        print("Original Plaintext:", plaintext)
        print("Encrypted Text:", ciphertext)
        print("Decrypted Text :", restore_case(decrypted_text, plaintext))

    except ValueError as e:
        print("Error:", e)