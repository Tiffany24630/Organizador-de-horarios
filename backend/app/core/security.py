import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError


password_hasher = PasswordHasher()
SESSION_COOKIE = "oh_session"
SESSION_DAYS = 14


def cookie_settings() -> tuple[bool, str]:
    secure = os.environ.get("COOKIE_SECURE", "true" if os.environ.get("DATABASE_URL") else "false").lower() == "true"
    return secure, "none" if secure else "lax"


def normalize_email(email: str) -> str:
    return email.strip().casefold()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def validate_password(password: str) -> None:
    if len(password) < 12:
        raise ValueError("La contraseña debe tener al menos 12 caracteres")
    if password.lower() == password or password.upper() == password:
        raise ValueError("La contraseña debe combinar mayúsculas y minúsculas")
    if not any(character.isdigit() for character in password):
        raise ValueError("La contraseña debe contener al menos un número")


def new_session_token() -> tuple[str, str]:
    token = secrets.token_urlsafe(48)
    return token, hash_token(token)


def hash_token(token: str) -> str:
    secret = os.environ.get("SESSION_HASH_SECRET", "local-development-session-secret")
    return hmac.new(secret.encode(), token.encode(), hashlib.sha256).hexdigest()


def session_expiry() -> datetime:
    return datetime.utcnow() + timedelta(days=SESSION_DAYS)


def new_invite_token() -> tuple[str, str]:
    token = secrets.token_urlsafe(32)
    return token, hash_token(token)

