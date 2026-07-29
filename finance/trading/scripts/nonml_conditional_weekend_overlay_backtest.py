"""Backtest — Effet week-end CONDITIONNEL (lundi | signe du vendredi
précédent) (spécification pré-enregistrée dans
PREREG_conditional_weekend_overlay.md, committée avant ce script).
n_trials=1, aucune dépendance ML. Règle de succès renforcée.
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
CAP = 2.0

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def conditional_monday_mask(dates: pd.Series, close: np.ndarray) -> np.ndarray:
    """Renvoie un masque booleen (longueur T, aligne sur close) : True
    les seances de LUNDI dont la seance de VENDREDI la plus recente qui
    la precede a un rendement STRICTEMENT POSITIF. Detection data-driven
    du jour de la semaine, recherche arriere robuste aux jours feries."""
    weekdays = pd.to_datetime(dates).dt.weekday.values  # 0=lundi, 4=vendredi
    T = len(close)
    mask = np.zeros(T, dtype=bool)
    last_friday_idx = -1
    last_friday_ret = np.nan
    for t in range(1, T):
        if weekdays[t] == 4:  # vendredi : enregistre son propre rendement pour un usage futur
            last_friday_idx = t
            last_friday_ret = close[t] / close[t - 1] - 1.0
        if weekdays[t] == 0 and last_friday_idx >= 0:  # lundi
            mask[t] = last_friday_ret > 0.0
    return mask


def main():
    lines = [
        "# Résultat — Effet week-end conditionnel lundi|vendredi (pré-enregistré, règle renforcée)",
        "",
        f"Position 1.0x en permanence, CAP={CAP}x UNIQUEMENT les séances de lundi dont le vendredi "
        f"précédent a un rendement strictement positif.",
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
        dates = df["date"]
        mask_full = conditional_monday_mask(dates, close)

        bh_full = np.log(close[1:] / close[:-1])
        mask = mask_full[1:]

        pos = np.where(mask, CAP, 1.0)
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
            f"{100*mask.mean():.1f}% | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_conditional_weekend_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
