import bcrypt

def hash_password(plain_password):
    """
    Hashes a plain password using bcrypt.
    Args:
        plain_password (str): The plaintext password to hash.
    Returns:
        str: The hashed password.
    """
    return bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()

# Authenticate user by comparing hashed password
def authenticate(username, password, users):
    if username in users:
        return bcrypt.checkpw(password.encode(), users[username].encode())
    return False