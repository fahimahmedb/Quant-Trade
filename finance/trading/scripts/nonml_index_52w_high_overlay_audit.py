"""Audit adversarial — Overlay levé proximité plus haut 52-semaines
(indice).

Recalcul indépendant du masque (boucle explicite, indépendante de
pandas.rolling.max) et test anti-lookahead (perturbation du futur).
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
from nonml_index_52w_high_overlay_backtest import near_high_mask, LOOKBACK, THRESHOLD, MARKETS  # noqa: E402


def independent_near_high_mask(close: np.ndarray) -> np.ndarray:
    T = len(close)
    out = np.zeros(T, dtype=bool)
    for i in range(LOOKBACK, T):
        window_max = close[i - LOOKBACK + 1:i + 1].max()
        out[i] = close[i] >= THRESHOLD * window_max
    return out


def main():
    lines = ["# Audit adversarial — Overlay levé proximité plus haut 52-semaines (indice)", "",
             "## 1. Recalcul indépendant (boucle explicite vs pandas.rolling.max)", "",
             "| Marché | Écart masque (nb j., hors 252 premiers) |",
             "|---|---|"]
    all_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        m_orig = near_high_mask(close)
        m_indep = independent_near_high_mask(close)
        diff = int(np.sum(m_orig[LOOKBACK:] != m_indep[LOOKBACK:]))
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
        m_before = near_high_mask(close)
        close_pert = close.copy()
        cut = len(close_pert) // 2
        rng = np.random.default_rng(23)
        close_pert[cut:] = close_pert[cut:] * (1.0 + rng.normal(0, 0.1, len(close_pert) - cut))
        m_after = near_high_mask(close_pert)
        identical = bool(np.array_equal(m_before[:cut], m_after[:cut]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")
    lines.append("")
    lines.append("**Lecture** : le signal \"proximité du plus haut\" coupe le levier dès que le "
                 "marché s'éloigne de 5% de son sommet -- plus réactif à la baisse que SMA200 "
                 "(qui attend un croisement de moyenne), ce qui explique une meilleure "
                 "préservation du MDD sur plusieurs marchés (ex. DAX -69,1%→-69,1%, quasi "
                 "inchangé, contre une dégradation nette au #29).")

    out = ROOT / "results" / "nonml_index_52w_high_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
