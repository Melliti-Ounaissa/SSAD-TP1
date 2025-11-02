#!/usr/bin/env python3
import string
import itertools # Essential for generating all combinations

def build_square_from_sequence(sequence):
    """
    Creates the 5x5 Playfair matrix directly from a 25-character sequence.
    The sequence is assumed to be a unique permutation of the 25 letters (A-Z excluding J).
    """ 
    # The sequence itself is the full key space permutation
    matrix = [sequence[i:i+5] for i in range(0,25,5)]
    return matrix

def pos_of(mat,ch):
    """
    Finds the row and column position (i, j) of a character in the 5x5 matrix.
    """
    for i in range(5):
        for j in range(5):
            if mat[i][j]==ch:
                return i,j
    return None

def playfair_decrypt_with_mat(ct, mat):
    """
    Decrypts the ciphertext using the given Playfair matrix.
    Handles the three Playfair rules (same row, same column, rectangle).
    """
    # Prepare ciphertext: uppercase, replace J with I, and ensure even length
    s = ct.upper().replace("J","I").replace(" ", "")
    # Remove final character if length is odd (due to common padding issues)
    if len(s) % 2 == 1:
        s = s[:-1] 
    
    out = []
    
    for i in range(0, len(s), 2):
        a,b = s[i], s[i+1]
        p1 = pos_of(mat,a); p2 = pos_of(mat,b)
        
        if p1 is None or p2 is None:
            # Handle non-alphabetic characters
            return None 

        r1, c1 = p1
        r2, c2 = p2
        
        # Rule 1: Same Row (move one column left)
        if r1 == r2:
            out.append(mat[r1][(c1-1)%5] + mat[r2][(c2-1)%5])
        # Rule 2: Same Column (move one row up)
        elif c1 == c2:
            out.append(mat[(r1-1)%5][c1] + mat[r2][c2])
        # Rule 3: Rectangle (swap column indices)
        else:
            out.append(mat[r1][c2] + mat[r2][c1])
            
    return "".join(out)

def print_results(results):
    """Helper to format and print the results found."""
    if not results:
        return

    print("\n--- Decryption Candidates Found ---")
    for i, (key_sequence, pt) in enumerate(results):
        # Format plaintext for cleaner output (adding a space every 5 chars)
        formatted_pt = " ".join([pt[j:j+5] for j in range(0, len(pt), 5)])
        # The key sequence is the full 25-letter permutation
        print(f"#{i+1}: Key='{key_sequence}' | Plaintext: {formatted_pt}")


def run_full_bruteforce(ct):
    """
    Performs the full theoretical brute-force attack by iterating through ALL 
    possible unique 25-letter permutations (25! keys).
    """
    all_letters = string.ascii_uppercase.replace("J", "") # The 25 unique letters
    results = []
    
    # --- CRITICAL WARNING: READ THIS COMMENT ---
    # The total number of permutations is 25! (approx. 1.55 x 10^25).
    # This loop WILL NOT finish. It is included only to demonstrate the mechanism 
    # of iterating over the full key space as requested.
    # The program will run until it is stopped or times out.
    # -------------------------------------------
    
    print(f"Starting UNLIMITED BRUTE-FORCE attack (25! total permutations)...")
    print("This process is EXTREMELY slow and will not finish.")
    
    for i, combo in enumerate(itertools.permutations(all_letters, 25)):
        # Convert the tuple of letters into a 25-character string key
        key_sequence = "".join(combo)
        
        # Print progress (once every 10 million iterations is still very fast in the beginning)
        if i % 100 == 0:
            print(f"\rProgress: Tested {i} permutations...", end='', flush=True)

        mat = build_square_from_sequence(key_sequence)
        pt = playfair_decrypt_with_mat(ct, mat)
        
        if pt is None:
            continue
            
        # Since there is no scoring, we just print the key/plaintext pair as soon as we find it
        # However, due to the volume, we only print a few to demonstrate it is working.
        if i < 100:
            results.append((key_sequence, pt))
        
        # To show that it continues working, we will periodically print results
        if i % 100 == 0 and i > 0:
            print_results(results)

    print("\n\nFull brute-force iteration complete (Theoretically impossible to reach this line).")
    print_results(results)

# --- Main Execution Block ---
if __name__ == "__main__":
    print("--- Playfair Decryption Tool: PURE, UNLIMITED Brute-Force Mode ---")
    
    # Example Playfair Ciphertext (Encrypted with a short key for quick testing):
    example_ciphertext = "LBMQUXKRNBKIMGLBNTMFQZTMXGZ"
    
    ciphertext = input(f"Ciphertext (e.g., {example_ciphertext}): ").strip()
    if not ciphertext:
        ciphertext = example_ciphertext
        
    run_full_bruteforce(ciphertext)
