"""Audit adversarial — Overlay vol-targeting gaté par la profondeur de
drawdown glissante.

Recalcul totalement indépendant (maximum glissant et drawdown recalculés
par boucle explicite, sans pandas.rolling, médiane par tri manuel) et
test anti-lookahead.
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
from nonml_drawdown_depth_vol_targeting_overlay_backtest import (  # noqa: E402
    healthy_dd_mask, combined_position, DD_WINDOW, MEDIAN_WINDOW, MARKETS,
)


def manual_median(window: np.ndarray) -> float:
    s = np.sort(window)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return float(s[mid])
    return float((s[mid - 1] + s[mid]) / 2.0)


def independent_gate(close: np.ndarray) -> np.ndarray:
    T = len(close)
    dd = np.full(T, np.nan)
    for t in range(T):
        lo = max(0, t - DD_WINDOW + 1)
        window = close[lo:t + 1]
        roll_max = window.max()
        dd[t] = close[t] / roll_max - 1.0
    dd_lagged = np.roll(dd, 1)
    dd_lagged[0] = np.nan
    dd_lagged = dd_lagged[1:]  # aligne sur r, longueur T-1

    n = len(dd_lagged)
    gate = np.zeros(n, dtype=bool)
    for t in range(MEDIAN_WINDOW - 1, n):
        w = dd_lagged[t - MEDIAN_WINDOW + 1:t + 1]
        if np.any(np.isnan(w)):
            continue
        med = manual_median(w)
        if not np.isnan(dd_lagged[t]):
            gate[t] = dd_lagged[t] >= med
    return gate


def main():
    lines = ["# Audit adversarial — Overlay vol-targeting gaté par la profondeur de drawdown glissante", "",
             "## 1. Recalcul totalement indépendant (maximum glissant et drawdown par boucle explicite, médiane par tri manuel)", "",
             "| Marché | Désaccords porte (hors marge de fenêtre) | Séances comparées |",
             "|---|---|---|"]
    all_ok = True
    start = DD_WINDOW + MEDIAN_WINDOW
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        if len(close) - 1 <= start:
            continue

        gate_orig = healthy_dd_mask(close)
        gate_indep = independent_gate(close)
        n_diff = int(np.sum(gate_orig[start:] != gate_indep[start:]))
        n_total = len(gate_orig) - start
        all_ok &= (n_diff == 0)
        lines.append(f"| {name} | {n_diff} | {n_total} |")

    lines.append("")
    lines.append(f"**{'OK — porte confirmée par recalcul totalement indépendant.' if all_ok else 'Désaccords détectés.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (perturbation du futur, close)")
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
        close = df["close"].values
        if len(close) - 1 <= start:
            continue
        bh_full = np.log(close[1:] / close[:-1])
        gate_before = healthy_dd_mask(close)
        pos_before = combined_position(bh_full, gate_before)

        cut = len(close) // 2
        rng = np.random.default_rng(73)
        close_pert = close.copy()
        close_pert[cut:] = close_pert[cut:] * (1.0 + rng.normal(0, 0.02, len(close) - cut))
        bh_full_pert = np.log(close_pert[1:] / close_pert[:-1])
        gate_after = healthy_dd_mask(close_pert)
        pos_after = combined_position(bh_full_pert, gate_after)

        check_end = cut - start
        if check_end < 10:
            lines.append(f"| {name} | (fenêtre trop courte pour tester) |")
            continue
        identical = bool(np.allclose(pos_before[start:start + check_end], pos_after[start:start + check_end]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_drawdown_depth_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
