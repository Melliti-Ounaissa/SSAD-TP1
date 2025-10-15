def caesar_encrypt(text, shift=3):
    result = ""

    for char in text:
        if char.isalpha():
            ascii_offset = 65 if char.isupper() else 97
            shifted = (ord(char) - ascii_offset + shift) % 26
            result += chr(shifted + ascii_offset)
        else:
            result += char

    return result


def caesar_decrypt(encrypted_text, shift=3):
    return caesar_encrypt(encrypted_text, -shift)
