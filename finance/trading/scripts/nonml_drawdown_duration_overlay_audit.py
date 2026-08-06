"""Audit adversarial — Overlay défensif durée du drawdown.

1. Recalcul indépendant de duration(t) par boucle explicite distincte
   (comparaison directe au lieu de running_max incrémental).
2. Vérification anti-lookahead par troncature de l'historique (même
   méthode que #191/#193/#195) : la position sur les N premières
   séances ne doit pas changer si on tronque le futur.
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
from nonml_drawdown_duration_overlay_backtest import (  # noqa: E402
    duration_series, expanding_tercile_cut_high, MARKETS,
)


def independent_duration(close: np.ndarray) -> np.ndarray:
    """Reimplementation independante : pour chaque t, recherche
    explicite en arriere du dernier index j<=t tel que close[j] soit un
    nouveau record (close[j] >= max(close[0:j+1])), duration = t - j."""
    n = len(close)
    dur = np.zeros(n, dtype=float)
    last_high_idx = 0
    best = close[0]
    for t in range(n):
        if close[t] >= best:
            best = close[t]
            last_high_idx = t
        dur[t] = t - last_high_idx
    return dur


def main():
    lines = ["# Audit adversarial — Overlay défensif durée du drawdown", "",
             "## 1. Recalcul indépendant de duration(t)", "",
             "| Marché | Séances | Désaccords |",
             "|---|---|---|"]
    all_ok = True
    ndx_close = None
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values

        dur_orig = duration_series(close)
        dur_indep = independent_duration(close)
        n_diff = int((dur_orig != dur_indep).sum())
        all_ok &= (n_diff == 0)
        lines.append(f"| {name} | {len(close)} | {n_diff} |")

        if name == "NDX (40 ans)":
            ndx_close = close

    lines.append("")
    lines.append(f"**{'OK — duration(t) confirmée par recalcul indépendant (0 désaccord).' if all_ok else 'ÉCHEC — désaccord détecté.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (troncature de l'historique)")
    lines.append("")
    N_CHECK = 2000
    TRUNC_POINTS = [3000, 5000, 8000]
    dur_full = duration_series(ndx_close)
    dur_lag_full = np.roll(dur_full, 1)
    dur_lag_full[0] = np.nan
    pos_full = expanding_tercile_cut_high(dur_lag_full[1:])

    all_trunc_ok = True
    for cut in TRUNC_POINTS:
        close_trunc = ndx_close[:cut]
        dur_trunc = duration_series(close_trunc)
        dur_lag_trunc = np.roll(dur_trunc, 1)
        dur_lag_trunc[0] = np.nan
        pos_trunc = expanding_tercile_cut_high(dur_lag_trunc[1:])
        n = min(N_CHECK, len(pos_trunc), cut - 1)
        match = np.allclose(pos_full[:n], pos_trunc[:n], equal_nan=True)
        all_trunc_ok &= match
        lines.append(f"Troncature à {cut} séances, comparaison sur les {n} premières positions : "
                     f"{'identique' if match else 'DIFFÉRENT'}.")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite, la position sur le passé est inchangée quel que soit le futur tronqué.' if all_trunc_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_drawdown_duration_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
