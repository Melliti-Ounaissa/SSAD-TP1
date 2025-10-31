import numpy as np
import math


def invrs_mod(a, m):
    """Return modular inverse of a modulo m, or None if it doesn't exist.

    Uses the extended Euclidean algorithm.
    """
    a = a % m

    def _egcd(x, y):
        if y == 0:
            return (1, 0, x)
        x1, y1, g = _egcd(y, x % y)
        return (y1, x1 - (x // y) * y1, g)

    x, _, g = _egcd(a, m)
    if g != 1:
        return None
    return x % m


def matrix_mod_inv(mat, mod=256):
    mat = np.array(mat, dtype=int)
    if mat.shape[0] != mat.shape[1]:
        raise ValueError("Matrix must be square")
    det = int(round(np.linalg.det(mat)))
    det_mod = det % mod
    inv_det = invrs_mod(det_mod, mod)
    if inv_det is None:
        return None
    # adjugate via inverse * det
    adj = np.round(np.linalg.inv(mat) * det).astype(int)
    inv = (inv_det * adj) % mod
    inv = np.where(inv < 0, inv + mod, inv)
    return inv.astype(int)


def pad_pkcs7(data: bytes, block_size: int) -> bytes:
    if block_size <= 0 or block_size > 255:
        raise ValueError("Invalid block size for PKCS#7 padding")
    pad_len = block_size - (len(data) % block_size)
    if pad_len == 0:
        pad_len = block_size
    return data + bytes([pad_len]) * pad_len


def unpad_pkcs7(data: bytes, block_size: int) -> bytes:
    if not data or len(data) % block_size != 0:
        raise ValueError("Invalid padded data length")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > block_size:
        raise ValueError("Invalid PKCS#7 padding")
    if data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise ValueError("Invalid PKCS#7 padding bytes")
    return data[:-pad_len]


def hill_encrypt_bytes(plaintext, key_matrix):
    """Encrypt bytes (or a str) using Hill cipher modulo 256 (UTF-8 mode only).

    plaintext: bytes or str (if str, encoded as utf-8)
    key_matrix: square matrix (list of lists or numpy array) with integer entries
    returns: bytes ciphertext
    """
    if isinstance(plaintext, str):
        data = plaintext.encode('utf-8')
    else:
        data = bytes(plaintext)

    mat = np.array(key_matrix, dtype=int) % 256
    if mat.shape[0] != mat.shape[1]:
        raise ValueError("Key matrix must be square")
    n = mat.shape[0]

    det = int(round(np.linalg.det(mat)))
    if math.gcd(det % 256, 256) != 1:
        raise ValueError("Invalid key matrix: Determinant is not invertible modulo 256.")

    data = pad_pkcs7(data, n)
    cipher = bytearray()
    for i in range(0, len(data), n):
        block = np.frombuffer(data[i:i+n], dtype=np.uint8).astype(int).reshape((n, 1))
        encrypted_block = (mat.dot(block) % 256).flatten()
        cipher.extend(int(x) for x in encrypted_block)
    return bytes(cipher)


def hill_decrypt_bytes(cipher_bytes: bytes, key_matrix) -> bytes:
    """Decrypt bytes produced by hill_encrypt_bytes. Returns raw bytes (still padded).
    Caller should decode utf-8 if needed after depadding.
    """
    mat = np.array(key_matrix, dtype=int) % 256
    if mat.shape[0] != mat.shape[1]:
        raise ValueError("Key matrix must be square")
    n = mat.shape[0]

    inv_mat = matrix_mod_inv(mat, 256)
    if inv_mat is None:
        raise ValueError("Key matrix is not invertible modulo 256")

    plain = bytearray()
    for i in range(0, len(cipher_bytes), n):
        block = np.frombuffer(cipher_bytes[i:i+n], dtype=np.uint8).astype(int).reshape((n, 1))
        decrypted_block = (inv_mat.dot(block) % 256).flatten()
        plain.extend(int(x) for x in decrypted_block)

    # remove padding
    plain_bytes = unpad_pkcs7(bytes(plain), n)
    return plain_bytes


if __name__ == "__main__":
    # Simplified CLI: only UTF-8 bytes mode is supported.
    n = int(input("Enter the matrix size (n x n): "))
    key = input(f"Enter the key (either comma-separated integers or a string; for string the utf-8 encoded length must be {n*n}): ").strip()
    plaintext = input("Enter the plaintext: ").strip()

    try:
        # bytes-based mode only
        if ',' in key:
            parts = [p.strip() for p in key.split(',') if p.strip()]
            if len(parts) != n * n:
                raise ValueError(f"Key must contain exactly {n*n} integers when using comma-separated format; got {len(parts)}")
            try:
                ints = [int(p) for p in parts]
            except Exception:
                raise ValueError("Invalid integer in key list")
            if any(x < 0 or x > 255 for x in ints):
                raise ValueError("Key integers must be in range 0..255")
            key_matrix = np.array([ints[i*n:(i+1)*n] for i in range(n)], dtype=int)
        else:
            key_bytes = key.encode('utf-8')
            if len(key_bytes) != n * n:
                raise ValueError(f"For bytes mode the key encoded as utf-8 must be exactly {n*n} bytes long; got {len(key_bytes)}")
            # construct key matrix from byte values
            key_matrix = np.array([list(key_bytes[i*n:(i+1)*n]) for i in range(n)], dtype=int)

        ct = hill_encrypt_bytes(plaintext, key_matrix)
        pt_bytes = hill_decrypt_bytes(ct, key_matrix)
        try:
            decoded = pt_bytes.decode('utf-8')
        except Exception:
            decoded = None

        print("\nKey Matrix (bytes):\n", key_matrix)
        print("Original Plaintext:", plaintext)
        print("Cipher bytes:", ct)
        print("Decrypted bytes:", pt_bytes)
        print("Decoded (utf-8):", decoded)
        print("Round-trip OK:", decoded == plaintext)

    except ValueError as e:
        print("Error:", e)