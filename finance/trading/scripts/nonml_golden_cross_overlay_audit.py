"""Audit adversarial — Overlay levé Golden Cross SMA50/SMA200.

Recalcul indépendant du masque (boucle explicite, indépendante de
pandas.rolling) et test anti-lookahead (perturbation du futur, même
protocole que le cycle #29).
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
from nonml_golden_cross_overlay_backtest import golden_cross_mask, SMA_SHORT, SMA_LONG, MARKETS  # noqa: E402


def independent_golden_mask(close: np.ndarray) -> np.ndarray:
    T = len(close)
    out = np.zeros(T, dtype=bool)
    for i in range(SMA_LONG, T):
        sma_s = close[i - SMA_SHORT + 1:i + 1].mean()
        sma_l = close[i - SMA_LONG + 1:i + 1].mean()
        out[i] = sma_s > sma_l
    return out


def main():
    lines = ["# Audit adversarial — Overlay levé Golden Cross SMA50/SMA200", "",
             "## 1. Recalcul indépendant (boucle explicite vs pandas.rolling)", "",
             "| Marché | Écart masque (nb j., hors 200 premiers) |",
             "|---|---|"]
    all_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        m_orig = golden_cross_mask(close)
        m_indep = independent_golden_mask(close)
        diff = int(np.sum(m_orig[SMA_LONG:] != m_indep[SMA_LONG:]))
        all_ok &= (diff == 0)
        lines.append(f"| {name} | {diff} |")

    lines.append("")
    lines.append(f"**{'OK — masque confirmé par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (perturbation du futur)")
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
        m_before = golden_cross_mask(close)
        close_pert = close.copy()
        cut = len(close_pert) // 2
        rng = np.random.default_rng(13)
        close_pert[cut:] = close_pert[cut:] * (1.0 + rng.normal(0, 0.1, len(close_pert) - cut))
        m_after = golden_cross_mask(close_pert)
        identical = bool(np.array_equal(m_before[:cut], m_after[:cut]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_golden_cross_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
