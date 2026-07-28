"""Backtest — Overlay levé sur pullback court terme au niveau indice
(spécification pré-enregistrée dans PREREG_short_pullback_rebound.md,
committée avant ce script). n_trials=1, aucune dépendance ML. Règle de
succès renforcée.
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
CAP = 2.0
PB_WINDOW = 3
PB_THRESHOLD = -0.03
REBOUND_LEN = 5

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def rebound_exposure(close: np.ndarray) -> np.ndarray:
    T = len(close)
    pullback_ret = np.full(T, np.nan)
    for i in range(PB_WINDOW, T):
        pullback_ret[i] = np.log(close[i] / close[i - PB_WINDOW])
    trigger = np.nan_to_num(pullback_ret, nan=0.0) <= PB_THRESHOLD

    pos = np.ones(T)
    remaining = 0
    for t in range(T):
        if trigger[t]:
            remaining = REBOUND_LEN  # (re)lance la fenetre de rebond
        if remaining > 0:
            pos[t] = CAP
            remaining -= 1
    return pos


def main():
    lines = [
        "# Résultat — Overlay levé sur pullback court terme, niveau indice (pré-enregistré, règle renforcée)",
        "",
        f"Repli = rendement log sur {PB_WINDOW}j ≤ {100*PB_THRESHOLD:.0f}% -> CAP={CAP}x pendant "
        f"{REBOUND_LEN}j suivants (relance si nouveau repli pendant la fenêtre), 1.0x sinon.",
        "",
        "| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j levé | Sharpe>BH | Rdt>BH |",
        "|---|---|---|---|---|---|---|---|---|---|",
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

        pos_full = rebound_exposure(close)
        pos = pos_full[1:]  # position decidee a t (close), appliquee au rendement t->t+1
        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl_ov = pos * bh_full - turn * (COST_BPS / 1e4)
        pnl_bh = bh_full.copy()
        pnl_bh[0] -= COST_BPS / 1e4

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
            f"{100*(pos > 1.0).mean():.1f}% | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_short_pullback_rebound_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
