import hashlib


def hash_token(token: str) -> str:
    """Hash a token string using SHA-256 before storing it in the database."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
