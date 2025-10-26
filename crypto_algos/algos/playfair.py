import re

class PlayfairError(Exception):
    def __init__(self, message):
        super().__init__(message)

class Playfair:
    def __init__(self, doublePadding='X', endPadding='X'):
        self.grid = self.generateGrid('')
        if len(doublePadding) != 1:
            raise PlayfairError('The double padding must be a single character.')
        elif not self.isAlphabet(doublePadding):
            raise PlayfairError('The double padding must be a letter of the alphabet.')
        elif doublePadding.upper() == 'J':
            raise PlayfairError('The double padding character cannot be J (J is merged into I).')
        else:
            self.doublePadding = doublePadding.upper()

        if len(endPadding) != 1:
            raise PlayfairError('The end padding must be a single character.')
        elif not self.isAlphabet(endPadding):
            raise PlayfairError('The end padding must be a letter of the alphabet.')
        elif endPadding.upper() == 'J':
            raise PlayfairError('The end padding character cannot be J (J is merged into I).')
        else:
            self.endPadding = endPadding.upper()

    def convertLetter(self, letter):
        if letter.upper() == 'J':
            return 'I'
        return letter.upper()

    def getAlphabet(self):
        return 'ABCDEFGHIKLMNOPQRSTUVWXYZ'

    def generateGrid(self, password):
        password = (password or '').upper()
        password = ''.join(self.convertLetter(c) for c in password if c.isalpha())
        grid = ''
        alphabet = self.getAlphabet()
        for letter in password:
            if letter not in grid and letter in alphabet:
                grid += letter
        for letter in alphabet:
            if letter not in grid:
                grid += letter
        return grid

    def generateDigraphs(self, input):
        input = self.toAlphabet(input).upper()
        inputFixed = ''
        for ch in input:
            inputFixed += self.convertLetter(ch)
        digraphs = []
        i = 0
        while i < len(inputFixed):
            if i + 1 == len(inputFixed):
                digraphs.append(inputFixed[i] + self.endPadding)
                break
            a = inputFixed[i]
            b = inputFixed[i+1]
            if a != b:
                digraphs.append(a + b)
                i += 2
            else:
                digraphs.append(a + self.doublePadding)
                i += 1
        return digraphs

    def encryptDigraph(self, input):
        if len(input) != 2:
            raise PlayfairError('The digraph that is going to be encrypted must be exactly 2 characters long.')
        elif not self.isUpper(input):
            raise PlayfairError('The digraph that is going to be encrypted must contain only uppercase letters of the alphabet.')
        f = input[0]; s = input[1]
        fp = self.grid.find(f); sp = self.grid.find(s)
        fc = (fp % 5, fp // 5); sc = (sp % 5, sp // 5)
        if fc[0] == sc[0]:  # same column
            fe = self.grid[(((fc[1] + 1) % 5) * 5) + fc[0]]
            se = self.grid[(((sc[1] + 1) % 5) * 5) + sc[0]]
        elif fc[1] == sc[1]:  # same row
            fe = self.grid[(fc[1] * 5) + ((fc[0] + 1) % 5)]
            se = self.grid[(sc[1] * 5) + ((sc[0] + 1) % 5)]
        else:
            fe = self.grid[(fc[1] * 5) + sc[0]]
            se = self.grid[(sc[1] * 5) + fc[0]]
        return fe + se

    def decryptDigraph(self, input):
        if len(input) != 2:
            raise PlayfairError('The digraph that is going to be decrypted must be exactly 2 characters long.')
        elif not self.isUpper(input):
            raise PlayfairError('The digraph that is going to be decrypted must contain only uppercase letters of the alphabet.')
        f = input[0]; s = input[1]
        fp = self.grid.find(f); sp = self.grid.find(s)
        fc = (fp % 5, fp // 5); sc = (sp % 5, sp // 5)
        if fc[0] == sc[0]:  # same column
            fr = self.grid[(((fc[1] - 1) % 5) * 5) + fc[0]]
            sr = self.grid[(((sc[1] - 1) % 5) * 5) + sc[0]]
        elif fc[1] == sc[1]:  # same row
            fr = self.grid[(fc[1] * 5) + ((fc[0] - 1) % 5)]
            sr = self.grid[(sc[1] * 5) + ((sc[0] - 1) % 5)]
        else:
            fr = self.grid[(fc[1] * 5) + sc[0]]
            sr = self.grid[(sc[1] * 5) + fc[0]]
        return fr + sr

    def encrypt(self, input):
        digraphs = self.generateDigraphs(input)
        return ''.join(self.encryptDigraph(d) for d in digraphs)

    def encryptWithCase(self, input):
        original_flags = []
        clean = []
        for ch in input:
            if ch.isalpha():
                original_flags.append(ch.islower())
                clean.append(ch)
            else:
                original_flags.append(None)
        clean_text = ''.join(clean)
        encrypted = self.encrypt(clean_text)
        result = ''
        enc_i = 0
        for flag in original_flags:
            if flag is None:
                result += input[len(result)]  # keep non-alpha as-is
            else:
                if enc_i < len(encrypted):
                    c = encrypted[enc_i]
                    result += c.lower() if flag else c.upper()
                    enc_i += 1
                else:
                    # No more encrypted chars to map (shouldn't normally happen), append placeholder
                    result += self.endPadding
        # append any remaining encrypted chars (from padding) at the end
        if enc_i < len(encrypted):
            result += encrypted[enc_i:]
        return result

    def _split_ciphertext_pairs(self, input):
        s = self.toAlphabet(input).upper()
        if len(s) % 2 != 0:
            raise PlayfairError("Ciphertext length must be even.")
        return [s[i:i+2] for i in range(0, len(s), 2)]

    def _remove_padding(self, text):
        s = text
        if self.endPadding and s.endswith(self.endPadding):
            s = s[:-1]
        res = []
        i = 0
        while i < len(s):
            if i + 2 < len(s) and s[i+1] == self.doublePadding and s[i] == s[i+2]:
                res.append(s[i])
                i += 2
            else:
                res.append(s[i])
                i += 1
        return ''.join(res)

    def decrypt(self, input):
        pairs = self._split_ciphertext_pairs(input)
        decrypted = ''.join(self.decryptDigraph(p) for p in pairs)
        cleaned = self._remove_padding(decrypted)
        return cleaned

    def decryptWithCase(self, input):
        original_flags = []
        for ch in input:
            if ch.isalpha():
                original_flags.append(ch.islower())
            else:
                original_flags.append(None)
        ciphertext_letters = self.toAlphabet(input).upper()
        decrypted = self.decrypt(ciphertext_letters)  # already cleaned from padding
        result = ''
        dec_i = 0
        src_index = 0
        for flag in original_flags:
            if flag is None:
                # place the original non-alpha char from input
                result += input[src_index]
            else:
                if dec_i < len(decrypted):
                    c = decrypted[dec_i]
                    result += c.lower() if flag else c.upper()
                    dec_i += 1
                else:
                    result += ''  # no more decrypted chars
            src_index += 1
        # if there are remaining decrypted characters (from padding removal rules), append them
        if dec_i < len(decrypted):
            result += decrypted[dec_i:]
        return result

    def setPassword(self, password):
        password = self.toAlphabet(password).upper()
        self.grid = self.generateGrid(password)

    def toAlphabet(self, input):
        return re.sub('[^A-Za-z]', '', input)

    def isAlphabet(self, input):
        return re.fullmatch('[A-Za-z]+', input) is not None

    def isUpper(self, input):
        return re.fullmatch('[A-Z]+', input) is not None

def main():
    print("=== Chiffrement de Playfair ===")
    print("Les lettres J sont converties en I.\n")
    try:
        password = input("Entrez le mot de passe (clé): ").strip()
        if not password:
            print("Mot de passe vide.")
            return
        message = input("Entrez le message: ").strip()
        if message is None:
            print("Message vide.")
            return
        cipher = Playfair()
        cipher.setPassword(password)
        encrypted = cipher.encryptWithCase(message)
        decrypted = cipher.decryptWithCase(encrypted)
        print("\nClé (grid):", cipher.grid)
        print("Message:", message)
        print("Chiffré:", encrypted)
        print("Déchiffré:", decrypted)
    except PlayfairError as e:
        print("Erreur:", e)
    except Exception as e:
        print("Erreur inattendue:", e)

if __name__ == "__main__":
    main()