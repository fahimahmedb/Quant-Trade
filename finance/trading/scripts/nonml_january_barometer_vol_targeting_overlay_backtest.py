"""Backtest — Overlay vol-targeting gaté par le January Barometer
(spécification pré-enregistrée dans
PREREG_january_barometer_vol_targeting_overlay.md, committée avant ce
script). Combine les cycles #59 (porte annuelle) et #46/#47 (mécanisme
vol-targeting). n_trials=1, aucune dépendance ML. Règle de succès
renforcée.
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
VOL_WINDOW = 20
TARGET_VOL_ANNUAL = 0.20
ANNUALIZATION = np.sqrt(252)

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def january_gate_mask(df) -> np.ndarray:
    """Renvoie un masque booleen (longueur T, alignee sur close) : True
    de fevrier a decembre de l'annee Y si le rendement de janvier(Y)
    (dec(Y-1)->jan(Y)) est positif, False sinon (et toujours False en
    janvier, identique au #59)."""
    dates = pd.to_datetime(df["date"])
    close = df["close"].values
    years = dates.dt.year.values
    months = dates.dt.month.values
    T = len(close)

    last_idx_of_month = {}
    for i in range(T):
        last_idx_of_month[(years[i], months[i])] = i

    all_years = sorted(set(years))
    jan_return_positive = {}
    for y in all_years:
        dec_prev_idx = last_idx_of_month.get((y - 1, 12))
        jan_idx = last_idx_of_month.get((y, 1))
        if dec_prev_idx is None or jan_idx is None:
            continue
        jan_ret = close[jan_idx] / close[dec_prev_idx] - 1.0
        jan_return_positive[y] = jan_ret > 0

    gate = np.zeros(T, dtype=bool)
    for i in range(T):
        y = years[i]
        if months[i] == 1:
            continue
        gate[i] = jan_return_positive.get(y, False)

    return gate


def combined_position(close: np.ndarray, r: np.ndarray, gate: np.ndarray) -> np.ndarray:
    """r = rendements log quotidiens (longueur T-1). gate = porte annuelle
    alignee sur close (longueur T). Renvoie la position pour chaque
    rendement de r."""
    gate_r = gate[:-1]  # meme convention causale que les autres portes hierarchiques

    vol_ann = pd.Series(r).rolling(VOL_WINDOW).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        vt_exposure = TARGET_VOL_ANNUAL / vol_lagged
    vt_exposure = np.clip(vt_exposure, 1.0, CAP)
    vt_exposure = np.nan_to_num(vt_exposure, nan=1.0)

    pos = np.where(gate_r, vt_exposure, 1.0)
    pos = np.nan_to_num(pos, nan=1.0)
    return pos


def main():
    lines = [
        "# Résultat — Overlay vol-targeting gaté par le January Barometer (pré-enregistré, combinaison #59+#46)",
        "",
        f"Position(t) = clip({TARGET_VOL_ANNUAL:.0%} / vol_réalisée_{VOL_WINDOW}j(t-1), 1.0, {CAP}x) "
        "de février à décembre de l'année Y si le rendement de janvier(Y) est positif, sinon 1.0x "
        "(toujours 1.0x en janvier).",
        "",
        "| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte active | Position moy. | Sharpe>BH | Rdt>BH |",
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
        bh_full = np.log(close[1:] / close[:-1])

        gate = january_gate_mask(df)
        pos_full = combined_position(close, bh_full, gate)
        start = VOL_WINDOW
        bh_t = bh_full[start:]
        pos = pos_full[start:]

        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl_ov = pos * bh_t - turn * (COST_BPS / 1e4)
        pnl_bh = bh_t.copy()
        pnl_bh[0] -= COST_BPS / 1e4

        me_bh = trading_metrics(pnl_bh)
        me_ov = trading_metrics(pnl_ov)
        ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
        ret_ov = np.cumprod(1.0 + pnl_ov)[-1] - 1.0

        sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
        ret_ok = ret_ov > ret_bh
        n_markets += 1
        n_success += int(sharpe_ok and ret_ok)

        gate_active = (pos > 1.0)
        lines.append(
            f"| {name} | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% | "
            f"{me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | {me_ov['max_drawdown_pct']:.1f}% | "
            f"{100*gate_active.mean():.1f}% | {pos.mean():.2f}x | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_january_barometer_vol_targeting_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
