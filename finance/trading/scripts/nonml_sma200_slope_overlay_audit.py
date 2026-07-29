"""Audit adversarial — Overlay levé filtre de pente SMA200 :
1) recalcul indépendant de la SMA200 et du masque de pente (boucle
   explicite, indépendante de pandas.rolling) ;
2) test anti-lookahead (perturbation du futur) ;
3) mesure de la fraction de jours levés PENDANT les grands krachs connus
   (drawdown ≥40%), pour comparaison avec le filtre de NIVEAU (#29) —
   teste l'hypothèse motivant ce cycle : la pente coupe-t-elle plus tôt
   que le niveau en début de retournement ?
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
from nonml_sma200_slope_overlay_backtest import sma_slope_positive_mask, SMA_WINDOW, SLOPE_LAG, MARKETS  # noqa: E402
from nonml_sma200_trend_overlay_backtest import above_sma_mask  # noqa: E402


def independent_slope_mask(close: np.ndarray) -> np.ndarray:
    T = len(close)
    sma = np.full(T, np.nan)
    for i in range(SMA_WINDOW - 1, T):
        sma[i] = close[i - SMA_WINDOW + 1:i + 1].mean()

    out = np.zeros(T, dtype=bool)
    for i in range(SMA_WINDOW - 1 + SLOPE_LAG, T):
        out[i] = sma[i] > sma[i - SLOPE_LAG]
    return out


def main():
    lines = ["# Audit adversarial — Overlay levé filtre de pente SMA200", "",
             "## 1. Recalcul indépendant (boucle explicite vs pandas.rolling)",
             "",
             "| Marché | Écart masque (nb j., hors marge de fenêtre) |",
             "|---|---|"]
    all_ok = True
    dfs = {}
    start_margin = SMA_WINDOW + SLOPE_LAG
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dfs[name] = df
        close = df["close"].values
        m_orig = sma_slope_positive_mask(close)
        m_indep = independent_slope_mask(close)
        diff = int(np.sum(m_orig[start_margin:] != m_indep[start_margin:]))
        all_ok &= (diff == 0)
        lines.append(f"| {name} | {diff} |")

    lines.append("")
    lines.append(f"**{'OK — masque de pente confirmé par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (perturbation du futur)")
    lines.append("")
    lines.append("| Marché | Décisions passées identiques après perturbation future |")
    lines.append("|---|---|")
    anti_leak_ok = True
    for name, df in dfs.items():
        close = df["close"].values
        m_before = sma_slope_positive_mask(close)

        close_pert = close.copy()
        cut = len(close_pert) // 2
        rng = np.random.default_rng(151)
        close_pert[cut:] = close_pert[cut:] * (1.0 + rng.normal(0, 0.1, len(close_pert) - cut))
        m_after = sma_slope_positive_mask(close_pert)

        identical = bool(np.array_equal(m_before[:cut], m_after[:cut]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")

    lines.append("")
    lines.append("## 3. Exposition pendant les grands krachs (drawdown ≥40%) : pente (#66) vs niveau (#29)")
    lines.append("")
    lines.append("| Marché | %j levé PENDANT drawdown≥40% (pente, #66) | %j levé PENDANT drawdown≥40% (niveau, #29) |")
    lines.append("|---|---|---|")
    for name, df in dfs.items():
        close = df["close"].values
        m_slope = sma_slope_positive_mask(close)
        m_level = above_sma_mask(close)
        rolling_max = np.maximum.accumulate(close)
        dd = close / rolling_max - 1.0
        in_crash = dd <= -0.40
        if in_crash.any():
            pct_slope = 100 * m_slope[in_crash].mean()
            pct_level = 100 * m_level[in_crash].mean()
        else:
            pct_slope = pct_level = float("nan")
        lines.append(f"| {name} | {pct_slope:.1f}% | {pct_level:.1f}% |")

    lines.append("")
    lines.append("**Lecture** : si le filtre de pente coupe réellement plus tôt en début de "
                 "retournement que le filtre de niveau, le %j levé pendant les grands krachs "
                 "devrait être PLUS FAIBLE pour la pente (#66) que pour le niveau (#29). Les "
                 "chiffres ci-dessus permettent de juger cette hypothèse sans qu'elle ait été "
                 "utilisée pour ajuster un paramètre — la comparaison est faite APRÈS coup, à "
                 "titre d'explication du résultat déjà obtenu, pas de retuning.")

    out = ROOT / "results" / "nonml_sma200_slope_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
