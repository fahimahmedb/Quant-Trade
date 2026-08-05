"""Audit adversarial — Overlay de vol-targeting estimateur Rogers-Satchell.

Recalcul indépendant de la position (boucle explicite recalculant la
variance de Rogers-Satchell elle-même à partir de open/high/low/close,
indépendamment de data_loader.rogers_satchell_var_pct) et test
anti-lookahead.
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
from nonml_rogers_satchell_vol_targeting_overlay_backtest import (  # noqa: E402
    rogers_satchell_vol_position, VOL_WINDOW, TARGET_VOL_ANNUAL, CAP, ANNUALIZATION, MARKETS,
)


def independent_rs_position(df) -> np.ndarray:
    """Recalcul totalement independant : variance de Rogers-Satchell
    calculee directement depuis open/high/low/close (pas via
    data_loader.rogers_satchell_var_pct), puis moyenne roulante et
    position par boucle explicite."""
    o = df["open"].values
    high = df["high"].values
    low = df["low"].values
    close = df["close"].values
    hc = 100.0 * np.log(high / close)
    ho = 100.0 * np.log(high / o)
    lc = 100.0 * np.log(low / close)
    lo = 100.0 * np.log(low / o)
    v = hc * ho + lc * lo  # %^2
    v = v[1:]  # aligne comme rogers_satchell_var_pct (drop 1re obs)

    n = len(v)
    pos = np.ones(n)
    for i in range(VOL_WINDOW + 1, n):
        window = v[i - VOL_WINDOW:i]
        var_mean = max(window.mean(), 0.0)
        vol_ann = np.sqrt(var_mean) * ANNUALIZATION / 100.0
        if vol_ann > 0:
            pos[i] = min(max(TARGET_VOL_ANNUAL / vol_ann, 0.0), CAP)
        else:
            pos[i] = CAP
    return pos


def main():
    lines = ["# Audit adversarial — Overlay de vol-targeting estimateur Rogers-Satchell", "",
             "## 1. Recalcul totalement indépendant (variance Rogers-Satchell recalculée depuis OHLC)", "",
             "| Marché | Écart position max (hors marge de fenêtre) |",
             "|---|---|"]
    all_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        pos_orig = rogers_satchell_vol_position(df)
        pos_indep = independent_rs_position(df)
        start = VOL_WINDOW + 1
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
        pos_before = rogers_satchell_vol_position(df)

        df_pert = df.copy()
        cut = len(df_pert) // 2
        rng = np.random.default_rng(73)
        shock = 1.0 + rng.normal(0, 0.1, len(df_pert) - cut)
        for col in ("open", "high", "low"):
            df_pert.loc[df_pert.index[cut:], col] = df_pert[col].values[cut:] * shock
        pos_after = rogers_satchell_vol_position(df_pert)

        check_end = cut - VOL_WINDOW
        identical = bool(np.allclose(pos_before[:check_end], pos_after[:check_end]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_rogers_satchell_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
