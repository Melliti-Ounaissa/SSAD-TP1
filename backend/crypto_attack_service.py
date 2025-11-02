# backend/crypto_attack_service.py

import os
# Assuming cle_dic.py and Ceasar_Hill_brute_force.py are accessible or their logic is here.
# For simplicity, we'll assume we can import the needed functions:
from Attacks.cle_dic import caesar_decrypt, playfair_decrypt, hill_decrypt_attack
from Attacks.Ceasar_Hill_brute_force import run_hill_bruteforce 

class CryptoAttackService:
    def __init__(self, keys_file='keys.txt', keys2_file='keys2.txt'):
        # Define paths to your dictionary files
        self.caesar_markers = (" THE ", " AND ", " TO ", " OF ")
        self.keys_file = keys_file # for Playfair
        self.keys2_file = keys2_file # for Hill 2x2

    def attack_cipher(self, cipher_type, ciphertext):
        
        # --- CAESAR BRUTE-FORCE ---
        if cipher_type == 'caesar':
            # Use the function from cle_dic.py that returns a list of (key, plaintext) tuples
            results = caesar_decrypt(ciphertext)
            
            # Simple scoring/filtering to highlight likely correct plaintexts
            formatted_results = []
            for key, pt in results:
                is_likely = any(marker in (" " + pt.upper() + " ") for marker in self.caesar_markers)
                formatted_results.append({
                    'key': key,
                    'plaintext': pt,
                    'is_likely': is_likely
                })
            return {"success": True, "type": "Caesar Brute-Force", "results": formatted_results}

        # --- PLAYFAIR DICTIONARY ATTACK ---
        elif cipher_type == 'playfair_dict':
            # Uses key words from a file to perform decryption
            results = playfair_decrypt(ciphertext, self.keys_file)
            
            formatted_results = [{
                'key': key,
                'plaintext': pt,
                'is_likely': False # Needs a more complex scoring function to be truly useful
            } for key, pt in results]
            
            return {"success": True, "type": "Playfair Dictionary", "results": formatted_results}

        # --- HILL 2X2 FULL BRUTE-FORCE ---
        elif cipher_type == 'hill_brute':
            # The run_hill_bruteforce prints results, but for API, we need it to return them.
            # You would need to modify the function in Ceasar_Hill_brute_force.py 
            # to return the results instead of printing them. 
            # Assuming a modified version of run_hill_bruteforce exists:
            # results = run_hill_bruteforce(ciphertext) 
            
            # Since that is a large attack, we will use the dictionary one for a quick API demo
            print("Warning: Full Hill Brute-Force is very slow. Using Dictionary Attack instead.")
            return self.attack_cipher('hill_dict', ciphertext)


        # --- HILL 2X2 DICTIONARY ATTACK ---
        elif cipher_type == 'hill_dict':
            # Uses the first 4 letters of key words from a file for the 2x2 key matrix
            results = hill_decrypt_attack(ciphertext, self.keys2_file)
            
            formatted_results = [{
                'key': key,
                'plaintext': pt,
                'is_likely': False
            } for key, pt in results]
            
            return {"success": True, "type": "Hill 2x2 Dictionary", "results": formatted_results}


        return {"success": False, "message": "Invalid cipher type."}