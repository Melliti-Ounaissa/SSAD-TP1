def caesar_encrypt(text, shift=3):
    import string
    alphabet = string.printable
    mlen = len(alphabet)
    resultat = []
    for ch in text:
        if ch in alphabet:
            m = alphabet.index(ch)
            c = (m + shift) % mlen
            resultat.append(alphabet[c])
        else:
            resultat.append(ch)
    return ''.join(resultat)


    # result = ""

    # for char in text:
    #     if char.isalpha():
    #         ascii_offset = 65 if char.isupper() else 97
    #         shifted = (ord(char) - ascii_offset + shift) % 26
    #         result += chr(shifted + ascii_offset)
    #     else:
    #         result += char

    # return result

    

def caesar_decrypt(encrypted_text, shift=3):
    return caesar_encrypt(encrypted_text, -shift)
