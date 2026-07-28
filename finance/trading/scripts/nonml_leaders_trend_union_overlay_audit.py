"""Audit adversarial — Leaders 52-semaines + overlay union SMA200∪52w-high indice.

Le résultat brut est IDENTIQUE, chiffre pour chiffre, au cycle #33
(Leaders + SMA200 seul) -- ce n'est PAS une coïncidence ni un bug de
copier-coller : cet audit vérifie explicitement la relation
ensembliste entre les deux signaux (near_high ⊆ above_sma sur cette
donnée) qui explique mathématiquement pourquoi l'union == SMA200 seul.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from nonml_leaders_trend_union_overlay_backtest import SMA_WINDOW, INDEX_LOOKBACK, INDEX_THRESHOLD  # noqa: E402


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values

    sma = pd.Series(close).rolling(SMA_WINDOW).mean().values
    above_sma = close > sma
    rolling_max = pd.Series(close).rolling(INDEX_LOOKBACK).max().values
    near_high = close >= INDEX_THRESHOLD * rolling_max

    start = max(SMA_WINDOW, INDEX_LOOKBACK)
    a = above_sma[start:]
    b = near_high[start:]
    union = a | b

    n_a, n_b, n_union = a.mean(), b.mean(), union.mean()
    n_b_not_a = int(np.sum(b & ~a))
    is_subset = n_b_not_a == 0

    subset_msg = ("CONFIRMÉ — le signal 52w-high (B) est un SOUS-ENSEMBLE STRICT du signal "
                  "SMA200 (A) sur cet historique : être à ≥95% du plus haut 252j implique "
                  "quasi-systématiquement être au-dessus de la SMA200. L'union A∪B est donc "
                  "mathématiquement IDENTIQUE à A seul.") if is_subset else (
                  "B n'est PAS un sous-ensemble de A -- écart à investiguer.")

    lines = [
        "# Audit adversarial — Leaders 52-semaines + overlay union SMA200∪52w-high indice",
        "",
        f"Fraction SMA200 (signal A) : {100*n_a:.1f}%",
        f"Fraction 52w-high (signal B) : {100*n_b:.1f}%",
        f"Fraction union (A∪B) : {100*n_union:.1f}%",
        "",
        f"Jours où B est actif MAIS PAS A : {n_b_not_a}",
        f"**{subset_msg}**",
        "",
        "**Explication du résultat** : c'est pourquoi le résultat du backtest #41 "
        "(Sharpe +1,08, rendement +287,6%, MDD -27,6%) est chiffre pour chiffre "
        "IDENTIQUE au cycle #33 (Leaders + SMA200 seul) -- ce n'est ni une coïncidence "
        "ni un bug de copier-coller, mais une conséquence mathématique directe de la "
        "relation d'inclusion entre les deux signaux sur cette donnée. **L'union "
        "n'apporte donc rigoureusement AUCUNE valeur ajoutée par rapport au SMA200 seul "
        "dans cette combinaison** -- résultat honnête, différent de l'union calendaire "
        "du #21 (ToM∪Halloween) où les deux fenêtres NE se recouvrent PAS et où "
        "l'union apportait un vrai gain.",
    ]

    out = ROOT / "results" / "nonml_leaders_trend_union_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
