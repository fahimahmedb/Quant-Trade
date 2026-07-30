"""Re-lecture Sortino de la stabilité temporelle et du stress de crise
du #121 (cycle #129, pré-enregistré dans
PREREG_sortino_reanalysis_dual_engine.md). PAS un nouveau backtest --
recalcule les mêmes folds/fenêtres de la Règle 9 avec Sortino au lieu
de Sharpe, sur le pnl déjà committé.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from prediction import trading_metrics  # noqa: E402

COST_BPS = 5.0
EMBARGO = 5
CRISIS_WINDOWS = [
    ("Dot-com crash", "2000-01-01", "2002-12-31"),
    ("Crise financière 2008", "2007-10-01", "2009-03-31"),
    ("Krach COVID", "2020-02-01", "2020-04-30"),
    ("Resserrement 2022", "2022-01-01", "2022-12-31"),
]


def pnl_at(pos, r):
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r - turn * (COST_BPS / 1e4)
    pnl_bh = r.copy()
    pnl_bh[0] -= COST_BPS / 1e4
    return pnl_ov, pnl_bh


def main():
    d = np.load(ROOT / "results" / "nonml_dual_engine_defensive_overlay_pnl.npz", allow_pickle=True)
    pos, r, cost_bps = d["pos"], d["r_asset"], float(d["cost_bps"])
    dates = pd.to_datetime(d["dates"])
    T = len(r)

    lines = ["# Re-lecture Sortino — stabilité temporelle et stress de crise du #121", "",
             "PAS un nouveau backtest -- même pnl déjà committé, même découpage Règle 9, "
             "métrique de lecture Sortino au lieu de Sharpe.", "",
             "## 1. Stabilité temporelle (4 folds, embargo 5j) -- Sharpe vs Sortino", "",
             "| Fold | Séances | Sharpe overlay | Sharpe BH | Bat BH (Sharpe) | Sortino overlay | Sortino BH | Bat BH (Sortino) |",
             "|---|---|---|---|---|---|---|---|"]

    n_folds = 4
    fold_len = T // n_folds
    n_beat_sharpe, n_beat_sortino = 0, 0
    n_scored = 0
    for k in range(n_folds):
        f0 = k * fold_len
        f1 = (k + 1) * fold_len if k < n_folds - 1 else T
        if k > 0:
            f0 += EMBARGO
        pos_f, r_f = pos[f0:f1], r[f0:f1]
        pnl_ov, pnl_bh = pnl_at(pos_f, r_f)
        me_ov, me_bh = trading_metrics(pnl_ov), trading_metrics(pnl_bh)
        beat_sharpe = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
        sortino_ov = me_ov["sortino_ann"] if np.isfinite(me_ov["sortino_ann"]) else -np.inf
        sortino_bh = me_bh["sortino_ann"] if np.isfinite(me_bh["sortino_ann"]) else -np.inf
        beat_sortino = sortino_ov > sortino_bh
        n_beat_sharpe += int(beat_sharpe)
        n_beat_sortino += int(beat_sortino)
        n_scored += 1
        lines.append(
            f"| {k+1} | {f1-f0} | {me_ov['sharpe_ann']:+.2f} | {me_bh['sharpe_ann']:+.2f} | "
            f"{'OUI' if beat_sharpe else 'non'} | {sortino_ov:+.2f} | {sortino_bh:+.2f} | "
            f"{'OUI' if beat_sortino else 'non'} |"
        )

    lines.append("")
    lines.append(f"Folds favorables sous Sharpe : {n_beat_sharpe}/{n_scored}. Sous Sortino : {n_beat_sortino}/{n_scored}.")
    lines.append("")

    lines.append("## 2. Fenêtres de crise -- MDD (officiel) vs Sortino (complémentaire)")
    lines.append("")
    lines.append("| Fenêtre | Séances | MDD overlay | MDD BH | Sortino overlay | Sortino BH | Sortino overlay>BH |")
    lines.append("|---|---|---|---|---|---|---|")
    n_sortino_crisis_ok = 0
    n_scored_crisis = 0
    for label, d0, d1 in CRISIS_WINDOWS:
        mask = (dates >= pd.Timestamp(d0)) & (dates <= pd.Timestamp(d1))
        n = int(mask.sum())
        if n < 20:
            lines.append(f"| {label} | {n} | -- | -- | -- | -- | hors couverture |")
            continue
        pos_w, r_w = pos[mask], r[mask]
        pnl_ov, pnl_bh = pnl_at(pos_w, r_w)
        me_ov, me_bh = trading_metrics(pnl_ov), trading_metrics(pnl_bh)
        sortino_ov = me_ov["sortino_ann"] if np.isfinite(me_ov["sortino_ann"]) else -np.inf
        sortino_bh = me_bh["sortino_ann"] if np.isfinite(me_bh["sortino_ann"]) else -np.inf
        ok = sortino_ov > sortino_bh
        n_sortino_crisis_ok += int(ok)
        n_scored_crisis += 1
        lines.append(
            f"| {label} | {n} | {me_ov['max_drawdown_pct']:.1f}% | {me_bh['max_drawdown_pct']:.1f}% | "
            f"{sortino_ov:+.2f} | {sortino_bh:+.2f} | {'OUI' if ok else 'non'} |"
        )
    lines.append("")
    lines.append(f"Fenêtres de crise favorables sous Sortino : {n_sortino_crisis_ok}/{n_scored_crisis}.")
    lines.append("")

    lines.append("## Conclusion")
    lines.append("")
    lines.append(
        f"Sous Sharpe (Règle 9c officielle) : {n_beat_sharpe}/{n_scored} folds favorables. Sous Sortino "
        f"(lecture complémentaire) : {n_beat_sortino}/{n_scored}. "
        + ("Le Sortino ne change PAS qualitativement la lecture -- la stabilité temporelle reste "
           "similaire sous les deux métriques." if n_beat_sortino == n_beat_sharpe else
           f"Le Sortino {'améliore' if n_beat_sortino > n_beat_sharpe else 'dégrade'} la lecture de "
           f"stabilité par rapport au Sharpe -- cohérent avec le profil de couverture (le mécanisme "
           f"pénalise moins la volatilité totale que la volatilité à la baisse). Ne change PAS le "
           f"verdict Règle 9 officiel (basé sur Sharpe/MDD/SPA/DSR, déjà tranché FAIL) -- une lecture "
           f"alternative documentée, pas un nouveau critère de succès adopté rétroactivement.")
    )

    out = ROOT / "results" / "nonml_sortino_reanalysis_dual_engine.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
