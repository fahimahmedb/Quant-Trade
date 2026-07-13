"""Meta-labeling (Lopez de Prado, AFML ch. 3) sur un signal primaire deja
retenu en Etape B (LogitL2). Le modele primaire ne change pas : on ajoute un
modele SECONDAIRE qui apprend a distinguer, parmi les paris pris par le
primaire, ceux qui ont une chance raisonnable d'etre gagnants (label derive
du triple barrier deja construit). Position finale = signe(primaire) *
taille(confiance secondaire), taille bornee [0,1] -> filtre et/ou
dimensionnement continu, sans jamais changer le sens du pari primaire.

Meme discipline anti-fuite que l'Etape B : le secondaire est lui aussi
entraine par walk-forward avec purge/embargo (5 j = horizon H du label), car
son label depend du meme triple barrier que le primaire.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from prediction import walk_forward_proba

__all__ = [
    "primary_signal",
    "secondary_labels",
    "build_secondary_features",
    "meta_size",
    "meta_labeled_position",
]


def primary_signal(X: pd.DataFrame, y: pd.Series, model_factory, t0: int,
                   refit_every: int, embargo: int, standardize: bool = True) -> np.ndarray:
    """p_up OOS du modele primaire (walk-forward, purge/embargo deja appliques)."""
    return walk_forward_proba(X, y, model_factory, t0, refit_every, embargo, standardize)


def secondary_labels(y: pd.Series, primary_pos: np.ndarray) -> pd.Series:
    """Label binaire du secondaire : le pari primaire a-t-il coincide avec le
    signe du label triple-barrier ? NaN la ou le primaire ne parie pas encore
    (warmup walk-forward) - exclu naturellement de l'entrainement secondaire.
    """
    y_sign = np.sign(y.values)
    lab = np.where(primary_pos != 0, (y_sign == primary_pos).astype(float), np.nan)
    return pd.Series(lab, index=y.index)


def build_secondary_features(X: pd.DataFrame, primary_proba: np.ndarray) -> pd.DataFrame:
    """Features du secondaire = features causales du primaire + confiance
    du primaire (|p_up-0.5|*2, dans [0,1]) + p_up lui-meme.
    """
    X2 = X.copy()
    X2["primary_conf"] = np.abs(np.asarray(primary_proba) - 0.5) * 2.0
    X2["primary_p_up"] = primary_proba
    return X2


def meta_size(p_win, mode: str = "continuous", threshold: float = 0.5) -> np.ndarray:
    """Taille de position dans [0,1] a partir de p_win (proba secondaire "pari gagnant").

    mode="threshold"  : filtre tout-ou-rien, discipline minimale demandee.
    mode="continuous" : rampe lineaire 0 (p_win<=0.5) -> 1 (p_win=1), bornee [0,1].
    p_win NaN (secondaire pas encore entraine, warmup) -> taille 0 (pas de
    confiance evaluee = pas de pari, choix conservateur).
    """
    p = np.asarray(p_win, dtype=float)
    if mode == "threshold":
        size = (p > threshold).astype(float)
    else:
        size = np.clip(2.0 * (p - 0.5), 0.0, 1.0)
    return np.where(np.isfinite(p), size, 0.0)


def meta_labeled_position(X: pd.DataFrame, y: pd.Series, model_factory_primary,
                          model_factory_secondary, t0: int, refit_every: int,
                          embargo: int, mode: str = "continuous") -> dict:
    """Pipeline complet primaire -> label secondaire -> secondaire -> position finale.

    Retourne un dict avec la position finale et les objets intermediaires utiles
    au diagnostic (p_up primaire, position primaire brute, p_win secondaire).
    """
    p_up = primary_signal(X, y, model_factory_primary, t0, refit_every, embargo,
                          standardize=True)
    pos_primary = np.where(np.isfinite(p_up), np.where(p_up > 0.5, 1.0, -1.0), 0.0)

    y_sec = secondary_labels(y, pos_primary)
    X_sec = build_secondary_features(X, p_up)
    p_win = walk_forward_proba(X_sec, y_sec, model_factory_secondary, t0, refit_every,
                               embargo, standardize=True)

    size = meta_size(p_win, mode=mode)
    pos_final = pos_primary * size
    return {"pos_final": pos_final, "pos_primary": pos_primary, "p_up": p_up, "p_win": p_win}
