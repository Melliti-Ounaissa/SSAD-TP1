from crypto_algos.algos.ceasare import caesar_encrypt, caesar_decrypt
from crypto_algos.algos.affine import affine_encrypt, affine_decrypt
from crypto_algos.algos.hill import hill_encrypt, hill_decrypt
from crypto_algos.algos.playfair import playfair_encrypt, playfair_decrypt
import json


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
            return hill_encrypt(message)

        elif algo == "playfair":
            key = key_params.get('key', 'MONARCHY') if key_params else 'MONARCHY'
            return playfair_encrypt(message, key=key)

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
            return hill_decrypt(encrypted_message)

        elif algo == "playfair":
            key = key_params.get('key', 'MONARCHY') if key_params else 'MONARCHY'
            return playfair_decrypt(encrypted_message, key=key)

        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
