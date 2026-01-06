"""Security utilities for password hashing and verification."""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _truncate_password(password: str, max_bytes: int = 72) -> str:
    """Safely truncate a password to a maximum number of UTF-8 bytes.
    
    This function truncates the password without breaking multi-byte UTF-8 characters.
    
    Args:
        password: The password string to truncate
        max_bytes: Maximum number of bytes (default 72 for bcrypt)
        
    Returns:
        The truncated password string
    """
    password_bytes = password.encode('utf-8')
    if len(password_bytes) <= max_bytes:
        return password
    
    # Truncate to max_bytes, but ensure we don't break a multi-byte character
    # UTF-8 continuation bytes start with 10xxxxxx (0x80-0xBF)
    # We need to find the last valid character boundary
    truncated = password_bytes[:max_bytes]
    
    # Walk backwards to find a valid UTF-8 character boundary
    while truncated:
        try:
            return truncated.decode('utf-8')
        except UnicodeDecodeError:
            # Remove the last byte and try again
            truncated = truncated[:-1]
    
    # If we get here, return empty string (shouldn't happen in practice)
    return ""


def hash_password(password: str) -> str:
    """Hash a password, truncating to 72 bytes if necessary for bcrypt.
    
    Note: Passwords are truncated at the UTF-8 byte level to fit bcrypt's 72-byte limit.
    For passwords with multi-byte characters, this may result in fewer characters being used.
    
    Args:
        password: The plain text password to hash
        
    Returns:
        The hashed password
    """
    truncated_password = _truncate_password(password, 72)
    return pwd_context.hash(truncated_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash, truncating if necessary.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to verify against
        
    Returns:
        True if the password matches, False otherwise
    """
    truncated_password = _truncate_password(plain_password, 72)
    return pwd_context.verify(truncated_password, hashed_password)
