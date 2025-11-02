#!/usr/bin/env python3
import sys
from string import ascii_uppercase
import math

MARKERS = (" THE ", " AND ", " TO ", " OF ")

def caesar_decrypt(ct, shift):
    out = []
    for ch in ct:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            out.append(chr((ord(ch)-base-shift) % 26 + base))
        else:
            out.append(ch)
    return ''.join(out)

def run_caesar(ct):
    s = ct
    for k in range(26):
        print(f"left {k}: {caesar_decrypt(s, k)}")
    for k in range(26):
        print(f"right {k}: {caesar_decrypt(s, -k)}")

def inv_mod26_2x2(a,b,c,d):
    det = (a*d - b*c) % 26
    if math.gcd(det, 26) != 1:
        return None
    inv_det = pow(det, -1, 26)
    adj = [[d % 26, (-b) % 26],
        [(-c) % 26, a % 26]]
    inv = [[(inv_det * adj[i][j]) % 26 for j in (0,1)] for i in (0,1)]
    return inv

def hill_decrypt_with_inv(ct, invk):
    s = ''.join(ch for ch in ct.upper() if ch.isalpha())
    if len(s) % 2 == 1:
        s = s[:-1]
    out = []
    for i in range(0, len(s), 2):
        x = ord(s[i]) - 65
        y = ord(s[i+1]) - 65
        r0 = (invk[0][0]*x + invk[0][1]*y) % 26
        r1 = (invk[1][0]*x + invk[1][1]*y) % 26
        out.append(chr(r0+65) + chr(r1+65))
    return ''.join(out)

def run_hill_bruteforce(ct, show_all=False):
    s = ''.join(ch for ch in ct.upper() if ch.isalpha())
    if len(s) < 2:
        print("Hill: ciphertext too short")
        return
    tried = 0
    skipped = 0
    printed = 0
    for a in range(26):
        for b in range(26):
            for c in range(26):
                for d in range(26):
                    tried += 1
                    invk = inv_mod26_2x2(a,b,c,d)
                    if invk is None:
                        skipped += 1
                        continue
                    pt = hill_decrypt_with_inv(ct, invk)
                    up = " " + pt + " "
                    if show_all or any(m in up for m in MARKERS):
                        print(f"key=[[{a},{b}],[{c},{d}]] -> {pt}")
                        printed += 1
    print(f"Hill done. tried={tried} skipped_noninv={skipped} printed={printed}")

if __name__ == "__main__":
    ct = input("Ciphertext: ").strip()
    if not ct:
        sys.exit(0)
    mode = input("Mode (caesar/hill/both) [both]: ").strip().lower() or "both"
    if mode in ("caesar","both"):
        run_caesar(ct)
    if mode in ("hill","both"):
        print("Brute-forcing all 2x2 matrices (may take a while)...")
        run_hill_bruteforce(ct, show_all=False)
