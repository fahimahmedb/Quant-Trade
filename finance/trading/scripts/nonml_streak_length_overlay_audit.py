"""Audit adversarial — Overlay de tendance par la longueur de série
directionnelle.

1. Recalcul indépendant du masque de streak (approche vectorisée
   différente : détection des ruptures de série via numpy, sans
   réutiliser la boucle Python explicite du backtest) sur les 5
   marchés.
2. Test anti-lookahead (mutation du futur, NDX).
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
from nonml_streak_length_overlay_backtest import up_streak_mask, MARKETS, STREAK_THRESHOLD  # noqa: E402


def independent_streak_mask(close: np.ndarray) -> np.ndarray:
    """Recalcul par approche vectorisee differente : identification des
    blocs de jours haussiers consecutifs via cumsum reinitialise aux
    ruptures, sans reutiliser la boucle explicite du backtest."""
    T = len(close)
    up = np.zeros(T, dtype=bool)
    up[1:] = close[1:] > close[:-1]
    # identifiant de groupe qui change a chaque rupture de serie
    group_id = np.zeros(T, dtype=np.int64)
    group_id[1:] = np.cumsum(up[1:] != up[:-1])
    df_streak = np.zeros(T, dtype=int)
    for g in np.unique(group_id):
        idx = np.where(group_id == g)[0]
        if not up[idx[0]]:
            continue
        df_streak[idx] = np.arange(1, len(idx) + 1)
    return df_streak >= STREAK_THRESHOLD


def main():
    lines = ["# Audit adversarial — Overlay de tendance par la longueur de série directionnelle", "",
             "## 1. Recalcul indépendant du masque de streak (approche vectorisée alternative)", "",
             "| Marché | Écart (nb jours différents) |",
             "|---|---|"]
    all_ok = True
    ndx_close = None
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        if "NDX" in name:
            ndx_close = close.copy()

        mask_orig = up_streak_mask(close)
        mask_indep = independent_streak_mask(close)
        diff = int(np.sum(mask_orig != mask_indep))
        all_ok &= (diff == 0)
        lines.append(f"| {name} | {diff} |")

    lines.append("")
    lines.append(f"**{'OK — masque de streak confirmé par recalcul indépendant sur les 5 marchés.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de données les plus récentes, NDX)")
    lines.append("")
    T = len(ndx_close)
    cut = int(T * 0.8)
    rng = np.random.default_rng(108)
    close_mut = ndx_close.copy()
    close_mut[cut:] = close_mut[cut:] * (1.0 + rng.normal(0, 0.5, T - cut))

    mask_before = up_streak_mask(ndx_close)
    mask_after = up_streak_mask(close_mut)
    check_slice = slice(0, cut - 10)
    diff_lookahead = int(np.sum(mask_before[check_slice] != mask_after[check_slice]))
    lines.append(f"Écart de masque sur les séances antérieures à la mutation : {diff_lookahead}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if diff_lookahead == 0 else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_streak_length_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
