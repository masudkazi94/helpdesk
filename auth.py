import hashlib
import secrets

def hash_password(password):
    salt = "helpdesk_salt_2024"
    return hashlib.sha256((password + salt).encode()).hexdigest()

def check_password(password, hashed):
    new_hash = hash_password(password)
    return new_hash == hashed

def create_token(email):
    return f"token_{email}_{secrets.token_hex(8)}"

def verify_token(token):
    if token and token.startswith("token_"):
        return True
    return False

def get_email_from_token(token):
    if token and token.startswith("token_"):
        parts = token.split("_")
        if len(parts) >= 2:
            return parts[1]
    return None