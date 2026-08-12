"""Backtest — Overlay avance-retard cross-marché DAX->marchés US
(spécification pré-enregistrée dans PREREG_dax_ndx_leadlag_overlay.md,
committée avant ce script). Alignement causal ffill+shift(1) réutilisé
des #175/#178/#186/#187/#191/#192/#193 (Règle 7). n_trials=1, aucune
dépendance ML. Règle de succès renforcée adaptée à 4 marchés (>=3/4).
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

TARGET_MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
}


def dax_ret_series() -> pd.Series:
    df = load_ohlc(str(REPO_ROOT / "data" / "dax_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates = pd.DatetimeIndex(df["date"].values)
    r = np.full(len(close), np.nan)
    r[1:] = np.log(close[1:] / close[:-1])
    return pd.Series(r, index=dates)


def dax_signal_lag(dates: pd.DatetimeIndex, dax_r: pd.Series) -> np.ndarray:
    """DaxRet(D-1) : derniere seance DAX close STRICTEMENT avant D, par
    recherche directe (searchsorted) sur les dates DAX -- PAS un
    ffill+shift(1) sur le calendrier cible, qui decale par POSITION dans
    l'index cible plutot que par comparaison de date reelle, et perd
    silencieusement une seance DAX quand un jour ferie propre aux
    marches US (ou inversement) desynchronise les deux calendriers.
    Bug trouve par l'audit dedie (174 desaccords sur NDX/Russell/S&P 500,
    39 sur Composite) et corrige AVANT tout commit de resultat."""
    dax_dates = dax_r.index.values
    dax_vals = dax_r.values
    idx = np.searchsorted(dax_dates, dates.values, side="left") - 1
    out = np.full(len(dates), np.nan)
    valid = idx >= 0
    out[valid] = dax_vals[idx[valid]]
    return out


def main():
    dax_r = dax_ret_series()

    lines = [
        "# Résultat — Overlay avance-retard cross-marché DAX→marchés US (pré-enregistré, règle renforcée)",
        "",
        f"`position(t) = {CAP}x` si DaxRet(D-1) > 0 (continuation), `1,0x` sinon. "
        "DAX exclu comme marché cible (autocorrélation, pas spillover). Coûts 5 bps.",
        "",
        "| Marché | Séances test. | % temps levé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    n_markets, n_success = 0, 0

    for name, fname in TARGET_MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        dates = pd.DatetimeIndex(df["date"].values)
        bh_full = np.log(close[1:] / close[:-1])

        signal_full = dax_signal_lag(dates, dax_r)
        signal = signal_full[1:]

        start = int(np.argmax(np.isfinite(signal)))
        signal_t = signal[start:]
        bh_t = bh_full[start:]

        pos = np.where(signal_t > 0, CAP, 1.0)
        frac_lev = float((pos == CAP).mean())

        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl_ov = pos * bh_t - turn * (COST_BPS / 1e4)
        pnl_bh = bh_t.copy()
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
            f"| {name} | {len(bh_t)} | {100*frac_lev:.1f}% | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | "
            f"{me_bh['max_drawdown_pct']:.1f}% | {me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | "
            f"{me_ov['max_drawdown_pct']:.1f}% | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

        if name == "NDX (40 ans)":
            dates_pnl = dates.values[1:][start:]
            np.savez(ROOT / "results" / "nonml_dax_ndx_leadlag_overlay_pnl.npz",
                     pos=pos, r_asset=bh_t, dates=dates_pnl, cost_bps=COST_BPS)

    verdict = n_success >= 3
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé adapté : ≥3/4).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_dax_ndx_leadlag_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
