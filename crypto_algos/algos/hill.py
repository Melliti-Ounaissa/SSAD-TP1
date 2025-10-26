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
    det_mod = det % 27
    if det_mod == 0 or math.gcd(det_mod, 27) != 1:
        raise ValueError("Invalid key matrix: Determinant is not invertible modulo 27.")

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
        encrypted_block = np.dot(key_matrix, block) % 27
        encrypted_block = np.where(encrypted_block < 0, encrypted_block + 27, encrypted_block)
        ciphertext += ''.join(num_to_char(int(num)) for num in encrypted_block.flatten())
    return ciphertext

def hill_decrypt(ciphertext, key_matrix, n):
    det = int(round(np.linalg.det(key_matrix)))
    det_mod = det % 27
    if det_mod < 0:
        det_mod += 27

    det_inv = pow(det_mod, -1, 27)  # inverse multiplicatif modulo 27

    adj_matrix = np.round(np.linalg.inv(key_matrix) * det).astype(int)
    key_matrix_mod_inv = (det_inv * adj_matrix) % 27
    key_matrix_mod_inv = np.where(key_matrix_mod_inv < 0, key_matrix_mod_inv + 27, key_matrix_mod_inv)

    plaintext = ""
    for i in range(0, len(ciphertext), n):
        block = [char_to_num(char) for char in ciphertext[i:i + n]]
        block = np.array(block).reshape((n, 1))
        decrypted_block = np.dot(key_matrix_mod_inv, block) % 27
        decrypted_block = np.where(decrypted_block < 0, decrypted_block + 27, decrypted_block)
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
    """Encrypt bytes (or a str) using Hill cipher modulo 256.

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
    # Interactive CLI preserved under __main__ so imports don't prompt.
    n = int(input("Enter the matrix size (n x n): "))
    key = input(f"Enter the key (length {n*n}): ").strip()
    plaintext = input("Enter the plaintext: ").strip()

    # Decide whether to use the alphabet-based Hill (A-Z + '#') or bytes-based (UTF-8) mode.
    # If plaintext contains characters outside A-Za-z and space, switch to bytes mode.
    use_bytes_mode = any(ch for ch in plaintext if not (ch.isalpha() or ch == ' '))

    try:
        if not use_bytes_mode:
            # alphabet-based mode (existing behavior)
            key_matrix = generate_key_matrix(key, n)
            ciphertext = hill_encrypt(plaintext, key_matrix, n)
            decrypted_text = hill_decrypt(ciphertext, key_matrix, n)
            print("\nKey Matrix:\n", key_matrix)
            print("Original Plaintext:", plaintext)
            print("Encrypted Text:", ciphertext)
            print("Decrypted Text :", restore_case(decrypted_text, plaintext))
        else:
            # bytes-based mode: encode plaintext as UTF-8 and use hill_encrypt_bytes
            # Build key matrix from key encoded as utf-8 bytes; key must have exactly n*n bytes.
            # Allow two key formats for bytes mode:
            # - comma-separated integers 0..255 (e.g. "3,3,2,5" for n=2)
            # - a string which will be encoded as utf-8 and must have exactly n*n bytes
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