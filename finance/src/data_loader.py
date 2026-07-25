"""Chargement et controle qualite des donnees NASDAQ Composite (OHLC quotidien).

Format source : export tabule, dates dd/mm/yyyy, decimales '.', volume toujours 0
(inutilisable). Seules les colonnes OHLC sont conservees.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

COLS = ["date", "open", "high", "low", "close"]


def load_ohlc(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep="\t", engine="python")
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={"ouv": "open", "haut": "high", "bas": "low", "clot": "close"})
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y %H:%M")
    df = df[COLS].dropna().sort_values("date").reset_index(drop=True)
    return df


def quality_report(df: pd.DataFrame) -> dict:
    """Controles de coherence. Retourne un dict de diagnostics; leve si fatal."""
    rep: dict = {}
    rep["n_obs"] = len(df)
    rep["start"], rep["end"] = df["date"].iloc[0], df["date"].iloc[-1]
    rep["dup_dates"] = int(df["date"].duplicated().sum())
    # jours ouvres manquants (feries US attendus ~9-10/an, au-dela = trous)
    bdays = pd.bdate_range(df["date"].iloc[0], df["date"].iloc[-1])
    rep["n_bdays"] = len(bdays)
    rep["missing_bdays"] = len(bdays) - len(df)
    # coherence OHLC
    bad_hl = (df["high"] < df[["open", "close"]].max(axis=1)) | (
        df["low"] > df[["open", "close"]].min(axis=1)
    )
    rep["bad_ohlc_rows"] = int(bad_hl.sum())
    # rendements extremes (> 12% en absolu sur un indice large = suspect)
    r = np.log(df["close"]).diff().dropna()
    rep["max_abs_ret_pct"] = float(100 * r.abs().max())
    rep["n_ret_gt_8pct"] = int((r.abs() > 0.08).sum())
    # ecarts calendaires > 5 jours (trous de cotation)
    gaps = df["date"].diff().dt.days.dropna()
    rep["max_gap_days"] = int(gaps.max())
    if rep["dup_dates"] or rep["bad_ohlc_rows"]:
        raise ValueError(f"Donnees corrompues: {rep}")
    return rep


def log_returns_pct(df: pd.DataFrame) -> pd.Series:
    """Rendements log quotidiens close-to-close, en % (convention arch)."""
    r = 100 * np.log(df["close"]).diff()
    r.index = df["date"]
    return r.dropna()


def parkinson_var_pct(df: pd.DataFrame) -> pd.Series:
    """Variance quotidienne range-based de Parkinson (1980), en %^2.

    ATTENTION : ne capture que la variance intra-seance (high/low). L'ecart
    d'ouverture (overnight gap) n'est pas couvert -> biais baissier vis-a-vis
    de la variance close-to-close. A utiliser comme proxy d'EFFICACITE, pas
    comme proxy non biaise.
    """
    hl = np.log(df["high"] / df["low"])
    v = (100 * hl) ** 2 / (4 * np.log(2.0))
    v.index = df["date"]
    return v.iloc[1:]  # aligne sur les rendements (1re obs sans rendement)
