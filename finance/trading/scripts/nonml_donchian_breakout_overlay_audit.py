"""Audit adversarial — Overlay levé breakout Donchian 20j.

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
from nonml_donchian_breakout_overlay_backtest import breakout_mask, DONCHIAN_WINDOW, MARKETS  # noqa: E402


def independent_breakout_mask(close: np.ndarray) -> np.ndarray:
    T = len(close)
    out = np.zeros(T, dtype=bool)
    for i in range(DONCHIAN_WINDOW, T):
        window_max = close[i - DONCHIAN_WINDOW + 1:i + 1].max()
        out[i] = close[i] >= window_max
    return out


def main():
    lines = ["# Audit adversarial — Overlay levé breakout Donchian 20j", "",
             "## 1. Recalcul indépendant (boucle explicite vs pandas.rolling.max)", "",
             "| Marché | Écart masque (nb j., hors 20 premiers) |",
             "|---|---|"]
    all_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        m_orig = breakout_mask(close)
        m_indep = independent_breakout_mask(close)
        diff = int(np.sum(m_orig[DONCHIAN_WINDOW:] != m_indep[DONCHIAN_WINDOW:]))
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
        m_before = breakout_mask(close)
        close_pert = close.copy()
        cut = len(close_pert) // 2
        rng = np.random.default_rng(37)
        close_pert[cut:] = close_pert[cut:] * (1.0 + rng.normal(0, 0.1, len(close_pert) - cut))
        m_after = breakout_mask(close_pert)
        identical = bool(np.array_equal(m_before[:cut], m_after[:cut]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")
    lines.append("")
    lines.append("**Lecture économique du FAIL** : l'exposition levée est proche de 18-20% du "
                 "temps (contre ~55-75% pour les signaux longs #29/#37) -- un breakout à 20j est "
                 "un événement fréquent et souvent bruité (le prix touche régulièrement son plus "
                 "haut récent sans que cela présage d'une continuation de tendance durable), "
                 "confirmant le même schéma déjà observé au #36 (MACD) : plus le signal de "
                 "tendance est court/réactif, moins il fonctionne bien comme déclencheur de "
                 "levier, comparé aux signaux longs (SMA200, 52w-high).")

    out = ROOT / "results" / "nonml_donchian_breakout_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
