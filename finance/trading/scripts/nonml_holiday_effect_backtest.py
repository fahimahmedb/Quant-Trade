"""Backtest — Effet pré/post jour férié (spécification pré-enregistrée
dans PREREG_holiday_effect.md, committée avant ce script). Détection des
jours fériés DATA-DRIVEN (trou anormal dans le calendrier de séances),
pas de calendrier codé en dur. n_trials=1, aucune dépendance ML. Règle de
succès renforcée.
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

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def holiday_masks(dates: pd.Series):
    """Renvoie (pre_mask, post_mask) : detection data-driven des jours
    feries via un trou calendaire anormal entre deux seances consecutives."""
    d = pd.to_datetime(dates).reset_index(drop=True)
    n = len(d)
    gap_days = (d.shift(-1) - d).dt.days  # gap[i] = jours calendaires entre seance i et i+1
    dow = d.dt.dayofweek  # 0=lundi ... 4=vendredi
    normal_gap = np.where(dow == 4, 3, 1)  # vendredi -> lundi = 3j normal, sinon 1j normal
    is_pre = (gap_days.values > normal_gap) & np.isfinite(gap_days.values)
    is_post = np.zeros(n, dtype=bool)
    is_post[1:] = is_pre[:-1]
    return is_pre, is_post


def main():
    lines = [
        "# Résultat — Effet pré/post jour férié (pré-enregistré, règle renforcée)",
        "",
        "Détection data-driven (trou calendaire anormal), pas de calendrier codé en dur.",
        "",
        "| Marché | BH Sharpe | BH Rdt total | Holiday Sharpe | Holiday Rdt total | % jours investis | Sharpe>BH | Rdt>BH |",
        "|---|---|---|---|---|---|---|---|",
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

        is_pre, is_post = holiday_masks(df["date"])
        mask = is_pre | is_post
        mask_r = mask[1:]  # rendement du jour t "active" si le jour t est pre OU post ferie

        pos = mask_r.astype(float)
        turn = np.abs(np.diff(pos, prepend=0.0))
        pnl_hol = pos * bh_full - turn * (COST_BPS / 1e4)
        pnl_bh = bh_full.copy()
        pnl_bh[0] -= COST_BPS / 1e4

        me_bh = trading_metrics(pnl_bh)
        me_hol = trading_metrics(pnl_hol)
        ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
        ret_hol = np.cumprod(1.0 + pnl_hol)[-1] - 1.0

        sharpe_ok = me_hol["sharpe_ann"] > me_bh["sharpe_ann"]
        ret_ok = ret_hol > ret_bh
        n_markets += 1
        n_success += int(sharpe_ok and ret_ok)

        lines.append(
            f"| {name} | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | "
            f"{me_hol['sharpe_ann']:+.2f} | {100*ret_hol:+.1f}% | {100*mask_r.mean():.1f}% | "
            f"{'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où Holiday-only bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_holiday_effect_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
