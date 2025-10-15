from crypto_algos.algos.ceasare import caesar_encrypt, caesar_decrypt
from crypto_algos.algos.affine import affine_encrypt, affine_decrypt
from crypto_algos.algos.hill import hill_encrypt, hill_decrypt
from crypto_algos.algos.playfair import playfair_encrypt, playfair_decrypt


class CryptoService:
    @staticmethod
    def encrypt_message(message, algorithm):
        if algorithm.lower() == "ceasar":
            return caesar_encrypt(message, shift=3)
        elif algorithm.lower() == "affine":
            return affine_encrypt(message, a=5, b=8)
        elif algorithm.lower() == "hill":
            return hill_encrypt(message)
        elif algorithm.lower() == "playfair":
            return playfair_encrypt(message, key="MONARCHY")
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

    @staticmethod
    def decrypt_message(encrypted_message, algorithm):
        if algorithm.lower() == "ceasar":
            return caesar_decrypt(encrypted_message, shift=3)
        elif algorithm.lower() == "affine":
            return affine_decrypt(encrypted_message, a=5, b=8)
        elif algorithm.lower() == "hill":
            return hill_decrypt(encrypted_message)
        elif algorithm.lower() == "playfair":
            return playfair_decrypt(encrypted_message, key="MONARCHY")
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
