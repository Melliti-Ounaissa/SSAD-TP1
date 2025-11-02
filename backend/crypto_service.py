from crypto_algos.algos.ceasare import caesar_encrypt, caesar_decrypt
# --- CORRIGÉ ---
# Importer les fonctions qui existent réellement dans votre hill.py
from crypto_algos.algos.hill import (
    hill_encrypt, 
    hill_decrypt, 
    generate_key_matrix, 
    restore_spaces
)
# --- FIN CORRECTION ---
from crypto_algos.algos.playfair import Playfair, PlayfairError
import json
import math
import numpy as np


class CryptoService:
    @staticmethod
    def encrypt_message(message, algorithm, key_params=None):
        algo = algorithm.lower()

        if algo == "ceasar":
            shift = int(key_params.get('shift', 3)) if key_params else 3
            return caesar_encrypt(message, shift=shift)

        elif algo == "hill":
            key = key_params.get('key', 'FRID') if key_params else 'FRID'
            key_len = len(key)

            if key_len == 0:
                raise ValueError("Hill key cannot be empty")

            n = int(math.sqrt(key_len))
            if n * n != key_len:
                raise ValueError(f"Hill key length must be a perfect square (4, 9, 16...). Got length {key_len}")

            try:
                # --- CORRIGÉ ---
                # Utiliser la fonction de génération de matrice de hill.py
                key_matrix = generate_key_matrix(key, n)

                # Appeler la fonction d'encryptage correcte
                # 'preserve_case=True' correspond à la logique de votre hill.py
                return hill_encrypt(message, key_matrix, n, preserve_case=True)
                # --- FIN CORRECTION ---
            except ValueError as e:
                raise ValueError(f"Hill key error: {e}")

        elif algo == "playfair":
            key = key_params.get('key', 'MONARCHY') if key_params else 'MONARCHY'
            try:
                cipher = Playfair()
                cipher.setPassword(key)
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

        elif algo == "hill":
            key = key_params.get('key', 'FRID') if key_params else 'FRID'
            key_len = len(key)

            # --- CORRIGÉ ---
            if key_len == 0:
                raise ValueError("Hill key cannot be empty")
            
            n = int(math.sqrt(key_len))
            if n * n != key_len:
                raise ValueError(f"Hill key length must be a perfect square (4, 9, 16...). Got length {key_len}")
            # --- FIN CORRECTION ---

            try:
                # --- CORRIGÉ ---
                # Générer la matrice de la même manière
                key_matrix = generate_key_matrix(key, n)

                # Appeler la fonction de déchiffrement correcte
                decrypted_text = hill_decrypt(encrypted_message, key_matrix, n)

                # Utiliser votre fonction pour nettoyer la sortie
                return restore_spaces(decrypted_text)
                # --- FIN CORRECTION ---

            except ValueError as e:
                raise ValueError(f"Hill key/decryption error: {e}")

        elif algo == "playfair":
            key = key_params.get('key', 'MONARCHY') if key_params else 'MONARCHY'
            try:
                cipher = Playfair()
                cipher.setPassword(key)
                return cipher.decryptWithCase(encrypted_message)
            except PlayfairError as e:
                raise ValueError(f"Playfair key/decryption error: {e}")
            except Exception as e:
                raise ValueError(f"Playfair error: {e}")

        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")