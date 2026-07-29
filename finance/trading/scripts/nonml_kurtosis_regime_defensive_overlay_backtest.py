"""Backtest — Overlay DÉFENSIF gaté par la kurtosis de l'indice
(spécification pré-enregistrée dans
PREREG_kurtosis_regime_defensive_overlay.md, committée avant ce
script). n_trials=1, aucune dépendance ML. Règle de succès renforcée.
Adapté du mécanisme #92 (skewness) avec la kurtosis comme estimateur et
une réponse DÉFENSIVE (réduction, jamais amplification), esprit du #44.
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
KURT_WINDOW = 60
WARMUP = 252
CUT = 0.5

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def high_kurtosis_regime_mask(r: np.ndarray) -> np.ndarray:
    """r = rendements quotidiens (log). Renvoie un masque booleen :
    True si le jour t est en regime de kurtosis ELEVEE (kurtosis
    roulante KURT_WINDOW a t-1 dans le tercile SUPERIEUR causal,
    calcule sur l'historique jusqu'a t-1)."""
    T = len(r)
    kurt = pd.Series(r).rolling(KURT_WINDOW).kurt().values
    mask = np.zeros(T, dtype=bool)
    for t in range(WARMUP, T):
        kurt_at_decision = kurt[t - 1]
        if not np.isfinite(kurt_at_decision):
            continue
        past_kurt = kurt[KURT_WINDOW:t]
        past_kurt = past_kurt[np.isfinite(past_kurt)]
        if len(past_kurt) < 30:
            continue
        q_hi = np.percentile(past_kurt, 200 / 3)  # tercile superieur (kurtosis la plus elevee)
        mask[t] = kurt_at_decision >= q_hi
    return mask


def main():
    lines = [
        "# Résultat — Overlay défensif gaté par la kurtosis de l'indice (pré-enregistré, règle renforcée)",
        "",
        f"Position 1.0x en permanence, CUT={CUT}x (réduction, jamais amplification) les jours en régime "
        f"de kurtosis ÉLEVÉE (kurtosis roulante {KURT_WINDOW}j, tercile supérieur causal expansif).",
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
        close = df["close"].values
        bh_full = np.log(close[1:] / close[:-1])
        T = len(bh_full)
        if T <= WARMUP + 30:
            continue

        mask = high_kurtosis_regime_mask(bh_full)
        idx = np.arange(WARMUP, T)

        pos = np.where(mask, CUT, 1.0)
        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl_ov_full = pos * bh_full - turn * (COST_BPS / 1e4)
        pnl_bh_full = bh_full.copy()
        pnl_bh_full[0] -= COST_BPS / 1e4

        pnl_ov, pnl_bh = pnl_ov_full[idx], pnl_bh_full[idx]

        me_bh = trading_metrics(pnl_bh)
        me_ov = trading_metrics(pnl_ov)
        ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
        ret_ov = np.cumprod(1.0 + pnl_ov)[-1] - 1.0

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

    out = ROOT / "results" / "nonml_kurtosis_regime_defensive_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
