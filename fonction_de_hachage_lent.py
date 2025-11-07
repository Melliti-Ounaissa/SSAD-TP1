import secrets


def _to_bytes(input_data):
    """Convertit l'entrée en bytes de façon sûre."""
    if isinstance(input_data, str):
        return input_data.encode('utf-8')
    if isinstance(input_data, bytes):
        return input_data
    return bytes(input_data)


def _slow_hash_core(data_bytes, salt_bytes, iterations=10000):
    """
    Coeur de l'algorithme de hachage.

    - data_bytes: bytes
    - salt_bytes: bytes
    - iterations: int

    Retourne le hash hex (8 chars) calculé.
    """
    # Réduire/obtenir une valeur 32-bit initiale pour le salt (compatibilité avec algo)
    salt_val = int.from_bytes(salt_bytes, 'big') & 0xFFFFFFFF
    hash_value = 0x5F5F5F5F

    for _ in range(iterations):
        for byte in data_bytes:
            hash_value ^= byte
            hash_value = ((hash_value << 7) | (hash_value >> 25)) & 0xFFFFFFFF
            hash_value = (hash_value + salt_val) & 0xFFFFFFFF
            hash_value = ((hash_value * 0x7FED5F) + 1) & 0xFFFFFFFF

            salt_val = ((salt_val << 3) | (salt_val >> 29)) & 0xFFFFFFFF
            salt_val ^= hash_value

    return format(hash_value, '08x')


def slow_hash(input_data, iterations=10000):
    """
    Fonction de hachage lente qui GENERE TOUJOURS un salt sécurisé.

    - input_data: str or bytes-like
    - iterations: nombre d'itérations (par défaut 10000)

    Retourne un tuple (hash_hex, salt_hex). Le salt est généré côté serveur
    et doit être stocké avec le hash. Le paramètre `salt` n'est pas accepté
    par design : la génération doit être faite par le serveur.
    """
    data = _to_bytes(input_data)
    salt_bytes = secrets.token_bytes(16)  # 128 bits de salt aléatoire
    hash_hex = _slow_hash_core(data, salt_bytes, iterations=iterations)
    return hash_hex, salt_bytes.hex()

def verify_password(stored_hash_hex, password, salt_hex, iterations=10000):
    """
    Vérifie qu'un mot de passe correspond au hash stocké en utilisant le salt fourni.

    - stored_hash_hex: hex string du hash stocké
    - password: mot de passe en clair (str ou bytes)
    - salt_hex: hex string du salt stocké
    - iterations: doit être la même que celle utilisée lors du hash

    Retourne True si correspond, False sinon.
    """
    # Convertir le salt_hex en bytes et recalculer le hash avec le même salt
    salt_bytes = bytes.fromhex(salt_hex)
    data = _to_bytes(password)
    computed_hash = _slow_hash_core(data, salt_bytes, iterations=iterations)
    # Utiliser compare_digest pour éviter les attaques par timing
    return secrets.compare_digest(computed_hash, stored_hash_hex)


if __name__ == "__main__":
    # Petit CLI pour tester localement
    import argparse

    parser = argparse.ArgumentParser(description="Testeur pour la fonction de hachage lente")
    sub = parser.add_subparsers(dest='cmd')

    p_hash = sub.add_parser('hash', help='Génère hash et salt pour un mot de passe')
    p_hash.add_argument('password')
    p_hash.add_argument('--iterations', type=int, default=10000)

    p_verify = sub.add_parser('verify', help='Vérifie un mot de passe contre un hash et salt')
    p_verify.add_argument('password')
    p_verify.add_argument('hash')
    p_verify.add_argument('salt')
    p_verify.add_argument('--iterations', type=int, default=10000)

    args = parser.parse_args()
    if args.cmd == 'hash':
        h, s = slow_hash(args.password, iterations=args.iterations)
        print(f'hash:{h}')
        print(f'salt:{s}')
    elif args.cmd == 'verify':
        ok = verify_password(args.hash, args.password, args.salt, iterations=args.iterations)
        print('OK' if ok else 'FAIL')
    else:
        parser.print_help()