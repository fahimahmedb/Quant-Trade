"""Backtest — Overlay défensif sur "faux breakout" de Donchian
(spécification pré-enregistrée dans PREREG_failed_breakout_overlay.md,
committée avant ce script). Variante INVERSE du #40 (continuation, FAIL) :
réduit l'exposition au lieu de l'amplifier. n_trials=1, aucune
dépendance ML. Règle de succès renforcée.
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
FLOOR = 0.5
DONCHIAN_WINDOW = 20
CONFIRM_WINDOW = 2
DEFENSE_LEN = 5

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def failed_breakout_position(close: np.ndarray) -> np.ndarray:
    """Renvoie la position pour chaque jour t (appliquee au rendement
    r(t) = close(t+1)/close(t)) : FLOOR pendant DEFENSE_LEN jours apres
    confirmation d'un faux breakout, 1.0x sinon. Decision au jour t basee
    uniquement sur close[0..t] (causal)."""
    T = len(close)
    donchian_max = pd.Series(close).rolling(DONCHIAN_WINDOW).max().values

    pos = np.ones(T)
    breakout_day = None
    breakout_level = None
    defensive_countdown = 0

    for t in range(DONCHIAN_WINDOW, T):
        if not np.isnan(donchian_max[t]) and close[t] >= donchian_max[t]:
            breakout_day = t
            breakout_level = donchian_max[t]

        if breakout_day is not None and 1 <= (t - breakout_day) <= CONFIRM_WINDOW:
            if close[t] < breakout_level:
                defensive_countdown = DEFENSE_LEN  # (re)lance la fenetre defensive
                breakout_day = None  # consomme ce breakout, evite un re-declenchement sur le meme

        pos[t] = FLOOR if defensive_countdown > 0 else 1.0
        if defensive_countdown > 0:
            defensive_countdown -= 1

    return pos


def main():
    lines = [
        "# Résultat — Overlay défensif sur faux breakout Donchian (pré-enregistré, règle renforcée)",
        "",
        f"Breakout = clôture ≥ plus haut glissant {DONCHIAN_WINDOW}j. Faux breakout confirmé si "
        f"clôture retombe sous ce niveau dans les {CONFIRM_WINDOW}j suivants → position = "
        f"FLOOR={FLOOR}x pendant {DEFENSE_LEN}j (relance si nouveau faux breakout), 1.0x sinon.",
        "",
        "| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j défensif | Sharpe>BH | Rdt>BH |",
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

        pos_full = failed_breakout_position(close)
        pos = pos_full[:-1]  # aligne sur bh_full (longueur T-1)

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
            f"| {name} | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% | "
            f"{me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | {me_ov['max_drawdown_pct']:.1f}% | "
            f"{100*(pos < 1.0).mean():.1f}% | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_failed_breakout_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
