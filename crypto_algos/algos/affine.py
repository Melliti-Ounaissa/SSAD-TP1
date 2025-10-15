def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def mod_inverse(a, m):
    for i in range(1, m):
        if (a * i) % m == 1:
            return i
    return None


def affine_encrypt(text, a=5, b=8):
    if gcd(a, 26) != 1:
        raise ValueError("'a' must be coprime with 26")

    result = ""

    for char in text:
        if char.isalpha():
            ascii_offset = 65 if char.isupper() else 97
            x = ord(char) - ascii_offset
            encrypted = (a * x + b) % 26
            result += chr(encrypted + ascii_offset)
        else:
            result += char

    return result


def affine_decrypt(encrypted_text, a=5, b=8):
    if gcd(a, 26) != 1:
        raise ValueError("'a' must be coprime with 26")

    a_inv = mod_inverse(a, 26)
    if a_inv is None:
        raise ValueError("No modular inverse exists for 'a'")

    result = ""

    for char in encrypted_text:
        if char.isalpha():
            ascii_offset = 65 if char.isupper() else 97
            y = ord(char) - ascii_offset
            decrypted = (a_inv * (y - b)) % 26
            result += chr(decrypted + ascii_offset)
        else:
            result += char

    return result
