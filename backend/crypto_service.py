from crypto_algos.algos.ceasare import caesar_encrypt, caesar_decrypt
from crypto_algos.algos.affine import affine_encrypt, affine_decrypt
# MODIFIED IMPORTS
from crypto_algos.algos.ceasare import caesar_encrypt, caesar_decrypt
from crypto_algos.algos.affine import affine_encrypt, affine_decrypt
# MODIFIED IMPORTS
from crypto_algos.algos.hill import hill_encrypt, hill_decrypt, generate_key_matrix, restore_spaces
# NEW PLAYFAIR IMPORTS
from crypto_algos.algos.playfair import Playfair, PlayfairError
import json
import math  # IMPORT MATH


class CryptoService:
    @staticmethod
    def encrypt_message(message, algorithm, key_params=None):
        algo = algorithm.lower()

        if algo == "ceasar":
            shift = int(key_params.get('shift', 3)) if key_params else 3
            return caesar_encrypt(message, shift=shift)

        elif algo == "affine":
            if key_params:
                a = int(key_params.get('a', 5))
                b = int(key_params.get('b', 8))
            else:
                a, b = 5, 8
            return affine_encrypt(message, a=a, b=b)

        elif algo == "hill":
            # MODIFIED HILL ENCRYPTION LOGIC
            key = key_params.get('key', 'FRID') if key_params else 'FRID'
            key_len = len(key)
            
            if key_len == 0:
                 raise ValueError("Hill key cannot be empty")

            n = int(math.sqrt(key_len))
            if n * n != key_len:
                raise ValueError(f"Hill key length must be a perfect square (4, 9, 16...). Got length {key_len}")

            try:
                key_matrix = generate_key_matrix(key, n)
                # Call new hill_encrypt, which handles spaces-to-'#' and padding
                return hill_encrypt(message, key_matrix, n, preserve_case=False)
            except ValueError as e:
                # Catch errors from generate_key_matrix (e.g., non-invertible)
                raise ValueError(f"Hill key error: {e}")

        elif algo == "playfair":
            # MODIFIED PLAYFAIR ENCRYPTION LOGIC
            key = key_params.get('key', 'MONARCHY') if key_params else 'MONARCHY'
            try:
                cipher = Playfair()
                cipher.setPassword(key)
                # Use encryptWithCase to preserve spaces and punctuation
                return cipher.encryptWithCase(message)
            except PlayfairError as e:
                raise ValueError(f"Playfair key/encryption error: {e}")
            except Exception as e:
                raise ValueError(f"Playfair error: {e}")

        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

    @staticmethod
    def decrypt_message(encrypted_message, algorithm, key_params=None):
        algo = algorithm.lower()

        if algo == "ceasar":
            shift = int(key_params.get('shift', 3)) if key_params else 3
            return caesar_decrypt(encrypted_message, shift=shift)

        elif algo == "affine":
            if key_params:
                a = int(key_params.get('a', 5))
                b = int(key_params.get('b', 8))
            else:
                a, b = 5, 8
            return affine_decrypt(encrypted_message, a=a, b=b)

        elif algo == "hill":
            # MODIFIED HILL DECRYPTION LOGIC
            key = key_params.get('key', 'FRID') if key_params else 'FRID'
            key_len = len(key)
            
            if key_len == 0:
                 raise ValueError("Hill key cannot be empty")
                 
            n = int(math.sqrt(key_len))
            if n * n != key_len:
                raise ValueError(f"Hill key length must be a perfect square (4, 9, 16...). Got length {key_len}")

            try:
                key_matrix = generate_key_matrix(key, n)
                decrypted_with_hash = hill_decrypt(encrypted_message, key_matrix, n)
                # Restore spaces from '#' and remove padding
                return restore_spaces(decrypted_with_hash)
            except ValueError as e:
                raise ValueError(f"Hill key/decryption error: {e}")

        elif algo == "playfair":
            # MODIFIED PLAYFAIR DECRYPTION LOGIC
            key = key_params.get('key', 'MONARCHY') if key_params else 'MONARCHY'
            try:
                cipher = Playfair()
                cipher.setPassword(key)
                # Use decryptWithCase to correctly handle spaces and punctuation
                return cipher.decryptWithCase(encrypted_message)
            except PlayfairError as e:
                raise ValueError(f"Playfair key/decryption error: {e}")
            except Exception as e:
                raise ValueError(f"Playfair error: {e}")

        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")