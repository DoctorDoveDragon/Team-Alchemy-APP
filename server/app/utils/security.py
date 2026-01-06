"""Security utilities for password hashing and verification.

This module provides utilities for safely hashing and verifying passwords
with bcrypt, ensuring compliance with bcrypt's 72-byte password limit.
"""
import bcrypt


def _truncate_to_bcrypt_bytes(password: str) -> bytes:
    """Encode password to UTF-8 and truncate to bcrypt's 72-byte limit.
    
    Args:
        password: The plain text password to encode and truncate
        
    Returns:
        The password encoded as UTF-8 bytes, truncated to 72 bytes if necessary
    """
    b = password.encode("utf-8")
    if len(b) > 72:
        b = b[:72]
    return b


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.
    
    Args:
        password: The plain text password to hash
        
    Returns:
        The bcrypt hashed password as a UTF-8 string
    """
    pw_bytes = _truncate_to_bcrypt_bytes(password)
    hashed = bcrypt.hashpw(pw_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a bcrypt hash.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The bcrypt hashed password to verify against
        
    Returns:
        True if the password matches the hash, False otherwise
    """
    pw_bytes = _truncate_to_bcrypt_bytes(plain_password)
    return bcrypt.checkpw(pw_bytes, hashed_password.encode("utf-8"))
