"""Robustesse — Overlay vol-targeting estimateur Yang-Zhang. Grille CAP
ET grille de fenêtre de vol (PAS un retuning de la cible), autour des
valeurs pré-enregistrées (CAP=2.0x, fenêtre=20j).
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402
from nonml_yang_zhang_vol_targeting_overlay_backtest import COST_BPS, TARGET_VOL_ANNUAL, ANNUALIZATION, MARKETS  # noqa: E402

CAP_GRID = [1.5, 2.0, 2.5, 3.0]
WINDOW_GRID = [15, 20, 25, 30]


def yang_zhang_vol_ann_lagged_n(df, n: int) -> np.ndarray:
    open_ = df["open"].values
    high = df["high"].values
    low = df["low"].values
    close = df["close"].values
    T = len(close)
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

    vol_ann_lagged = np.full(T - 1, np.nan)
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


def run_one(df, cap: float, window: int) -> bool:
    close = df["close"].values
    r = np.log(close[1:] / close[:-1])
    vol_lagged = yang_zhang_vol_ann_lagged_n(df, window)
    with np.errstate(divide="ignore", invalid="ignore"):
        pos_full = TARGET_VOL_ANNUAL / vol_lagged
    pos_full = np.clip(pos_full, 0.0, cap)
    pos_full = np.nan_to_num(pos_full, nan=1.0)

    start = window
    r_t = r[start:]
    pos = pos_full[start:]
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r_t - turn * (COST_BPS / 1e4)
    pnl_bh = r_t.copy()
    pnl_bh[0] -= COST_BPS / 1e4
    me_bh, me_ov = trading_metrics(pnl_bh), trading_metrics(pnl_ov)
    ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
    ret_ov = np.cumprod(1.0 + pnl_ov)[-1] - 1.0
    return (me_ov["sharpe_ann"] > me_bh["sharpe_ann"]) and (ret_ov > ret_bh)


def main():
    dfs = {}
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if path.exists():
            df = load_ohlc(str(path))
            quality_report(df)
            dfs[name] = df

    lines = [
        "# Robustesse — Overlay vol-targeting Yang-Zhang (grilles CAP et fenêtre, PAS un retuning)",
        "",
        "CAP pré-enregistré = 2.0x, fenêtre pré-enregistrée = 20j (n dans la formule YZ, y compris le "
        "facteur k qui en dépend, recalculé pour chaque fenêtre testée).",
        "",
        "## Grille CAP (fenêtre fixée à 20j)",
        "",
        "| CAP | Nb marchés PASS /5 |",
        "|---|---|",
    ]
    for cap in CAP_GRID:
        n_pass = sum(run_one(df, cap, 20) for df in dfs.values())
        marker = " ← CAP pré-enregistré" if cap == 2.0 else ""
        lines.append(f"| {cap}x | {n_pass}/{len(dfs)}{marker} |")

    lines.append("")
    lines.append("## Grille fenêtre de vol (CAP fixé à 2.0x)")
    lines.append("")
    lines.append("| Fenêtre | Nb marchés PASS /5 |")
    lines.append("|---|---|")
    for window in WINDOW_GRID:
        n_pass = sum(run_one(df, 2.0, window) for df in dfs.values())
        marker = " ← fenêtre pré-enregistrée" if window == 20 else ""
        lines.append(f"| {window}j | {n_pass}/{len(dfs)}{marker} |")

    out = ROOT / "results" / "nonml_yang_zhang_vol_targeting_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
