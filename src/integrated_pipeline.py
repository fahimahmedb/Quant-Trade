"""Pipeline integree Etape B -> meta-labeling -> overlay (Etape D optimisee).

Objectif (cf. CLAUDE.md, Etape D "en cours") : verifier que la COMBINAISON
des 3 composantes deja construites reduit le max drawdown du SIGNAL ACTIF
LogitL2 lui-meme (pas seulement celui de Buy & Hold, deja traite en
Etape D/etape_D_overlay_optimized.md).

Ne reinvente aucun des 3 moteurs deja valides ailleurs dans le repo -
reutilises tels quels :
  - src/prediction.py    : build_features, triple_barrier_labels,
                           walk_forward_proba (LogitL2 primaire, Etape B)
  - src/meta_labeling.py : secondary_labels, build_secondary_features,
                           meta_size, SECONDARY_MODELS["LogitL2"] (secondaire
                           meilleure variante retenue, DSR=0.866, cf.
                           results/meta_labeling_multi.md)
  - src/overlay.py       : walk_forward_vol_forecast, vol_target_exposure,
                           extreme_cut, EXTREME_CUT_FRAC (GJR-GARCH(1,1)-t,
                           cap 2.0x / coupe 90e percentile = meilleure
                           combinaison du grid-search fige, cf.
                           results/etape_D_overlay_optimized.md)

Position finale generique (les 5 variantes du protocole fige, cf.
scripts/run_integrated_pipeline.py, ne sont que des cas particuliers de la
meme formule ; chaque composante absente = neutre, valeur 1) :

    pos_final = signe(LogitL2) x confiance_meta_labeling x exposition_overlay

Aucun parametre n'est retouche par rapport aux etudes qui les ont etablis :
T0=750, refit 21 j, purge/embargo 5 j (triple barrier H=5 j), couts 5 bps
aller-retour, overlay cap 2.0x / coupe au 90e percentile in-sample (coupe
totale, EXTREME_CUT_FRAC=0.0). Discipline anti data-snooping : ces reglages
proviennent de recherches DEJA figees et publiees (meta_labeling_multi.md,
etape_D_overlay_optimized.md) - on ne les re-optimise pas ici, on verifie
seulement leur effet COMBINE sur le drawdown du signal actif.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from data_loader import log_returns_pct
from meta_labeling import (
    SECONDARY_MODELS,
    build_secondary_features,
    meta_size,
    secondary_labels,
)
from overlay import EXTREME_CUT_FRAC, extreme_cut, vol_target_exposure, walk_forward_vol_forecast
from prediction import build_features, triple_barrier_labels, walk_forward_proba

__all__ = [
    "T0", "REFIT_EVERY", "EMBARGO", "H", "VOL_SPAN", "BARRIER_MULT", "COST_BPS",
    "OVERLAY_CAP", "OVERLAY_PCTL", "VARIANTS", "build_pipeline",
]

# ------------------------------------------------------------------ protocole FIGE
# Identique Etape B / meta_labeling_multi (primaire + secondaire).
T0, REFIT_EVERY, EMBARGO, H = 750, 21, 5, 5
VOL_SPAN, BARRIER_MULT = 20, 1.5
COST_BPS = 5.0
# Identique etape_D_overlay_optimized.md (meilleure combinaison de la grille
# figee cap in {1.00,1.25,1.50,2.00} x pctl in {90,95,99}).
OVERLAY_CAP = 2.0
OVERLAY_PCTL = 90.0

# Univers FIGE des 5 variantes evaluees (cf. scripts/run_integrated_pipeline.py),
# aucun ajout a posteriori - n_trials=5 pour le DSR.
VARIANTS = ["BuyHold", "LogitL2", "LogitL2+Meta", "LogitL2+Overlay", "LogitL2+Meta+Overlay"]


def primary_logit():
    """Modele primaire : LogitL2, identique a l'Etape B (meilleur signal actif trouve)."""
    return SECONDARY_MODELS["LogitL2"]()


def secondary_logit():
    """Modele secondaire du meta-labeling : LogitL2, meilleure variante retenue
    (DSR=0.866 sur les 3 secondaires testes, cf. results/meta_labeling_multi.md)."""
    return SECONDARY_MODELS["LogitL2"]()


def build_pipeline(df_raw: pd.DataFrame) -> dict:
    """Calcule, en un seul passage walk-forward par composante, les 5 positions
    finales de l'univers fige.

    df_raw : DataFrame issu de data_loader.load_ohlc (colonne 'date' NON
    indexee - requis tel quel par log_returns_pct, qui lit df_raw['date']).

    Retourne un dict :
      - "positions" : {nom_variante: array de longueur n (positions finales)}
      - "r_fwd"      : rendement forward t->t+1 (convention backtest() Etape B)
      - "dates"      : index date (longueur n)
      - "n"          : nombre de seances
      - objets intermediaires (p_up, p_win, meta_conf, exposure) pour diagnostic.
    """
    df = df_raw.set_index("date")
    close = df["close"].astype(float)
    logp = np.log(close)
    r_fwd = (logp.shift(-1) - logp).values  # r_fwd[t] = rendement log t -> t+1
    n = len(df)
    dates = df.index

    # --- 1) Primaire LogitL2 (Etape B, walk-forward purge/embargo, inchange)
    X = build_features(df)
    y = triple_barrier_labels(df.reset_index(), horizon=H, vol_span=VOL_SPAN, mult=BARRIER_MULT)
    y.index = df.index
    p_up = walk_forward_proba(X, y, primary_logit, T0, REFIT_EVERY, EMBARGO, standardize=True)
    pos_primary = np.where(np.isfinite(p_up), np.where(p_up > 0.5, 1.0, -1.0), 0.0)

    # --- 2) Secondaire meta-labeling LogitL2 (meilleure variante, cf. docstring module)
    y_sec = secondary_labels(y, pos_primary)
    X_sec = build_secondary_features(X, p_up)
    p_win = walk_forward_proba(X_sec, y_sec, secondary_logit, T0, REFIT_EVERY, EMBARGO,
                               standardize=True)
    meta_conf = meta_size(p_win, mode="continuous")  # dans [0,1], 0 pendant le warmup

    # --- 3) Overlay vol-targeting GJR-t (cap 2.0x, coupe 90e pctl in-sample, coupe totale)
    r_pct = log_returns_pct(df_raw).values  # longueur n-1 ; r_pct[t] == r_fwd[t] (meme
    # quantite : log_returns_pct decale l'index d'une ligne par construction - cf. note
    # ci-dessous - donc r_pct et r_fwd partagent exactement les memes valeurs numeriques
    # aux memes positions t < n-1, seule la derniere position de r_fwd (NaN) n'a pas
    # d'equivalent dans r_pct).
    fc = walk_forward_vol_forecast(r_pct, T0, REFIT_EVERY, extreme_pctl=OVERLAY_PCTL)
    expo = vol_target_exposure(fc["vol_fcst"], fc["vol_target"], OVERLAY_CAP)
    expo = extreme_cut(expo, fc["vol_fcst"], fc["vol_thresh"], EXTREME_CUT_FRAC)
    exposure = np.nan_to_num(expo, nan=0.0)
    # Complete a la longueur n (une position de plus que r_pct) par 0 : cette derniere
    # position n'est jamais evaluee dans l'OOS (oos = arange(T0, n-1), cf. script appelant).
    exposure = np.concatenate([exposure, [0.0]])

    # --- 4) Position finale generique (chaque variante = cas particulier de la formule)
    positions = {
        "BuyHold": np.ones(n),
        "LogitL2": pos_primary,
        "LogitL2+Meta": pos_primary * meta_conf,
        "LogitL2+Overlay": pos_primary * exposure,
        "LogitL2+Meta+Overlay": pos_primary * meta_conf * exposure,
    }
    return {
        "positions": positions,
        "r_fwd": r_fwd,
        "dates": dates,
        "n": n,
        "p_up": p_up,
        "p_win": p_win,
        "meta_conf": meta_conf,
        "exposure": exposure,
    }
