import numpy as np


def mod_inverse(a, m):
    for i in range(1, m):
        if (a * i) % m == 1:
            return i
    return None


def matrix_mod_inverse(matrix, modulus):
    det = int(np.round(np.linalg.det(matrix)))
    det = det % modulus
    det_inv = mod_inverse(det, modulus)

    if det_inv is None:
        raise ValueError("Matrix is not invertible")

    matrix_adj = np.round(det * np.linalg.inv(matrix)).astype(int) % modulus
    matrix_inv = (det_inv * matrix_adj) % modulus

    return matrix_inv


def prepare_text(text, block_size):
    text = ''.join([c.upper() for c in text if c.isalpha()])

    while len(text) % block_size != 0:
        text += 'X'

    return text


def hill_encrypt(text, key_matrix=None):
    if key_matrix is None:
        key_matrix = np.array([[6, 24, 1], [13, 16, 10], [20, 17, 15]])

    key_matrix = np.array(key_matrix)
    block_size = key_matrix.shape[0]
    text = prepare_text(text, block_size)

    result = ""

    for i in range(0, len(text), block_size):
        block = text[i:i+block_size]
        vector = np.array([ord(c) - 65 for c in block])
        encrypted_vector = np.dot(key_matrix, vector) % 26
        result += ''.join([chr(int(num) + 65) for num in encrypted_vector])

    return result


def hill_decrypt(encrypted_text, key_matrix=None):
    if key_matrix is None:
        key_matrix = np.array([[6, 24, 1], [13, 16, 10], [20, 17, 15]])

    key_matrix = np.array(key_matrix)
    block_size = key_matrix.shape[0]

    try:
        key_matrix_inv = matrix_mod_inverse(key_matrix, 26)
    except ValueError as e:
        raise ValueError(f"Cannot decrypt: {e}")

    result = ""

    for i in range(0, len(encrypted_text), block_size):
        block = encrypted_text[i:i+block_size]
        vector = np.array([ord(c) - 65 for c in block])
        decrypted_vector = np.dot(key_matrix_inv, vector) % 26
        result += ''.join([chr(int(num) + 65) for num in decrypted_vector])

    return result
