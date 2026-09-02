"""Réglages globaux de l'application.

Valeurs volontairement simples (constantes + une table Settings à une seule
ligne pour ce qui doit rester ajustable par le gérant sans redéploiement).
Pas de gestion multi-environnement : le MVP tourne pour un seul restaurant.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Photos de bons de livraison (F1). Hors dépôt Git : données du restaurant.
UPLOAD_DIR = DATA_DIR / "uploads"

DATABASE_URL = os.environ.get(
    "RESTAURANT_STOCK_DATABASE_URL",
    f"sqlite:///{DATA_DIR / 'restaurant_stock.db'}",
)

# Nombre de jours utilisés pour calculer la consommation moyenne glissante
# servant de base à la suggestion de commande (section 4.6 du brief).
ROLLING_AVERAGE_WINDOW_DAYS = 7

# Valeurs par défaut si le gérant n'a pas défini de seuil manuel pour un
# ingrédient : seuil d'alerte = consommation moyenne journalière * SAFETY_DAYS,
# quantité cible après commande = consommation moyenne journalière * TARGET_DAYS.
# Modifiable depuis la page Réglages (table Settings), pas en dur pour toujours.
DEFAULT_SAFETY_DAYS = 2
DEFAULT_TARGET_DAYS = 5

# --- Exploitation (F2) ----------------------------------------------------
# Durée de session : l'appareil de la cuisine est partagé et rarement
# reconnecté, on évite de redemander le mot de passe toutes les semaines.
SESSION_MAX_AGE_DAYS = 30

# Cookie de session en Secure : à laisser à 1 en production (HTTPS
# obligatoire, cf. README). Mis à 0 uniquement pour un accès local en http.
SESSION_COOKIE_SECURE = os.environ.get("RESTAURANT_STOCK_COOKIE_SECURE", "1") != "0"


def _load_or_create_secret_key() -> str:
    """Clé de signature des sessions.

    Priorité à la variable d'environnement (production). À défaut, une clé
    est générée puis conservée dans data/secret_key : sans persistance, un
    redémarrage déconnecterait tout le monde.
    """
    from_env = os.environ.get("RESTAURANT_STOCK_SECRET_KEY")
    if from_env:
        return from_env
    key_file = DATA_DIR / "secret_key"
    if key_file.exists():
        return key_file.read_text().strip()
    import secrets

    key = secrets.token_urlsafe(48)
    key_file.write_text(key)
    key_file.chmod(0o600)
    return key


SECRET_KEY = _load_or_create_secret_key()
