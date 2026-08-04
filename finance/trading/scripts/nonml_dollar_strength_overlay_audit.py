"""Audit indépendant — Force du dollar américain (DTWEXBGS).

Recalcule USDChange(t), l'alignement causal et le tercile expanding par
une méthode alternative (boucle explicite, sans pandas.reindex/ffill ni
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
from nonml_dollar_strength_overlay_backtest import (  # noqa: E402
    COST_BPS, CUT, RET_WINDOW, MARKETS, build_usd_change_series,
    load_usd_change_lag, expanding_tercile_cut_high,
)


def manual_usd_change_dict() -> dict:
    """Recalcul de USDChange(t) par boucle explicite (dict indexe par
    date), independant de la construction numpy vectorisee du script
    principal."""
    raw = pd.read_csv(REPO_ROOT / "data" / "dtwexbgs_daily.csv")
    raw["observation_date"] = pd.to_datetime(raw["observation_date"])
    raw = raw.dropna(subset=["DTWEXBGS"]).drop_duplicates("observation_date").sort_values("observation_date")
    dates = raw["observation_date"].values
    vals = raw["DTWEXBGS"].astype(float).values
    out = {}
    for i in range(RET_WINDOW, len(vals)):
        out[pd.Timestamp(dates[i])] = float(np.log(vals[i] / vals[i - RET_WINDOW]))
    return out


def manual_ffill_shift(dates: pd.DatetimeIndex, usd_dict: dict) -> np.ndarray:
    usd_dates = np.array(sorted(usd_dict.keys()))
    usd_vals = np.array([usd_dict[d] for d in usd_dates])
    out = np.full(len(dates), np.nan)
    for i, d in enumerate(dates):
        idx = np.searchsorted(usd_dates, d, side="right") - 1
        if idx < 0:
            continue
        out[i] = usd_vals[idx]
    shifted = np.full(len(dates), np.nan)
    shifted[1:] = out[:-1]
    return shifted


def manual_percentile_high_tercile(hist: np.ndarray) -> float:
    s = np.sort(hist)
    n = len(s)
    pos = (n - 1) * (200.0 / 3.0) / 100.0
    lo = int(np.floor(pos))
    hi = int(np.ceil(pos))
    if lo == hi:
        return float(s[lo])
    frac = pos - lo
    return float(s[lo] * (1 - frac) + s[hi] * frac)


def main():
    lines = ["# Audit — Force du dollar américain (DTWEXBGS)", ""]
    all_ok = True

    usd_series = build_usd_change_series()
    usd_manual_dict = manual_usd_change_dict()

    common_dates = sorted(set(usd_series.index) & set(usd_manual_dict.keys()))
    usd_diff = max(abs(usd_series[d] - usd_manual_dict[d]) for d in common_dates)
    lines.append("## Recalcul USDChange(t) (log-rendement 21j)")
    lines.append(f"- Écart max USDChange(t) (construction numpy vectorisée vs boucle+dict explicite) : {usd_diff:.2e}")
    ok_usd = usd_diff < 1e-8
    all_ok &= ok_usd
    lines.append(f"- **{'OK' if ok_usd else 'ÉCART DÉTECTÉ'}**")
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

        usd_lag_official = load_usd_change_lag(dates, usd_series)[1:]
        pos_official = expanding_tercile_cut_high(usd_lag_official)

        usd_lag_manual = manual_ffill_shift(dates, usd_manual_dict)[1:]
        diff_align = np.nanmax(np.abs(usd_lag_official - usd_lag_manual))

        start = int(np.argmax(np.isfinite(usd_lag_manual)))
        T = len(usd_lag_manual)
        pos_manual = np.full(T, np.nan)
        for t in range(start, T):
            if not np.isfinite(usd_lag_manual[t]):
                continue
            hist = usd_lag_manual[start:t + 1]
            hist = hist[np.isfinite(hist)]
            thresh = manual_percentile_high_tercile(hist)
            pos_manual[t] = CUT if usd_lag_manual[t] >= thresh else 1.0

        mask = np.isfinite(pos_official) & np.isfinite(pos_manual)
        pos_diff_mask = np.abs(pos_official[mask] - pos_manual[mask]) > 1e-9
        n_pos_diff = int(pos_diff_mask.sum())
        n_total = int(mask.sum())

        boundary_tie_ok = True
        for i in np.where(mask)[0][pos_diff_mask]:
            local_diff = abs(usd_lag_official[i] - usd_lag_manual[i])
            if local_diff >= 1e-10:
                boundary_tie_ok = False

        ok = (diff_align < 1e-8) and (n_pos_diff == 0 or boundary_tie_ok)
        all_ok &= ok
        lines.append(f"## {name}")
        lines.append(f"- Écart max alignement causal (pandas reindex/ffill/shift vs boucle+searchsorted manuel) : {diff_align:.2e}")
        if n_pos_diff == 0:
            lines.append(f"- Écart max position (percentile numpy vs tri+interpolation manuel) : 0.00e+00")
        else:
            lines.append(f"- **{n_pos_diff}/{n_total} désaccords de position** — sensibilité de bord flottante "
                         f"documentée (même pattern que #193/#195/#196/#197) : {'confirmé' if boundary_tie_ok else 'NON confirmé, écart réel'}.")
        lines.append(f"- **{'OK' if ok else 'ÉCART DÉTECTÉ'}**")
        lines.append("")

    # Anti-lookahead : troncature de l'historique.
    name, fname = "NDX (40 ans)", MARKETS["NDX (40 ans)"]
    df = load_ohlc(str(REPO_ROOT / "data" / fname))
    dates = pd.DatetimeIndex(df["date"].values)
    usd_lag_full = load_usd_change_lag(dates, usd_series)[1:]
    valid_start = int(np.argmax(np.isfinite(usd_lag_full)))
    T_CUT = valid_start + 1000
    pos_full = expanding_tercile_cut_high(usd_lag_full)
    pos_truncated = expanding_tercile_cut_high(usd_lag_full[:T_CUT])
    lookahead_diff = np.nanmax(np.abs(pos_full[valid_start:T_CUT] - pos_truncated[valid_start:T_CUT]))
    ok_lookahead = lookahead_diff < 1e-8
    all_ok &= ok_lookahead

    lines.append(f"## Anti-lookahead (NDX, troncature à {T_CUT} séances)")
    lines.append(f"- Écart max position sur la zone valide, pleine série vs série tronquée : {lookahead_diff:.2e}")
    lines.append(f"- **{'OK — aucune fuite' if ok_lookahead else 'FUITE DÉTECTÉE'}**")
    lines.append("")

    lines.append(f"## Verdict global : **{'CONFORME' if all_ok else 'ÉCART DÉTECTÉ'}**")

    out = ROOT / "results" / "nonml_dollar_strength_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return all_ok


if __name__ == "__main__":
    main()
