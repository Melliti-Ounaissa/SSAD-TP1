def create_playfair_matrix(key="MONARCHY"):
    key = key.upper().replace("J", "I")

    matrix = []
    used = set()

    for char in key:
        if char.isalpha() and char not in used:
            matrix.append(char)
            used.add(char)

    for char in "ABCDEFGHIKLMNOPQRSTUVWXYZ":
        if char not in used:
            matrix.append(char)

    return [matrix[i:i+5] for i in range(0, 25, 5)]


def find_position(matrix, char):
    for i, row in enumerate(matrix):
        for j, c in enumerate(row):
            if c == char:
                return i, j
    return None, None


def prepare_text(text):
    text = text.upper().replace("J", "I")
    text = ''.join([c for c in text if c.isalpha()])

    prepared = []
    i = 0

    while i < len(text):
        char1 = text[i]

        if i + 1 < len(text):
            char2 = text[i + 1]
            if char1 == char2:
                prepared.append(char1)
                prepared.append('X')
                i += 1
            else:
                prepared.append(char1)
                prepared.append(char2)
                i += 2
        else:
            prepared.append(char1)
            prepared.append('X')
            i += 1

    return ''.join(prepared)


def playfair_encrypt(text, key="MONARCHY"):
    matrix = create_playfair_matrix(key)
    text = prepare_text(text)

    result = ""

    for i in range(0, len(text), 2):
        char1, char2 = text[i], text[i+1]
        row1, col1 = find_position(matrix, char1)
        row2, col2 = find_position(matrix, char2)

        if row1 == row2:
            result += matrix[row1][(col1 + 1) % 5]
            result += matrix[row2][(col2 + 1) % 5]
        elif col1 == col2:
            result += matrix[(row1 + 1) % 5][col1]
            result += matrix[(row2 + 1) % 5][col2]
        else:
            result += matrix[row1][col2]
            result += matrix[row2][col1]

    return result


def playfair_decrypt(encrypted_text, key="MONARCHY"):
    matrix = create_playfair_matrix(key)

    result = ""

    for i in range(0, len(encrypted_text), 2):
        char1, char2 = encrypted_text[i], encrypted_text[i+1]
        row1, col1 = find_position(matrix, char1)
        row2, col2 = find_position(matrix, char2)

        if row1 == row2:
            result += matrix[row1][(col1 - 1) % 5]
            result += matrix[row2][(col2 - 1) % 5]
        elif col1 == col2:
            result += matrix[(row1 - 1) % 5][col1]
            result += matrix[(row2 - 1) % 5][col2]
        else:
            result += matrix[row1][col2]
            result += matrix[row2][col1]

    return result
