"""Security utilities for password hashing and verification."""
import bcrypt

MAX_BCRYPT_BYTES = 72


def _truncate_to_bcrypt_bytes(password: str) -> bytes:
    """Encode password as UTF-8 and truncate to bcrypt's 72-byte limit."""
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > MAX_BCRYPT_BYTES:
        password_bytes = password_bytes[:MAX_BCRYPT_BYTES]
    return password_bytes


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt after truncating to 72 bytes.
    Returns the hashed password as a UTF-8 string.
    """
    pw_bytes = _truncate_to_bcrypt_bytes(password)
    hashed = bcrypt.hashpw(pw_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a bcrypt hash.
    Applies the same truncation logic before verification.
    """
    pw_bytes = _truncate_to_bcrypt_bytes(plain_password)
    return bcrypt.checkpw(pw_bytes, hashed_password.encode("utf-8"))
