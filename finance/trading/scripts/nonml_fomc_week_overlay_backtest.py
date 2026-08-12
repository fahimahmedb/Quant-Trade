"""Backtest — Semaine FOMC entière (J-2 à J+2), overlay levé (spécification
pré-enregistrée dans PREREG_fomc_week_overlay.md, committée avant ce
script). n_trials=1, aucune dépendance ML. Règle de succès renforcée sur
5 marchés (≥4/5).

Réutilise `FOMC_DATES` du #171 (`nonml_pre_fomc_drift_overlay_backtest.py`)
-- aucune redéfinition de la liste, Règle 7. Implémentation autonome du
masque (pas de réutilisation de pre_fomc_mask/post_fomc_mask, pour éviter
toute ambiguïté d'offset -- voir PREREG §3 pour la dérivation).
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
from prediction import trading_metrics  # noqa: E402
from nonml_pre_fomc_drift_overlay_backtest import FOMC_DATES, MARKETS  # noqa: E402

COST_BPS = 5.0
CAP = 2.0


def fomc_week_mask(dates: pd.DatetimeIndex) -> np.ndarray:
    """True aux indices k = ann_idx-3 .. ann_idx+1 (5 valeurs), pour capter
    les rendements REALISES sur les 5 seances J-2..J+2 autour de chaque
    annonce (voir PREREG §3 pour la derivation de l'offset)."""
    dates_arr = dates.values
    T = len(dates)
    mask = np.zeros(T, dtype=bool)
    for fomc_date in FOMC_DATES.values:
        ann_idx = np.searchsorted(dates_arr, fomc_date)
        if ann_idx >= T:
            continue
        for k in range(ann_idx - 3, ann_idx + 2):
            if 0 <= k < T:
                mask[k] = True
    return mask


def main():
    lines = [
        "# Résultat — Semaine FOMC entière (pré-enregistré, incertitude générale J-2 à J+2)",
        "",
        f"Position(t) = {CAP}x sur les 5 séances J-2 à J+2 entourant chaque annonce FOMC "
        f"(95 dates, réutilisées du #171), 1.0x sinon. Coûts {COST_BPS:.0f} bps.",
        "",
        "| Marché | Séances test. | Jours semaine-FOMC | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    n_markets, n_success = 0, 0

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        dates = pd.DatetimeIndex(df["date"].values)
        bh_full = np.log(close[1:] / close[:-1])

        week_mask_full = fomc_week_mask(dates)
        week_mask_r = week_mask_full[:-1]

        n_week = int(week_mask_r.sum())
        pos = np.where(week_mask_r, CAP, 1.0)

        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl_ov = pos * bh_full - turn * (COST_BPS / 1e4)
        pnl_bh = bh_full.copy()
        pnl_bh[0] -= COST_BPS / 1e4

        me_bh = trading_metrics(pnl_bh)
        me_ov = trading_metrics(pnl_ov)
        ret_bh = np.exp(pnl_bh.sum()) - 1.0
        ret_ov = np.exp(pnl_ov.sum()) - 1.0

        sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
        ret_ok = ret_ov > ret_bh
        n_markets += 1
        n_success += int(sharpe_ok and ret_ok)

        lines.append(
            f"| {name} | {len(bh_full)} | {n_week} | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | "
            f"{me_bh['max_drawdown_pct']:.1f}% | {me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | "
            f"{me_ov['max_drawdown_pct']:.1f}% | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_fomc_week_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
