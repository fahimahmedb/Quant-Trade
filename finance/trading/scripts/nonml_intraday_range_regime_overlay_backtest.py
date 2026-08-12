"""Backtest — Overlay de régime par le RANGE intra-séance (high-low)/close
(spécification pré-enregistrée dans PREREG_intraday_range_regime_overlay.md,
committée avant ce script). n_trials=1, aucune dépendance ML. Règle de
succès renforcée. Adapté du mécanisme #9 (régime calme, close-to-close)
avec un estimateur intra-séance à la place.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402

COST_BPS = 5.0
RANGE_WINDOW = 20
WARMUP = 252
CAP = 2.0

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def calm_range_regime_mask(high: np.ndarray, low: np.ndarray, close: np.ndarray) -> np.ndarray:
    """Renvoie un masque booleen : True si le jour t est en regime
    calme (range intra-seance moyen roulant a t-1 dans le tercile
    inferieur CAUSAL, calcule sur l'historique jusqu'a t-1)."""
    T = len(close)
    daily_range = (high - low) / close
    range_ma = pd.Series(daily_range).rolling(RANGE_WINDOW).mean().values  # range_ma[t] utilise daily_range[t-19:t+1]
    mask = np.zeros(T, dtype=bool)
    for t in range(WARMUP, T):
        range_at_decision = range_ma[t - 1]  # connu a la cloture de t-1, decide la position de t
        if not np.isfinite(range_at_decision):
            continue
        past_range = range_ma[RANGE_WINDOW:t]
        past_range = past_range[np.isfinite(past_range)]
        if len(past_range) < 30:
            continue
        q_lo = np.percentile(past_range, 100 / 3)
        mask[t] = range_at_decision <= q_lo
    return mask


def main():
    lines = [
        "# Résultat — Overlay de régime par le range intra-séance (pré-enregistré, règle renforcée)",
        "",
        f"Position 1.0x en permanence, CAP={CAP}x les jours en régime calme "
        f"(range intra-séance moyen roulant {RANGE_WINDOW}j, tercile inférieur causal expansif).",
        "",
        "| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    n_markets, n_success = 0, 0

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        high = df["high"].values
        low = df["low"].values
        close = df["close"].values
        bh_full = np.log(close[1:] / close[:-1])
        T = len(bh_full)
        if T <= WARMUP + 30:
            continue

        mask_full = calm_range_regime_mask(high, low, close)
        mask = mask_full[1:]  # aligner avec bh_full (rendement de t => signal connu a t-1, indices decales de 1)
        idx = np.arange(WARMUP, T)

        pos = np.where(mask, CAP, 1.0)
        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl_ov_full = pos * bh_full - turn * (COST_BPS / 1e4)
        pnl_bh_full = bh_full.copy()
        pnl_bh_full[0] -= COST_BPS / 1e4

        pnl_ov, pnl_bh = pnl_ov_full[idx], pnl_bh_full[idx]

        me_bh = trading_metrics(pnl_bh)
        me_ov = trading_metrics(pnl_ov)
        ret_bh = np.exp(pnl_bh.sum()) - 1.0
        ret_ov = np.exp(pnl_ov.sum()) - 1.0

        sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
        ret_ok = ret_ov > ret_bh
        n_markets += 1
        n_success += int(sharpe_ok and ret_ok)

        lines.append(
            f"| {name} | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% | "
            f"{me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | {me_ov['max_drawdown_pct']:.1f}% | "
            f"{'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")
    lines.append("")
    lines.append("**Rappel du risque assumé** : levier ajouté en période calme -- une bascule "
                 "brutale calme->agité en fin de fenêtre de levier pourrait amplifier une perte, "
                 "signalé via le MDD ci-dessus.")

    out = ROOT / "results" / "nonml_intraday_range_regime_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
