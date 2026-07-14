"""Etape D - Overlay de gestion du risque : vol-targeting + coupe en regime extreme.

Contexte de decision (cf. CLAUDE.md, resultats deja etablis A/B/C, ne pas
redemontrer) : aucun signal directionnel (Etape B) ne bat durablement Buy &
Hold net de couts et deflate (DSR). Le modele de volatilite GJR-GARCH(1,1)-t
(Etape C) est en revanche statistiquement robuste (SPA valide sur
l'historique long, p=0.0000 a h=1). L'edge exploitable n'est donc PAS
directionnel mais de GESTION DU RISQUE : ce module pilote l'EXPOSITION d'une
position Buy & Hold (toujours long) a partir des previsions de volatilite
walk-forward du GJR-t, sans jamais reinventer le moteur GARCH
(src/volatility.py : fit_arch, garch_path, ARCH_SPECS["GJR-t"] reutilises
tels quels).

Univers de variantes FIGE AVANT evaluation (cf. scripts/run_etape_d.py), pas
plus :
  1. Vol-targeting seul :
       exposition_t = clip(vol_cible / vol_prevue_t, 0, cap)
     vol_cible = vol annualisee REALISEE de Buy & Hold sur la fenetre
     d'entrainement (expansive, recalculee a chaque re-estimation - jamais
     une constante magique). cap = plafond de levier EXPLICITE (jamais de
     levier illimite, cf. scripts/run_etape_d.py).
  2. Vol-targeting + coupe en regime extreme :
       exposition -> exposition * EXTREME_CUT_FRAC si vol_prevue_t depasse
     le EXTREME_PCTL-eme percentile IN-SAMPLE (fenetre d'entrainement
     uniquement) de la distribution de la vol GJR-t annualisee. Regle fixee
     A PRIORI (95e percentile, coupe totale a 0 - simple a justifier : le
     top 5% des regimes de vol predite est historiquement associe aux
     krachs, cf. NDX -83% 2000-2002), jamais recalibree sur le futur ni
     optimisee sur l'OOS.

Le cout applique est le meme que backtest() de src/prediction.py : cost_bps
aller-retour preleve sur le turnover |delta exposition|.
"""
from __future__ import annotations

import numpy as np

from volatility import ANNUALIZE, fit_arch, garch_path, params_dict

# Regle a priori, fixee AVANT evaluation (anti data-snooping) : seuil de coupe
# = 95e percentile in-sample de la vol GJR-t annualisee ; coupe totale (0).
# Pas de balayage de seuils : un seul choix, justifie ci-dessus, jamais
# retouche apres avoir vu les resultats OOS.
EXTREME_PCTL = 95.0
EXTREME_CUT_FRAC = 0.0


def realized_ann_vol_pct(r_pct: np.ndarray) -> float:
    """Vol annualisee (%) des rendements log en % (convention arch), sur la fenetre donnee."""
    r_pct = np.asarray(r_pct, dtype=float)
    return float(r_pct.std(ddof=1) * ANNUALIZE)


def vol_target_exposure(vol_fcst_ann_pct: np.ndarray, vol_target_ann_pct, cap: float) -> np.ndarray:
    """expo_t = clip(vol_cible / vol_prevue_t, 0, cap).

    vol_target_ann_pct peut etre un scalaire ou un tableau (recalcule au fil
    du temps sur la fenetre d'entrainement). cap : plafond de levier explicite.
    """
    vol_fcst_ann_pct = np.asarray(vol_fcst_ann_pct, dtype=float)
    vol_target_ann_pct = np.asarray(vol_target_ann_pct, dtype=float)
    expo = vol_target_ann_pct / np.maximum(vol_fcst_ann_pct, 1e-8)
    return np.clip(expo, 0.0, cap)


def extreme_cut(exposure: np.ndarray, vol_fcst_ann_pct: np.ndarray,
                 threshold_ann_pct: np.ndarray, cut_frac: float = EXTREME_CUT_FRAC) -> np.ndarray:
    """Reduit l'exposition a cut_frac x son niveau vol-targeting si vol_prevue > seuil.

    threshold_ann_pct : seuil FIXE sur la fenetre d'entrainement (percentile
    in-sample de la distribution des previsions passees), jamais recalibre
    avec le futur - peut etre un scalaire ou un tableau aligne sur exposure.
    """
    exposure = np.asarray(exposure, dtype=float).copy()
    vol_fcst_ann_pct = np.asarray(vol_fcst_ann_pct, dtype=float)
    threshold_ann_pct = np.asarray(threshold_ann_pct, dtype=float)
    mask = vol_fcst_ann_pct > threshold_ann_pct
    exposure[mask] = exposure[mask] * cut_frac
    return exposure


def walk_forward_vol_forecast(r: np.ndarray, t0: int, refit_every: int,
                              extreme_pctl: float = EXTREME_PCTL) -> dict:
    """Previsions GJR-t walk-forward (1 pas) + calibration in-sample de l'overlay.

    Meme cadence que l'Etape C (fenetre expansive, re-estimation tous les
    `refit_every` jours, reutilise fit_arch/garch_path/ARCH_SPECS["GJR-t"]).
    A chaque re-estimation sur r[:tr] (passe uniquement, aucune fuite) :
      - vol_fcst[t]   : vol GJR-t annualisee prevue pour r[t] (info t-1)
      - vol_target[t] : vol annualisee REALISEE de r[:tr] (cible Buy & Hold,
                        recalculee a chaque refit, jamais une constante figee
                        a la main)
      - vol_thresh[t] : extreme_pctl-eme percentile in-sample de la vol GJR-t
                        annualisee sur r[:tr] (seuil de coupe, passe uniquement)

    `extreme_pctl` : percentile in-sample utilise pour le seuil de coupe
    extreme (parametre, defaut = EXTREME_PCTL = 95e, cf. module docstring;
    fait partie de l'univers de variantes FIGE avant evaluation - cf. le
    script appelant pour la liste exacte des valeurs testees).
    Retourne des tableaux de taille len(r), NaN avant t0 (periode de burn-in,
    hors evaluation - meme convention que l'Etape C).
    """
    T = len(r)
    vol_fcst = np.full(T, np.nan)
    vol_target = np.full(T, np.nan)
    vol_thresh = np.full(T, np.nan)
    for tr in range(t0, T, refit_every):
        block = range(tr, min(tr + refit_every, T))
        res = fit_arch(r[:tr], "GJR-t")
        p = params_dict(res)
        path = garch_path(r, p, gjr=True)  # taille T+1 ; path[t] = var(r[t] | info t-1)
        vol_ann_in = ANNUALIZE * np.sqrt(path[:tr])  # distribution in-sample (passe uniquement)
        thresh = float(np.percentile(vol_ann_in, extreme_pctl))
        vtar = realized_ann_vol_pct(r[:tr])
        for t in block:
            vol_fcst[t] = ANNUALIZE * np.sqrt(path[t])
            vol_target[t] = vtar
            vol_thresh[t] = thresh
    return {"vol_fcst": vol_fcst, "vol_target": vol_target, "vol_thresh": vol_thresh}


def walk_forward_vol_forecast_multi(r: np.ndarray, t0: int, refit_every: int,
                                    extreme_pctls: list) -> dict:
    """Comme walk_forward_vol_forecast, mais calcule vol_thresh pour PLUSIEURS
    percentiles en un seul passage (un seul fit GJR-t par fenetre de refit,
    reutilise pour toutes les valeurs de extreme_pctls - le percentile
    in-sample est un simple quantile de la meme distribution passee, pas un
    nouveau fit). Utilise par le grid-search (scripts/run_etape_d_optimize.py)
    pour eviter de refitter le meme GJR-t une fois par combo.

    Retourne {"vol_fcst":..., "vol_target":..., "vol_thresh": {pctl: array}}.
    """
    T = len(r)
    vol_fcst = np.full(T, np.nan)
    vol_target = np.full(T, np.nan)
    vol_thresh = {pc: np.full(T, np.nan) for pc in extreme_pctls}
    for tr in range(t0, T, refit_every):
        block = range(tr, min(tr + refit_every, T))
        res = fit_arch(r[:tr], "GJR-t")
        p = params_dict(res)
        path = garch_path(r, p, gjr=True)
        vol_ann_in = ANNUALIZE * np.sqrt(path[:tr])
        threshes = {pc: float(np.percentile(vol_ann_in, pc)) for pc in extreme_pctls}
        vtar = realized_ann_vol_pct(r[:tr])
        for t in block:
            vol_fcst[t] = ANNUALIZE * np.sqrt(path[t])
            vol_target[t] = vtar
            for pc in extreme_pctls:
                vol_thresh[pc][t] = threshes[pc]
    return {"vol_fcst": vol_fcst, "vol_target": vol_target, "vol_thresh": vol_thresh}


def build_overlay_positions(r: np.ndarray, t0: int, refit_every: int, cap: float,
                            with_extreme_cut: bool, extreme_pctl: float = EXTREME_PCTL,
                            cut_frac: float = EXTREME_CUT_FRAC,
                            vol_fc: dict | None = None) -> dict:
    """Construit les positions (exposition Buy & Hold, toujours long) walk-forward.

    `cap`, `extreme_pctl`, `cut_frac` sont parametrables (grid-search figee,
    cf. scripts/run_etape_d_optimize.py) sans toucher au moteur GARCH.
    `vol_fc` : previsions walk-forward deja calculees (dict de
    walk_forward_vol_forecast) - permet de reutiliser le meme fit GJR-t pour
    plusieurs valeurs de extreme_pctl (le percentile ne depend que de la
    distribution in-sample de vol_fcst, pas d'un nouveau fit). Si None,
    recalcule (comportement d'origine, compatible ascendant).
    Retourne {"pos": array, "vol_fcst":..., "vol_target":..., "vol_thresh":...}.
    pos = NaN -> 0 avant t0 (periode de burn-in, hors evaluation).
    """
    fc = walk_forward_vol_forecast(r, t0, refit_every, extreme_pctl) if vol_fc is None else vol_fc
    expo = vol_target_exposure(fc["vol_fcst"], fc["vol_target"], cap)
    if with_extreme_cut:
        expo = extreme_cut(expo, fc["vol_fcst"], fc["vol_thresh"], cut_frac)
    pos = np.nan_to_num(expo, nan=0.0)
    out = dict(fc)
    out["pos"] = pos
    return out
