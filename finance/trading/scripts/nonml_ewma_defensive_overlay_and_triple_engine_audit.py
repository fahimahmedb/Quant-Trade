"""Audit adversarial — Overlay défensif EWMA + ensemble 3 moteurs.

1. Recalcul indépendant du chemin EWMA walk-forward (boucle Python
   explicite, récursion manuelle, sans réutiliser ewma_path() vectorisé)
   à un échantillon de dates.
2. Test anti-lookahead (mutation du futur NDX).
3. Recalcul indépendant de la moyenne à 3 (boucle Python explicite).
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
from nonml_ewma_defensive_overlay_and_triple_engine_backtest import (  # noqa: E402
    ewma_walkforward_position, T0, REFIT_EVERY, LAM, TARGET_VOL_ANNUAL, CAP,
)


def independent_ewma_position_at(r: np.ndarray, i: int) -> float:
    """Recalcul manuel : retrouve le dernier refit tr <= i, recalcule
    mu_tr (train-only, SANS re-demeanage -- correction du bug trouve au
    premier essai de cet audit, voir docstring du backtest) et la
    recursion EWMA depuis t=0 jusqu'a i (boucle Python explicite)."""
    tr = T0 + ((i - T0) // REFIT_EVERY) * REFIT_EVERY
    mu_tr = sum(r[:tr]) / tr
    eps = [x - mu_tr for x in r]
    train_eps = eps[:tr]
    mean_train = sum(train_eps) / len(train_eps)
    var_train = sum((x - mean_train) ** 2 for x in train_eps) / len(train_eps)
    s2 = var_train
    for t in range(i):
        s2 = LAM * s2 + (1 - LAM) * eps[t] ** 2
    vol_ann = (max(s2, 0.0) * 252) ** 0.5
    return vol_ann


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    r = np.log(close[1:] / close[:-1])

    pos_orig = ewma_walkforward_position(r)
    T = len(r)

    lines = ["# Audit adversarial — Overlay défensif EWMA + ensemble 3 moteurs", "",
             "## 1. Recalcul indépendant du chemin EWMA (récursion manuelle, boucle Python explicite)", "",
             "| Date (indice) | Vol annualisée originale | Vol annualisée recalculée | Écart relatif |",
             "|---|---|---|---|"]
    check_idx = [T0 + 5, T0 + 500, T0 + 3000, T0 + 6000]
    all_ok = True
    for i in check_idx:
        if i >= T:
            continue
        # reconstruit la vol annualisee originale a partir de la position (inversion)
        vol_lagged_i1 = pos_orig[i + 1] if i + 1 < T else np.nan
        # plus simple : recalcule directement via la fonction pour comparaison croisee
        indep_vol = independent_ewma_position_at(r, i)
        # comparaison indirecte : verifie coherence de la position elle-meme au jour i+1
        vt = TARGET_VOL_ANNUAL / indep_vol if indep_vol > 0 else np.nan
        vt = max(0.0, min(CAP, vt)) if np.isfinite(vt) else 1.0
        orig_pos = pos_orig[i + 1] if i + 1 < T else np.nan
        diff = abs(vt - orig_pos) if np.isfinite(orig_pos) else np.nan
        ok = (diff is not None) and (diff < 1e-6)
        all_ok &= bool(ok)
        lines.append(f"| {i} | -- | {indep_vol:.4f} | position: {diff:.2e} |")
    lines.append("")
    lines.append(f"**{'OK — chemin EWMA confirmé par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de données NDX les plus récentes)")
    lines.append("")
    cut = int(T * 0.8)
    rng = np.random.default_rng(124)
    r_mut = r.copy()
    r_mut[cut:] = r_mut[cut:] + rng.normal(0, 0.05, T - cut)
    pos_mut = ewma_walkforward_position(r_mut)
    check_slice = slice(0, cut - REFIT_EVERY - 10)
    diff_lookahead = float(np.nanmax(np.abs(pos_orig[check_slice] - pos_mut[check_slice])))
    lines.append(f"Écart max sur les positions passées (avant mutation) : {diff_lookahead:.2e}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if diff_lookahead < 1e-9 else 'ÉCHEC — fuite détectée.'}**")

    lines.append("")
    lines.append("## 3. Recalcul indépendant de la moyenne à 3 (boucle Python explicite)")
    lines.append("")
    d1 = np.load(ROOT / "results" / "nonml_defensive_calmar_vol_targeting_overlay_pnl.npz", allow_pickle=True)
    d2 = np.load(ROOT / "results" / "nonml_etape_d_garch_defensive_overlay_pnl.npz", allow_pickle=True)
    d_ewma = np.load(ROOT / "results" / "nonml_ewma_defensive_overlay_pnl.npz", allow_pickle=True)
    d3 = np.load(ROOT / "results" / "nonml_ewma_defensive_overlay_and_triple_engine_pnl.npz", allow_pickle=True)
    dates1 = pd.to_datetime(d1["dates"])
    dates2 = pd.to_datetime(d2["dates"])
    dates_ewma = pd.to_datetime(d_ewma["dates"])
    dates3 = pd.to_datetime(d3["dates"])
    s_pos1 = pd.Series(d1["pos"], index=dates1)
    s_pos2 = pd.Series(d2["pos"], index=dates2)
    s_pos_ewma = pd.Series(d_ewma["pos"], index=dates_ewma)
    pos_triple_orig = d3["pos"]
    ok3 = True
    n_checked3 = 0
    for k in range(0, len(dates3), 1500):
        d = dates3[k]
        p1 = float(s_pos1.get(d, np.nan))
        p2 = float(s_pos2.get(d, np.nan))
        p3_ewma = float(s_pos_ewma.get(d, np.nan))
        if not (np.isfinite(p1) and np.isfinite(p2) and np.isfinite(p3_ewma)):
            continue
        manual_avg = (p1 + p2 + p3_ewma) / 3.0
        diff = abs(manual_avg - float(pos_triple_orig[k]))
        ok3 &= (diff < 1e-9)
        n_checked3 += 1
    lines.append(f"**{'OK — moyenne à 3 confirmée par recalcul indépendant (' + str(n_checked3) + ' dates, à partir des 3 npz sources séparées).' if (ok3 and n_checked3 > 0) else 'ÉCHEC ou aucune date vérifiable.'}**")

    out = ROOT / "results" / "nonml_ewma_defensive_overlay_and_triple_engine_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
