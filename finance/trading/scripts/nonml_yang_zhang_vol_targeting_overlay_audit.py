"""Audit adversarial — Overlay de vol-targeting estimateur Yang-Zhang.

Recalcul indépendant de la position (boucle explicite recalculant les
variances overnight/ouverture-clôture/Rogers-Satchell par une seconde
implémentation, indépendamment de yang_zhang_vol_ann_lagged) et test
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
from nonml_yang_zhang_vol_targeting_overlay_backtest import (  # noqa: E402
    yang_zhang_vol_position, VOL_WINDOW, TARGET_VOL_ANNUAL, CAP, ANNUALIZATION, MARKETS,
)


def manual_var(window: np.ndarray) -> float:
    mu = window.mean()
    return float(np.sum((window - mu) ** 2) / (len(window) - 1))


def independent_yz_position(df) -> np.ndarray:
    """Recalcul totalement independant : chaque composante (overnight,
    ouverture-cloture, Rogers-Satchell) recalculee bar par bar par boucle
    explicite, variance par formule manuelle (sans np.var), sans
    reutiliser yang_zhang_vol_ann_lagged."""
    o_ = df["open"].values
    high = df["high"].values
    low = df["low"].values
    close = df["close"].values
    T = len(close)
    n = VOL_WINDOW
    k = 0.34 / (1.34 + (n + 1) / (n - 1))

    o = [np.nan] * T
    c = [np.nan] * T
    rs = [np.nan] * T
    for t in range(1, T):
        o[t] = np.log(o_[t] / close[t - 1])
        c[t] = np.log(close[t] / o_[t])
        hc = np.log(high[t] / close[t])
        ho = np.log(high[t] / o_[t])
        lc = np.log(low[t] / close[t])
        lo = np.log(low[t] / o_[t])
        rs[t] = hc * ho + lc * lo
    o, c, rs = np.array(o), np.array(c), np.array(rs)

    vol_lagged = np.full(T - 1, np.nan)
    for i in range(n, T - 1):
        wo = o[i - n + 1:i + 1]
        wc = c[i - n + 1:i + 1]
        wrs = rs[i - n + 1:i + 1]
        if np.any(np.isnan(wo)):
            continue
        var_o = manual_var(wo)
        var_c = manual_var(wc)
        var_rs = float(np.sum(wrs) / n)
        var_yz = max(var_o + k * var_c + (1 - k) * var_rs, 0.0)
        vol_lagged[i] = np.sqrt(var_yz) * ANNUALIZATION

    with np.errstate(divide="ignore", invalid="ignore"):
        pos = TARGET_VOL_ANNUAL / vol_lagged
    pos = np.clip(pos, 0.0, CAP)
    return np.nan_to_num(pos, nan=1.0)


def main():
    lines = ["# Audit adversarial — Overlay de vol-targeting estimateur Yang-Zhang", "",
             "## 1. Recalcul totalement indépendant (composantes recalculées bar par bar, variance manuelle)", "",
             "| Marché | Écart position max (hors marge de fenêtre) |",
             "|---|---|"]
    all_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        pos_orig = yang_zhang_vol_position(df)
        pos_indep = independent_yz_position(df)
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
        pos_before = yang_zhang_vol_position(df)

        df_pert = df.copy()
        cut = len(df_pert) // 2
        rng = np.random.default_rng(73)
        shock = 1.0 + rng.normal(0, 0.1, len(df_pert) - cut)
        for col in ("open", "high", "low"):
            df_pert.loc[df_pert.index[cut:], col] = df_pert[col].values[cut:] * shock
        pos_after = yang_zhang_vol_position(df_pert)

        check_end = cut - VOL_WINDOW
        identical = bool(np.allclose(pos_before[:check_end], pos_after[:check_end]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_yang_zhang_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
