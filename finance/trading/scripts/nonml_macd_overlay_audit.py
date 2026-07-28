"""Audit adversarial — Overlay levé croisement MACD.

Recalcul indépendant des EMA (récursion explicite, indépendante de
pandas.ewm) et test anti-lookahead.
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
from nonml_macd_overlay_backtest import macd_bullish_mask, EMA_FAST, EMA_SLOW, EMA_SIGNAL, START_IDX, MARKETS  # noqa: E402


def ema_explicit(x: np.ndarray, span: int) -> np.ndarray:
    alpha = 2.0 / (span + 1.0)
    out = np.empty_like(x, dtype=float)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = alpha * x[i] + (1 - alpha) * out[i - 1]
    return out


def independent_macd_mask(close: np.ndarray) -> np.ndarray:
    ema_fast = ema_explicit(close, EMA_FAST)
    ema_slow = ema_explicit(close, EMA_SLOW)
    macd_line = ema_fast - ema_slow
    signal_line = ema_explicit(macd_line, EMA_SIGNAL)
    return macd_line > signal_line


def main():
    lines = ["# Audit adversarial — Overlay levé croisement MACD", "",
             "## 1. Recalcul indépendant (récursion EMA explicite vs pandas.ewm)", "",
             "| Marché | Écart masque (nb j., hors marge de convergence) |",
             "|---|---|"]
    all_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        m_orig = macd_bullish_mask(close)
        m_indep = independent_macd_mask(close)
        # marge de convergence : les tout premiers points de l'EMA dependent
        # de la seed (out[0]=x[0]), ecart attendu proche du debut seulement
        diff = int(np.sum(m_orig[START_IDX:] != m_indep[START_IDX:]))
        all_ok &= (diff == 0)
        lines.append(f"| {name} | {diff} |")

    lines.append("")
    lines.append(f"**{'OK — masque MACD confirmé par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")

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
        m_before = macd_bullish_mask(close)
        close_pert = close.copy()
        cut = len(close_pert) // 2
        rng = np.random.default_rng(19)
        close_pert[cut:] = close_pert[cut:] * (1.0 + rng.normal(0, 0.1, len(close_pert) - cut))
        m_after = macd_bullish_mask(close_pert)
        identical = bool(np.array_equal(m_before[:cut], m_after[:cut]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")
    lines.append("")
    lines.append("**Lecture économique du FAIL** : l'exposition levée est proche de 50% (contre "
                 "~70-75% pour SMA200/#29) -- le MACD est un signal beaucoup plus réactif (bruité), "
                 "générant plus de faux signaux/allers-retours en régime sans tendance nette, avec "
                 "des coûts de transaction accrus, contrairement au filtre plus lent SMA200/Golden "
                 "Cross qui a mieux fonctionné.")

    out = ROOT / "results" / "nonml_macd_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
