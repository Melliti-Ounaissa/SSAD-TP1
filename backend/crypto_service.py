from crypto_algos.algos.ceasare import caesar_encrypt, caesar_decrypt
from crypto_algos.algos.affine import affine_encrypt, affine_decrypt
from crypto_algos.algos.hill import hill_encrypt_bytes, hill_decrypt_bytes
from crypto_algos.algos.hill import matrix_mod_inv # You'll need this to check key invertibility
from crypto_algos.algos.playfair import Playfair, PlayfairError
import json
import math  # IMPORT MATH
import numpy as np # You'll need this for key matrix creation


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
            key = key_params.get('key', 'FRID') if key_params else 'FRID'
            key_len = len(key)

            if key_len == 0:
                raise ValueError("Hill key cannot be empty")

            n = int(math.sqrt(key_len))
            if n * n != key_len:
                raise ValueError(f"Hill key length must be a perfect square (4, 9, 16...). Got length {key_len}")

            # --- NEW LOGIC TO CREATE KEY MATRIX ---
            try:
                key_bytes = key.encode('utf-8')
                if len(key_bytes) != n * n:
                    raise ValueError(f"Key encoded as utf-8 must be exactly {n*n} bytes long")
                key_matrix = np.array([list(key_bytes[i*n:(i+1)*n]) for i in range(n)], dtype=int)
                # You might need to check invertibility here, or let hill_encrypt_bytes handle it

                # Use the existing function name
                return hill_encrypt_bytes(message, key_matrix)
            except ValueError as e:
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
            key = key_params.get('key', 'FRID') if key_params else 'FRID'
            key_len = len(key)

            # ... (key length checks as above) ...

            try:
                # --- NEW LOGIC TO CREATE KEY MATRIX ---
                key_bytes = key.encode('utf-8')
                key_matrix = np.array([list(key_bytes[i*n:(i+1)*n]) for i in range(n)], dtype=int)

                # Use the existing function name. The result is bytes.
                decrypted_bytes = hill_decrypt_bytes(encrypted_message, key_matrix)

                # The original logic for restore_spaces is now irrelevant.
                # You must decode the result to a string.
                return decrypted_bytes.decode('utf-8')

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