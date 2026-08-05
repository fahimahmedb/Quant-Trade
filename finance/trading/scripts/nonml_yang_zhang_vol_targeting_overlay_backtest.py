"""Backtest — Overlay de vol-targeting avec estimateur Yang-Zhang (2000)
(spécification pré-enregistrée dans
PREREG_yang_zhang_vol_targeting_overlay.md, committée avant ce script).
Combine variance overnight, ouverture->cloture et Rogers-Satchell
intra-seance ; estimateur range-based le plus complet de la lignee
#46/#50/#215/#221. n_trials=1, aucune dependance ML. Regle de succes
renforcee.
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


def yang_zhang_vol_ann_lagged(df) -> np.ndarray:
    """Renvoie la vol annualisee Yang-Zhang, alignee sur les rendements
    r = log(close[1:]/close[:-1]) (longueur T-1). vol_ann_lagged[i]
    (indice de r) est calculee sur les barres [i-VOL_WINDOW+1, i] du
    DataFrame -- ne depend que de donnees connues a la cloture du jour i,
    deja causale par construction (pas de decalage supplementaire
    necessaire, contrairement aux #46/#50/#215/#221)."""
    open_ = df["open"].values
    high = df["high"].values
    low = df["low"].values
    close = df["close"].values
    T = len(close)
    n = VOL_WINDOW
    k = 0.34 / (1.34 + (n + 1) / (n - 1))

    o = np.full(T, np.nan)
    c = np.full(T, np.nan)
    rs = np.full(T, np.nan)
    o[1:] = np.log(open_[1:] / close[:-1])
    c[1:] = np.log(close[1:] / open_[1:])
    hc = np.log(high[1:] / close[1:])
    ho = np.log(high[1:] / open_[1:])
    lc = np.log(low[1:] / close[1:])
    lo = np.log(low[1:] / open_[1:])
    rs[1:] = hc * ho + lc * lo

    vol_ann_lagged = np.full(T - 1, np.nan)  # aligne sur r, longueur T-1
    for i in range(n, T - 1):
        window_o = o[i - n + 1:i + 1]
        window_c = c[i - n + 1:i + 1]
        window_rs = rs[i - n + 1:i + 1]
        if np.any(np.isnan(window_o)):
            continue
        var_o = window_o.var(ddof=1)
        var_c = window_c.var(ddof=1)
        var_rs = window_rs.mean()
        var_yz = max(var_o + k * var_c + (1 - k) * var_rs, 0.0)
        vol_ann_lagged[i] = np.sqrt(var_yz) * ANNUALIZATION
    return vol_ann_lagged


def yang_zhang_vol_position(df) -> np.ndarray:
    """Renvoie la position continue clip(vol_cible / vol_yz(t), 0, CAP),
    alignee sur les rendements clot-a-clot r = log(close[1:]/close[:-1])."""
    vol_lagged = yang_zhang_vol_ann_lagged(df)
    with np.errstate(divide="ignore", invalid="ignore"):
        pos = TARGET_VOL_ANNUAL / vol_lagged
    pos = np.clip(pos, 0.0, CAP)
    pos = np.nan_to_num(pos, nan=1.0)
    return pos


def main():
    lines = [
        "# Résultat — Overlay de vol-targeting estimateur Yang-Zhang (pré-enregistré, règle renforcée)",
        "",
        f"Position(t) = clip({TARGET_VOL_ANNUAL:.0%} / vol_YangZhang_{VOL_WINDOW}j(t), 0.0, {CAP}x) "
        f"— variante du #46/#50/#215/#221 combinant overnight + ouverture→clôture + Rogers-Satchell. "
        f"Échantillon testable = à partir de la {VOL_WINDOW+2}e séance.",
        "",
        "| Marché | Séances test. | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Position moy. | Sharpe>BH | Rdt>BH |",
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
        bh_full = np.log(close[1:] / close[:-1])  # longueur T-1

        pos_full = yang_zhang_vol_position(df)  # longueur T-1, aligne sur bh_full
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

        lines.append(
            f"| {name} | {len(bh_t)} | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% | "
            f"{me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | {me_ov['max_drawdown_pct']:.1f}% | "
            f"{pos.mean():.2f}x | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

        if name == "NDX (40 ans)":
            dates_pnl = dates.values[1:][start:]
            np.savez(ROOT / "results" / "nonml_yang_zhang_vol_targeting_overlay_pnl.npz",
                     pos=pos, r_asset=bh_t, dates=dates_pnl, cost_bps=COST_BPS)

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_yang_zhang_vol_targeting_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
