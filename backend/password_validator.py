import re


class PasswordValidator:
    @staticmethod
    def validate_password(password):
        if PasswordValidator.is_type1_password(password):
            return True, "Valid Type 1 password (3 digits: 2, 3, or 4)"
        elif PasswordValidator.is_type2_password(password):
            return True, "Valid Type 2 password (5 digits: 0-9)"
        elif PasswordValidator.is_type3_password(password):
            return True, "Valid Type 3 password (6 characters: a-z, A-Z, 0-9, +, *)"
        else:
            return False, "Invalid password"

    @staticmethod
    def is_type1_password(password):
        if len(password) != 3:
            return False
        for char in password:
            if char not in ['2', '3', '4']:
                return False
        return True

    @staticmethod
    def is_type2_password(password):
        if len(password) != 5:
            return False
        return password.isdigit()

    @staticmethod
    def is_type3_password(password):
        if len(password) != 6:
            return False
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+*')
        for char in password:
            if char not in allowed_chars:
                return False
        return True
