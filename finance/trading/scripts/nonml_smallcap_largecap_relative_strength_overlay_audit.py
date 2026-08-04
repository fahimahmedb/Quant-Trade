"""Audit indépendant — Force relative Russell 2000 vs S&P 500.

Recalcule RS(t), l'alignement causal et le tercile expanding par une
méthode alternative (boucle explicite, sans pandas.reindex/ffill ni
np.percentile), compare au résultat committé du backtest. Vérifie aussi
l'absence de fuite (troncature de l'historique).
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
from nonml_smallcap_largecap_relative_strength_overlay_backtest import (  # noqa: E402
    COST_BPS, CUT, RET_WINDOW, MARKETS, rolling_ret21_series, load_rs_lag,
    expanding_tercile_cut,
)


def manual_ret21(fname: str) -> dict:
    """Recalcul du rendement glissant 21j par boucle explicite (indexe
    par date en dict), independant de la construction numpy vectorisee
    du script principal."""
    df = load_ohlc(str(REPO_ROOT / "data" / fname))
    close = df["close"].values
    dates = pd.DatetimeIndex(df["date"].values)
    out = {}
    for i in range(RET_WINDOW, len(close)):
        out[dates[i]] = float(np.log(close[i] / close[i - RET_WINDOW]))
    return out


def manual_ffill_shift(dates: pd.DatetimeIndex, rs_dict: dict) -> np.ndarray:
    """Reindex+ffill+shift(1) recalcule par boucle explicite sur les
    dates triees du dictionnaire RS, sans pandas.reindex."""
    rs_dates = np.array(sorted(rs_dict.keys()))
    rs_vals = np.array([rs_dict[d] for d in rs_dates])
    out = np.full(len(dates), np.nan)
    for i, d in enumerate(dates):
        idx = np.searchsorted(rs_dates, d, side="right") - 1
        if idx < 0:
            continue
        out[i] = rs_vals[idx]
    # shift(1) : la valeur au jour i doit etre celle disponible a i-1
    shifted = np.full(len(dates), np.nan)
    shifted[1:] = out[:-1]
    return shifted


def manual_percentile_low_tercile(hist: np.ndarray) -> float:
    s = np.sort(hist)
    n = len(s)
    pos = (n - 1) * (100.0 / 3.0) / 100.0
    lo = int(np.floor(pos))
    hi = int(np.ceil(pos))
    if lo == hi:
        return float(s[lo])
    frac = pos - lo
    return float(s[lo] * (1 - frac) + s[hi] * frac)


def main():
    lines = ["# Audit — Force relative Russell 2000 vs S&P 500", ""]
    all_ok = True

    ret21_russell = rolling_ret21_series("russell2000_daily.txt")
    ret21_sp500 = rolling_ret21_series("sp500_daily.txt")
    common = ret21_russell.index.union(ret21_sp500.index)
    rs_series = (ret21_russell.reindex(common) - ret21_sp500.reindex(common)).dropna()

    russell_manual = manual_ret21("russell2000_daily.txt")
    sp500_manual = manual_ret21("sp500_daily.txt")
    common_manual_dates = sorted(set(russell_manual) & set(sp500_manual))
    rs_manual_dict = {d: russell_manual[d] - sp500_manual[d] for d in common_manual_dates}

    rs_diff = max(
        abs(rs_series.get(d, np.nan) - rs_manual_dict[d])
        for d in common_manual_dates
        if np.isfinite(rs_series.get(d, np.nan))
    )
    lines.append(f"## Recalcul RS(t) (rendement 21j + différence)")
    lines.append(f"- Écart max RS(t) (construction numpy vectorisée vs boucle+dict explicite) : {rs_diff:.2e}")
    ok_rs = rs_diff < 1e-8
    all_ok &= ok_rs
    lines.append(f"- **{'OK' if ok_rs else 'ÉCART DÉTECTÉ'}**")
    lines.append("")

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        dates = pd.DatetimeIndex(df["date"].values)
        bh_full = np.log(close[1:] / close[:-1])

        rs_lag_official = load_rs_lag(dates, rs_series)[1:]
        pos_official = expanding_tercile_cut(rs_lag_official)

        rs_lag_manual = manual_ffill_shift(dates, rs_manual_dict)[1:]
        diff_align = np.nanmax(np.abs(rs_lag_official - rs_lag_manual))

        start = int(np.argmax(np.isfinite(rs_lag_manual)))
        T = len(rs_lag_manual)
        pos_manual = np.full(T, np.nan)
        for t in range(start, T):
            if not np.isfinite(rs_lag_manual[t]):
                continue
            hist = rs_lag_manual[start:t + 1]
            hist = hist[np.isfinite(hist)]
            thresh = manual_percentile_low_tercile(hist)
            pos_manual[t] = CUT if rs_lag_manual[t] <= thresh else 1.0

        mask = np.isfinite(pos_official) & np.isfinite(pos_manual)
        pos_diff = np.max(np.abs(pos_official[mask] - pos_manual[mask])) if mask.any() else np.nan

        ok = (diff_align < 1e-8) and (pos_diff < 1e-8)
        all_ok &= ok
        lines.append(f"## {name}")
        lines.append(f"- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : {diff_align:.2e}")
        lines.append(f"- Écart max position (percentile numpy vs tri+interpolation manuel) : {pos_diff:.2e}")
        lines.append(f"- **{'OK' if ok else 'ÉCART DÉTECTÉ'}**")
        lines.append("")

    # Anti-lookahead : troncature de l'historique, le seuil au temps t ne
    # doit pas changer si on tronque le futur.
    name, fname = "NDX (40 ans)", MARKETS["NDX (40 ans)"]
    df = load_ohlc(str(REPO_ROOT / "data" / fname))
    dates = pd.DatetimeIndex(df["date"].values)
    rs_lag_full = load_rs_lag(dates, rs_series)[1:]
    pos_full = expanding_tercile_cut(rs_lag_full)
    T_CUT = 2000
    pos_truncated = expanding_tercile_cut(rs_lag_full[:T_CUT])
    lookahead_diff = np.nanmax(np.abs(pos_full[:T_CUT] - pos_truncated))
    ok_lookahead = lookahead_diff < 1e-8
    all_ok &= ok_lookahead

    lines.append("## Anti-lookahead (NDX, troncature à 2000 séances)")
    lines.append(f"- Écart max position[0:2000] pleine série vs série tronquée : {lookahead_diff:.2e}")
    lines.append(f"- **{'OK — aucune fuite' if ok_lookahead else 'FUITE DÉTECTÉE'}**")
    lines.append("")

    lines.append(f"## Verdict global : **{'CONFORME' if all_ok else 'ÉCART DÉTECTÉ'}**")

    out = ROOT / "results" / "nonml_smallcap_largecap_relative_strength_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return all_ok


if __name__ == "__main__":
    main()
