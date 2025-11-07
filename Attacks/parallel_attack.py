# Attacks/parallel_attack.py
import time
from itertools import product
from multiprocessing import Pool, cpu_count
import os
from fonction_de_hachage_lent import verify_password

def load_wordlist(path):
    path = os.path.expanduser(path)
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return [line.rstrip("\n\r") for line in f if line.strip()]

def _check_candidate_with_slowhash(args):
    candidate, stored_hash, salt_hex = args
    try:
        if verify_password(stored_hash, candidate, salt_hex):
            return candidate
    except Exception:
        pass
    return None

def parallel_dictionary_attack(wordlist_path, stored_hash, salt_hex, chunksize=256):
    words = load_wordlist(wordlist_path)
    n = len(words)
    if n == 0:
        print("[parallel_dictionary_attack] wordlist empty")
        return {"found": None, "processed": 0, "total": 0, "duration": 0.0}

    start = time.time()
    found = None
    processed = 0
    processes = cpu_count()
    print(f"[*] parallel_dictionary_attack: loaded {n} words, using {processes} processes")

    iterable = ((w, stored_hash, salt_hex) for w in words)
    with Pool(processes=processes) as pool:
        for result in pool.imap_unordered(_check_candidate_with_slowhash, iterable, chunksize=chunksize):
            processed += 1
            if result:
                found = result
                pool.terminate()
                pool.join()
                break
            if processed <= 20 or processed % 5000 == 0:
                elapsed = time.time() - start
                print(f"[progress] processed={processed}/{n}, elapsed={elapsed:.2f}s")

    elapsed = time.time() - start
    return {"found": found, "processed": processed, "total": n, "duration": elapsed}

def _check_bruteforce_with_slowhash(args):
    candidate, stored_hash, salt_hex = args
    try:
        if verify_password(stored_hash, candidate, salt_hex):
            return candidate
    except Exception:
        pass
    return None

def parallel_bruteforce(charset, length, stored_hash, salt_hex, chunksize=1):
    """
    Parallel brute force attack.
    
    Reduced chunksize from 1024 to 1 to ensure immediate early stopping.
    With chunksize=1024, the pool pre-sends 1024 tasks before returning results,
    causing many unnecessary checks even after finding the password.
    chunksize=1 means each worker processes one task at a time, allowing immediate
    termination when a match is found.
    """
    if length <= 0:
        raise ValueError("length must be > 0")

    processes = cpu_count()
    total = len(charset) ** length
    print(f"[*] parallel_bruteforce: charset_len={len(charset)}, length={length}, processes={processes}")
    print(f"[*] Total combinations: {total:,}")

    start = time.time()
    found = None
    processed = 0

    combos = (''.join(p) for p in product(charset, repeat=length))
    iterable = ((c, stored_hash, salt_hex) for c in combos)

    with Pool(processes=processes) as pool:
        for result in pool.imap_unordered(_check_bruteforce_with_slowhash, iterable, chunksize=chunksize):
            processed += 1
            if result:
                found = result
                pool.terminate()
                pool.join()
                break
            if processed <= 20 or processed % 10000 == 0:
                elapsed = time.time() - start
                rate = processed / elapsed if elapsed > 0 else 0
                print(f"[progress] checked={processed}/{total:,} ({rate:.0f} checks/s), elapsed={elapsed:.2f}s")

    elapsed = time.time() - start
    return {"found": found, "processed": processed, "total": total, "duration": elapsed}
