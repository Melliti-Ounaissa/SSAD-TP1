def caesar_encrypt(text, shift=3, direction='droite'):
    """
    Encrypt text using Caesar cipher with direction support
    
    Args:
        text: Text to encrypt
        shift: Number of positions to shift
        direction: 'droite' (right) or 'gauche' (left)
    """
    import string
    alphabet = string.printable
    mlen = len(alphabet)
    resultat = []
    
    # Normalize direction
    if direction.lower() == "droite":
        sens = 1
    elif direction.lower() == "gauche":
        sens = -1
    else:
        raise ValueError("La direction doit être 'droite' ou 'gauche'.")
    
    for ch in text:
        if ch in alphabet:
            m = alphabet.index(ch)
            c = (m + sens * shift) % mlen
            resultat.append(alphabet[c])
        else:
            resultat.append(ch)
    
    return ''.join(resultat)


def caesar_decrypt(encrypted_text, shift=3, direction='droite'):
    """
    Decrypt text using Caesar cipher with direction support
    
    Args:
        encrypted_text: Text to decrypt
        shift: Number of positions to shift
        direction: 'droite' (right) or 'gauche' (left)
    """
    import string
    alphabet = string.printable
    mlen = len(alphabet)
    resultat = []
    
    # Normalize direction
    if direction.lower() == "droite":
        sens = 1
    elif direction.lower() == "gauche":
        sens = -1
    else:
        raise ValueError("La direction doit être 'droite' ou 'gauche'.")
    
    for ch in encrypted_text:
        if ch in alphabet:
            c = alphabet.index(ch)
            m = (c - sens * shift) % mlen
            resultat.append(alphabet[m])
        else:
            resultat.append(ch)
    
    return ''.join(resultat)