import hashlib
import os
import hmac


# BASIC SHA-256 HASH (good for anonymizing voter IDs)

def sha256_hash(text: str) -> str:
    """
    Returns a hexadecimal SHA-256 hash of the given text.
    Used for:
      - voter_id hashing before writing to blockchain
    """
    return hashlib.sha256(text.encode()).hexdigest()


# SALTED HASH (for passwords, if needed)

def generate_salt(length: int = 16) -> str:
    """
    Returns a securely generated random salt.
    """
    return os.urandom(length).hex()


def salted_hash(password: str, salt: str) -> str:
    """
    Creates a salted SHA-256 hash for secure password storage.
    """
    return hashlib.sha256((password + salt).encode()).hexdigest()


# CONSTANT-TIME HASH COMPARISON

def safe_compare(hash1: str, hash2: str) -> bool:
    """
    Compares two hashes in constant time.
    Prevents timing attacks.
    """
    return hmac.compare_digest(hash1, hash2)


# PASSWORD VERIFICATION HELPER

def verify_password(password: str, salt: str, stored_hash: str) -> bool:
    """
    Verifies that a given password matches
    the stored salted-hash value.
    """
    return safe_compare(
        salted_hash(password, salt),
        stored_hash
    )
