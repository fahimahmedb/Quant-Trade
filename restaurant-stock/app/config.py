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
