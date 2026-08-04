"""Audit indépendant — Prime de risque de variance (VIX - vol réalisée).

Recalcule VRP, le tercile expanding et la position par une méthode
alternative (boucle explicite, sans np.percentile ni pandas.rolling),
compare au résultat committé du backtest. Vérifie aussi l'absence de
fuite : le seuil au temps t ne doit dépendre que de vrp[0:t+1].
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from nonml_variance_risk_premium_overlay_backtest import (  # noqa: E402
    COST_BPS, CUT, VOL_WINDOW, ANNUALIZATION, MARKETS, load_vix_lag,
    expanding_tercile_cut,
)


def manual_percentile_low_tercile(hist: np.ndarray) -> float:
    """Recalcul du 33,33e percentile par tri explicite (interpolation
    lineaire, methode 'linear' de numpy) -- implementation independante
    de np.percentile pour verification."""
    s = np.sort(hist)
    n = len(s)
    pos = (n - 1) * (100.0 / 3.0) / 100.0
    lo = int(np.floor(pos))
    hi = int(np.ceil(pos))
    if lo == hi:
        return float(s[lo])
    frac = pos - lo
    return float(s[lo] * (1 - frac) + s[hi] * frac)


def manual_rv(r_log: np.ndarray) -> np.ndarray:
    """Vol realisee annualisee, recalcul explicite (boucle) de la
    fenetre glissante VOL_WINDOW, sans pandas.rolling."""
    T = len(r_log)
    rv = np.full(T, np.nan)
    for t in range(VOL_WINDOW - 1, T):
        window = r_log[t - VOL_WINDOW + 1:t + 1]
        rv[t] = np.std(window, ddof=1) * ANNUALIZATION * 100.0
    return rv


def main():
    lines = ["# Audit — Prime de risque de variance (VIX - vol réalisée)", ""]
    all_ok = True

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        dates = pd.DatetimeIndex(df["date"].values)
        r_log = np.log(close[1:] / close[:-1])

        # Recalcul officiel (import direct du script de backtest)
        rv_ann_official = pd.Series(r_log).rolling(VOL_WINDOW).std().values * ANNUALIZATION * 100.0
        rv_lag_official = np.concatenate([[np.nan], rv_ann_official[:-1]])
        vix_lag_official = load_vix_lag(dates)[1:]
        vrp_official = vix_lag_official - rv_lag_official
        pos_official = expanding_tercile_cut(vrp_official)

        # Recalcul independant (boucle explicite, methode differente)
        rv_manual = manual_rv(r_log)
        rv_lag_manual = np.concatenate([[np.nan], rv_manual[:-1]])
        vrp_manual = vix_lag_official - rv_lag_manual

        vrp_diff = np.nanmax(np.abs(vrp_official - vrp_manual))

        # Position recalculee avec le percentile manuel
        T = len(vrp_manual)
        pos_manual = np.full(T, np.nan)
        start = int(np.argmax(np.isfinite(vrp_manual)))
        for t in range(start, T):
            if not np.isfinite(vrp_manual[t]):
                continue
            hist = vrp_manual[start:t + 1]
            hist = hist[np.isfinite(hist)]
            thresh = manual_percentile_low_tercile(hist)
            pos_manual[t] = CUT if vrp_manual[t] <= thresh else 1.0

        mask = np.isfinite(pos_official) & np.isfinite(pos_manual)
        pos_diff = np.max(np.abs(pos_official[mask] - pos_manual[mask])) if mask.any() else np.nan

        ok = (vrp_diff < 1e-8) and (pos_diff < 1e-8)
        all_ok &= ok
        lines.append(f"## {name}")
        lines.append(f"- Écart max VRP (rolling/std pandas vs boucle+std manuel ddof=1) : {vrp_diff:.2e}")
        lines.append(f"- Écart max position (percentile numpy vs tri+interpolation manuel) : {pos_diff:.2e}")
        lines.append(f"- **{'OK' if ok else 'ÉCART DÉTECTÉ'}**")
        lines.append("")

    # Verification anti-lookahead : le seuil au temps t ne doit PAS changer
    # si on tronque l'historique futur (invariance stricte).
    name, fname = "NDX (40 ans)", MARKETS["NDX (40 ans)"]
    df = load_ohlc(str(REPO_ROOT / "data" / fname))
    close = df["close"].values
    dates = pd.DatetimeIndex(df["date"].values)
    r_log = np.log(close[1:] / close[:-1])
    rv_ann = pd.Series(r_log).rolling(VOL_WINDOW).std().values * ANNUALIZATION * 100.0
    rv_lag = np.concatenate([[np.nan], rv_ann[:-1]])
    vix_lag = load_vix_lag(dates)[1:]
    vrp = vix_lag - rv_lag

    pos_full = expanding_tercile_cut(vrp)
    T_CUT = 2000
    pos_truncated = expanding_tercile_cut(vrp[:T_CUT])
    lookahead_diff = np.nanmax(np.abs(pos_full[:T_CUT] - pos_truncated))

    lines.append("## Anti-lookahead (NDX, troncature à 2000 séances)")
    lines.append(f"- Écart max position[0:2000] pleine série vs série tronquée : {lookahead_diff:.2e}")
    ok_lookahead = lookahead_diff < 1e-8
    all_ok &= ok_lookahead
    lines.append(f"- **{'OK — aucune fuite (le seuil expanding ne dépend jamais du futur)' if ok_lookahead else 'FUITE DÉTECTÉE'}**")
    lines.append("")

    lines.append(f"## Verdict global : **{'CONFORME' if all_ok else 'ÉCART DÉTECTÉ'}**")

    out = ROOT / "results" / "nonml_variance_risk_premium_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return all_ok


if __name__ == "__main__":
    main()
