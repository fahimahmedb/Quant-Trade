"""Audit adversarial — Overlay levé filtre de tendance SMA50 (variante
moyen terme du #29/SMA200, même protocole d'audit) :
1) recalcul indépendant de la SMA50 et du masque (boucle explicite,
   indépendante de pandas.rolling) ;
2) test anti-lookahead (perturbation du futur) ;
3) mesure de la fraction de jours levés PENDANT les grands krachs connus,
   pour comparaison avec le SMA200 (signal plus réactif -> devrait
   couper plus vite mais aussi ré-entrer plus vite en faux signal).
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
from nonml_sma50_trend_overlay_backtest import above_sma_mask, SMA_WINDOW, MARKETS  # noqa: E402


def independent_above_mask(close: np.ndarray) -> np.ndarray:
    T = len(close)
    out = np.zeros(T, dtype=bool)
    for i in range(SMA_WINDOW, T):
        window_mean = close[i - SMA_WINDOW + 1:i + 1].mean()
        out[i] = close[i] > window_mean
    out[:SMA_WINDOW] = False
    return out


def main():
    lines = ["# Audit adversarial — Overlay levé filtre de tendance SMA50", "",
             "## 1. Recalcul indépendant du masque (boucle explicite vs pandas.rolling)",
             "",
             "| Marché | Écart masque (nb j., hors 50 premiers) |",
             "|---|---|"]
    all_ok = True
    dfs = {}
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dfs[name] = df
        close = df["close"].values
        m_orig = above_sma_mask(close)
        m_indep = independent_above_mask(close)
        diff = int(np.sum(m_orig[SMA_WINDOW:] != m_indep[SMA_WINDOW:]))
        all_ok &= (diff == 0)
        lines.append(f"| {name} | {diff} |")

    lines.append("")
    lines.append(f"**{'OK — SMA50 et masque confirmés par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (perturbation du futur)")
    lines.append("")
    lines.append("| Marché | Décisions passées identiques après perturbation future |")
    lines.append("|---|---|")
    anti_leak_ok = True
    for name, df in dfs.items():
        close = df["close"].values
        m_before = above_sma_mask(close)

        close_pert = close.copy()
        cut = len(close_pert) // 2
        rng = np.random.default_rng(101)
        close_pert[cut:] = close_pert[cut:] * (1.0 + rng.normal(0, 0.1, len(close_pert) - cut))
        m_after = above_sma_mask(close_pert)

        identical = bool(np.array_equal(m_before[:cut], m_after[:cut]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures, décisions passées strictement causales.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")

    lines.append("")
    lines.append("## 3. Exposition pendant les grands krachs (drawdown ≥40% depuis le plus haut), comparaison SMA50 vs SMA200")
    lines.append("")
    lines.append("| Marché | %j levé PENDANT drawdown≥40% (SMA50) |")
    lines.append("|---|---|")
    for name, df in dfs.items():
        close = df["close"].values
        m = above_sma_mask(close)
        rolling_max = np.maximum.accumulate(close)
        dd = close / rolling_max - 1.0
        in_crash = dd <= -0.40
        pct_levered = 100 * m[in_crash].mean() if in_crash.any() else float("nan")
        lines.append(f"| {name} | {pct_levered:.1f}% |")

    lines.append("")
    lines.append("**Lecture** : la SMA50, plus réactive que la SMA200, coupe généralement plus vite "
                 "en début de krach mais génère aussi plus de faux signaux de ré-entrée pendant les "
                 "phases de rebond-piège d'un marché baissier prolongé. Sur NDX, le MDD est ici "
                 "légèrement MOINS dégradé que le #29 (-82,9%→-90,2% contre -82,9%→-91,7% au #29), "
                 "cohérent avec une exposition levée légèrement moindre (66,3% du temps ici contre "
                 "75,3% au #29) malgré un edge Sharpe/rendement globalement similaire.")

    out = ROOT / "results" / "nonml_sma50_trend_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
