"""Audit adversarial — Overlay vol-targeting gaté par le ratio vol
Parkinson / vol close-to-close.

Recalcul totalement indépendant (variance Parkinson, écart-type
close-to-close, ratio et médiane recalculés par boucle explicite,
indépendamment de pandas.rolling) et test anti-lookahead.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, log_returns_pct, quality_report  # noqa: E402
from nonml_parkinson_c2c_ratio_vol_targeting_overlay_backtest import (  # noqa: E402
    calm_ratio_mask, combined_position, VOL_WINDOW, MEDIAN_WINDOW, MARKETS,
)

ANNUALIZATION = np.sqrt(252)


def manual_median(window: np.ndarray) -> float:
    s = np.sort(window)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return float(s[mid])
    return float((s[mid - 1] + s[mid]) / 2.0)


def manual_std(window: np.ndarray) -> float:
    mu = window.mean()
    return float(np.sqrt(np.sum((window - mu) ** 2) / (len(window) - 1)))


def manual_parkinson_var_pct(df) -> np.ndarray:
    """Recalcul independant de la variance de Parkinson (formule directe,
    sans reutiliser data_loader.py::parkinson_var_pct), en %^2, alignee
    sur log_returns_pct (longueur T-1, premiere ligne du df exclue)."""
    high = df["high"].values[1:]
    low = df["low"].values[1:]
    hl = np.log(high / low)
    return (hl ** 2) / (4.0 * np.log(2.0)) * 1e4


def independent_gate(r_pct: np.ndarray, rv_pct2: np.ndarray) -> np.ndarray:
    n = len(r_pct)
    r_frac = r_pct / 100.0

    vc2c = np.full(n, np.nan)
    for t in range(VOL_WINDOW - 1, n):
        window = r_frac[t - VOL_WINDOW + 1:t + 1]
        vc2c[t] = manual_std(window) * ANNUALIZATION * 100.0
    vc2c_lag = np.roll(vc2c, 1)
    vc2c_lag[0] = np.nan

    vpark = np.full(n, np.nan)
    for t in range(VOL_WINDOW - 1, n):
        window = rv_pct2[t - VOL_WINDOW + 1:t + 1]
        rv_ann = window.mean() * (ANNUALIZATION ** 2)
        vpark[t] = np.sqrt(max(rv_ann, 0.0))
    vpark_lag = np.roll(vpark, 1)
    vpark_lag[0] = np.nan

    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = vpark_lag / vc2c_lag

    gate = np.zeros(n, dtype=bool)
    for t in range(MEDIAN_WINDOW - 1, n):
        window = ratio[t - MEDIAN_WINDOW + 1:t + 1]
        if np.any(np.isnan(window)):
            continue
        med = manual_median(window)
        if not np.isnan(ratio[t]):
            gate[t] = ratio[t] >= med
    return gate


def main():
    lines = ["# Audit adversarial — Overlay vol-targeting gaté par le ratio vol Parkinson / vol close-to-close", "",
             "## 1. Recalcul totalement indépendant (variance Parkinson par formule directe, écart-type "
             "et médiane par boucle explicite)", "",
             "| Marché | Désaccords porte (hors marge de fenêtre) | Séances comparées |",
             "|---|---|---|"]
    all_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        r_pct = log_returns_pct(df).values
        rv_pct2_indep = manual_parkinson_var_pct(df)
        assert len(rv_pct2_indep) == len(r_pct)
        start = VOL_WINDOW + MEDIAN_WINDOW
        if len(r_pct) <= start:
            continue

        gate_orig = calm_ratio_mask(r_pct, rv_pct2_indep)
        gate_indep = independent_gate(r_pct, rv_pct2_indep)
        n_diff = int(np.sum(gate_orig[start:] != gate_indep[start:]))
        n_total = len(gate_orig) - start
        all_ok &= (n_diff == 0)
        lines.append(f"| {name} | {n_diff} | {n_total} |")

    lines.append("")
    lines.append(f"**{'OK — porte confirmée par recalcul totalement indépendant.' if all_ok else 'Désaccords détectés (voir plus bas).'}**")

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
        r_pct = log_returns_pct(df).values
        rv_pct2 = manual_parkinson_var_pct(df)
        start = VOL_WINDOW + MEDIAN_WINDOW
        if len(r_pct) <= start:
            continue
        gate_before = calm_ratio_mask(r_pct, rv_pct2)
        pos_before = combined_position(r_pct, gate_before)

        df_pert = df.copy()
        cut = len(df_pert) // 2
        rng = np.random.default_rng(73)
        shock = 1.0 + rng.normal(0, 0.1, len(df_pert) - cut)
        for col in ("open", "high", "low", "close"):
            df_pert.loc[df_pert.index[cut:], col] = df_pert[col].values[cut:] * shock

        r_pct_pert = log_returns_pct(df_pert).values
        rv_pct2_pert = manual_parkinson_var_pct(df_pert)
        gate_after = calm_ratio_mask(r_pct_pert, rv_pct2_pert)
        pos_after = combined_position(r_pct_pert, gate_after)

        check_end = cut - 1 - start  # log_returns_pct decale d'1 vs df
        if check_end < 10:
            lines.append(f"| {name} | (fenêtre trop courte pour tester) |")
            continue
        identical = bool(np.allclose(pos_before[start:start + check_end], pos_after[start:start + check_end]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_parkinson_c2c_ratio_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
