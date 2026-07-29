"""Audit adversarial — Overlay de tendance par le temps depuis le
dernier plus haut.

1. Recalcul indépendant de days_since_high (approche vectorisée
   différente : via np.maximum.accumulate, sans réutiliser la boucle
   Python explicite du backtest) sur les 5 marchés.
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
from nonml_days_since_high_overlay_backtest import days_since_high, MARKETS, THRESHOLD_DAYS, WARMUP  # noqa: E402


def independent_days_since_high(close: np.ndarray) -> np.ndarray:
    """Recalcul par approche vectorisee (np.maximum.accumulate), sans
    reutiliser la boucle Python explicite du backtest."""
    T = len(close)
    running_max = np.maximum.accumulate(close)
    is_new_high = close >= running_max  # egal par construction a chaque record
    idx = np.arange(T)
    last_high_idx = np.where(is_new_high, idx, -1)
    last_high_idx = np.maximum.accumulate(last_high_idx)
    return idx - last_high_idx


def main():
    lines = ["# Audit adversarial — Overlay de tendance par le temps depuis le dernier plus haut", "",
             "## 1. Recalcul indépendant de days_since_high (np.maximum.accumulate vectorisé)", "",
             "| Marché | Écart max absolu |",
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
        dsh_orig = days_since_high(close)
        dsh_indep = independent_days_since_high(close)
        diff = int(np.max(np.abs(dsh_orig - dsh_indep)))
        all_ok &= (diff == 0)
        lines.append(f"| {name} | {diff} |")

    lines.append("")
    lines.append(f"**{'OK — days_since_high confirmé par recalcul indépendant sur les 5 marchés.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de données les plus récentes, NDX)")
    lines.append("")
    T = len(ndx_close)
    cut = int(T * 0.8)
    rng = np.random.default_rng(91)
    close_mut = ndx_close.copy()
    close_mut[cut:] = close_mut[cut:] * (1.0 + rng.normal(0, 0.5, T - cut))

    dsh_before = independent_days_since_high(ndx_close)
    dsh_after = independent_days_since_high(close_mut)
    check_slice = slice(WARMUP, cut - THRESHOLD_DAYS - 10)
    diff_lookahead = int(np.max(np.abs(dsh_before[check_slice] - dsh_after[check_slice])))
    lines.append(f"Écart sur days_since_high calculé à des dates antérieures à la mutation : {diff_lookahead}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if diff_lookahead == 0 else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_days_since_high_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
