"""Audit adversarial — Overlay de vol-targeting estimateur ATR.

Recalcul indépendant de la position (True Range et lissage de Wilder
recalculés par boucle explicite, indépendamment de prediction.py::_atr)
et test anti-lookahead.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from nonml_atr_vol_targeting_overlay_backtest import (  # noqa: E402
    atr_vol_position, TARGET_VOL_ANNUAL, CAP, ANNUALIZATION, MARKETS,
)

N_WILDER = 14


def independent_atr_position(df) -> np.ndarray:
    """Recalcul totalement independant : True Range et lissage de Wilder
    recalcules par boucle explicite (sans pandas.ewm), sans reutiliser
    prediction.py::_atr."""
    high = df["high"].values
    low = df["low"].values
    close = df["close"].values
    T = len(close)

    tr = np.empty(T)
    tr[0] = high[0] - low[0]
    for t in range(1, T):
        hl = high[t] - low[t]
        hc = abs(high[t] - close[t - 1])
        lc = abs(low[t] - close[t - 1])
        tr[t] = max(hl, hc, lc)

    alpha = 1.0 / N_WILDER
    atr = np.empty(T)
    atr[0] = tr[0]
    for t in range(1, T):
        atr[t] = alpha * tr[t] + (1 - alpha) * atr[t - 1]

    atr_pct = atr / close
    vol_ann = atr_pct * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    vol_lagged = vol_lagged[1:]

    with np.errstate(divide="ignore", invalid="ignore"):
        pos = TARGET_VOL_ANNUAL / vol_lagged
    pos = np.clip(pos, 0.0, CAP)
    return np.nan_to_num(pos, nan=1.0)


def main():
    lines = ["# Audit adversarial — Overlay de vol-targeting estimateur ATR", "",
             "## 1. Recalcul totalement indépendant (True Range et lissage de Wilder par boucle explicite)", "",
             "| Marché | Écart position max (hors marge de fenêtre) |",
             "|---|---|"]
    all_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        pos_orig = atr_vol_position(df)
        pos_indep = independent_atr_position(df)
        start = 15
        max_diff = float(np.max(np.abs(pos_orig[start:] - pos_indep[start:])))
        all_ok &= (max_diff < 1e-9)
        lines.append(f"| {name} | {max_diff:.2e} |")

    lines.append("")
    lines.append(f"**{'OK — position confirmée par recalcul totalement indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (perturbation du futur, OHLC)")
    lines.append("")
    lines.append("| Marché | Décisions passées identiques après perturbation future |")
    lines.append("|---|---|")
    anti_leak_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        pos_before = atr_vol_position(df)

        df_pert = df.copy()
        cut = len(df_pert) // 2
        rng = np.random.default_rng(73)
        shock = 1.0 + rng.normal(0, 0.1, len(df_pert) - cut)
        for col in ("open", "high", "low", "close"):
            df_pert.loc[df_pert.index[cut:], col] = df_pert[col].values[cut:] * shock
        pos_after = atr_vol_position(df_pert)

        check_end = cut - 15
        identical = bool(np.allclose(pos_before[:check_end], pos_after[:check_end]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_atr_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
