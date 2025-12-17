import bcrypt

def hash_password(password: str) -> str:
    """
    Turns a plain-text password into a secure hash.
    Used during Registration.
    """
    # Generate a 'salt' and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks if a typed password matches the stored hash.
    Used during Login.
    """
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )