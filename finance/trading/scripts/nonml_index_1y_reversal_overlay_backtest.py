"""Backtest — Renversement 1 an au niveau INDICE, overlay levé
(spécification pré-enregistrée dans PREREG_index_1y_reversal_overlay.md,
committée avant ce script). n_trials=1, aucune dépendance ML. Règle de
succès renforcée, marché unique (NDX). Même structure que le #177
(LOOKBACK différent), Règle 7.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402

COST_BPS = 5.0
LOOKBACK = 252          # 1 an de bourse
TERCILE_PCT = 100.0 / 3.0
BURN_IN = 252
CAP = 2.0
FLOOR = 1.0
MARKET_NAME = "NDX (40 ans)"
MARKET_FILE = "nasdaq100_daily.txt"


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / MARKET_FILE))
    quality_report(df)
    close = df["close"].values
    T = len(close)
    bh_full = np.log(close[1:] / close[:-1])

    signal = np.full(T, np.nan)
    for t in range(LOOKBACK + 1, T):
        signal[t] = close[t - 1] / close[t - 1 - LOOKBACK] - 1.0

    start = LOOKBACK + 1 + BURN_IN
    pos_full = np.full(T, np.nan)
    for t in range(start, T):
        hist = signal[LOOKBACK + 1:t + 1]
        thresh = np.percentile(hist, TERCILE_PCT)
        pos_full[t] = CAP if signal[t] <= thresh else FLOOR

    pos = pos_full[start:-1]
    bh_t = bh_full[start:]
    assert len(pos) == len(bh_t)
    assert np.isfinite(pos).all()

    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * bh_t - turn * (COST_BPS / 1e4)
    pnl_bh = bh_t.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    me_bh = trading_metrics(pnl_bh)
    me_ov = trading_metrics(pnl_ov)
    ret_bh = float(np.exp(pnl_bh.sum()) - 1.0)
    ret_ov = float(np.exp(pnl_ov.sum()) - 1.0)

    sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_ov > ret_bh
    verdict = bool(sharpe_ok and ret_ok)

    frac_cap = float((pos > FLOOR).mean())

    lines = [
        "# Résultat — Renversement 1 an au niveau indice (pré-enregistré, complète le #177)",
        "",
        f"Marché : **{MARKET_NAME}** uniquement. "
        f"`position(t) = {CAP}x` si `retour_1an(t) ≤ percentile_{TERCILE_PCT:.2f}_expanding`, "
        f"`{FLOOR}x` sinon. LOOKBACK={LOOKBACK}j, BURN_IN={BURN_IN}j, coûts {COST_BPS:.0f} bps.",
        "",
        f"- Séances testées : {len(bh_t)}.",
        f"- Part du temps en régime de renversement (2.0x) : **{100*frac_cap:.1f}%**.",
        "",
        "| | Sharpe ann. | Rendement total | MDD |",
        "|---|---|---|---|",
        f"| Buy & Hold | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Overlay renversement 1 an** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100*ret_ov:+.1f}%** | {me_ov['max_drawdown_pct']:.1f}% |",
        "",
        f"- Sharpe overlay > BH : {'OUI' if sharpe_ok else 'NON'}",
        f"- Rendement overlay > BH : {'OUI' if ret_ok else 'NON'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_index_1y_reversal_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
