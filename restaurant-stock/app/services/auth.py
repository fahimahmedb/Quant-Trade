"""Authentification de l'établissement (Specs V2, F2).

Un compte par installation, session persistante 30 jours sur l'appareil
partagé de la cuisine. Hachage par scrypt (bibliothèque standard) : pas de
dépendance supplémentaire à auditer, et un KDF à coût mémoire réglable.
"""
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy.orm import Session

from app import models
from app.config import SECRET_KEY, SESSION_MAX_AGE_DAYS

SESSION_COOKIE = "resto_session"
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 5

# Paramètres scrypt : n=2^15 tient largement sous la seconde sur un petit VPS.
# maxmem explicite : scrypt demande ici ~33 Mo (128 × n × r) et la limite
# OpenSSL par défaut est de 32 Mo — sans ce réglage, le hachage échoue.
_SCRYPT = {"n": 2**15, "r": 8, "p": 1, "dklen": 32, "maxmem": 64 * 1024 * 1024}


class AuthError(ValueError):
    """Échec d'authentification à présenter tel quel à l'utilisateur."""


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived = hashlib.scrypt(password.encode(), salt=salt, **_SCRYPT)
    return f"scrypt${salt.hex()}${derived.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, salt_hex, hash_hex = stored.split("$")
        if scheme != "scrypt":
            return False
        derived = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex), **_SCRYPT)
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(derived.hex(), hash_hex)


def account_exists(db: Session) -> bool:
    return db.query(models.Account).first() is not None


def create_account(db: Session, *, email: str, password: str, restaurant_name: str | None = None) -> models.Account:
    email = (email or "").strip().lower()
    if "@" not in email:
        raise AuthError("Adresse e-mail invalide.")
    if len(password or "") < 8:
        raise AuthError("Le mot de passe doit faire au moins 8 caractères.")
    if db.query(models.Account).filter(models.Account.email == email).first():
        raise AuthError("Un compte existe déjà pour cette adresse.")

    account = models.Account(
        email=email,
        password_hash=hash_password(password),
        restaurant_name=(restaurant_name or "").strip() or None,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def authenticate(db: Session, *, email: str, password: str, now: datetime | None = None) -> models.Account:
    """Vérifie les identifiants, avec temporisation après échecs répétés (TC-F2-02)."""
    now = now or datetime.utcnow()
    account = (
        db.query(models.Account)
        .filter(models.Account.email == (email or "").strip().lower())
        .first()
    )
    if account is None:
        # Coût comparable à une vérification réelle : pas d'oracle sur l'existence du compte.
        hash_password(password or "")
        raise AuthError("Identifiants incorrects.")

    if account.locked_until and account.locked_until > now:
        remaining = int((account.locked_until - now).total_seconds() // 60) + 1
        raise AuthError(
            f"Trop de tentatives. Réessayez dans {remaining} minute(s)."
        )

    if not verify_password(password or "", account.password_hash):
        account.failed_attempts += 1
        if account.failed_attempts >= MAX_FAILED_ATTEMPTS:
            account.locked_until = now + timedelta(minutes=LOCKOUT_MINUTES)
            account.failed_attempts = 0
            db.commit()
            raise AuthError(
                f"Trop de tentatives. Réessayez dans {LOCKOUT_MINUTES} minutes."
            )
        db.commit()
        raise AuthError("Identifiants incorrects.")

    account.failed_attempts = 0
    account.locked_until = None
    account.last_login_at = now
    db.commit()
    return account


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(SECRET_KEY, salt="resto-session")


def issue_session(account: models.Account) -> str:
    """Jeton signé porteur de l'identifiant du compte et d'un aléa anti-rejeu."""
    return _serializer().dumps({"account_id": account.id, "nonce": secrets.token_hex(8)})


def read_session(db: Session, token: str | None) -> models.Account | None:
    """Compte associé au jeton, ou None si absent, invalide ou expiré."""
    if not token:
        return None
    try:
        payload = _serializer().loads(token, max_age=SESSION_MAX_AGE_DAYS * 86400)
    except (BadSignature, SignatureExpired):
        return None
    return db.get(models.Account, payload.get("account_id"))
