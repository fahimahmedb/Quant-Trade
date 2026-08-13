"""Backtest — Overlay vol-targeting gaté par la breadth de drawdown profond,
univers de titres POINT-IN-TIME (spécification pré-enregistrée dans
`PREREG_deep_drawdown_breadth_vol_targeting_overlay_pit_universe.md`,
committée avant ce script).

Réutilisation stricte (Règle 7) du cycle d'origine
(`nonml_deep_drawdown_breadth_vol_targeting_overlay_backtest.py`) : **aucun
paramètre n'est modifié**. Seul l'univers servant à construire le SIGNAL change —
`data/pead/prices/` (liste NDX-100 figée de 2026, biaisée par le survivant)
devient `data/pead/prices_pit/` avec appartenance résolue à chaque date par
`ndx100_membership.tickers_as_of_date`.

Le P&L reste **indiciel** (`pos * rendement log du NDX`) : l'univers de titres
n'intervient que dans le comptage de la breadth.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402
from ndx100_membership import tickers_as_of_date  # noqa: E402

PRICES_PIT_DIR = ROOT / "data" / "pead" / "prices_pit"
COMPOSITION_START = pd.Timestamp("2015-01-01")

# --- Parametres REPRIS A L'IDENTIQUE du cycle d'origine (Regle 7) ---
INDEX_LOOKBACK = 252
DD_THRESHOLD = 0.80
MEDIAN_WINDOW = 252
COST_BPS = 5.0
CAP = 2.0
VOL_WINDOW = 20
TARGET_VOL_ANNUAL = 0.20
ANNUALIZATION = np.sqrt(252)


def load_prices_pit():
    series = {}
    for path in sorted(PRICES_PIT_DIR.glob("*.json")):
        payload = json.loads(path.read_text())
        if "error" in payload:
            continue
        ts = pd.to_datetime(payload["ts"], unit="s").normalize()
        close = pd.Series(payload["close"], index=ts, dtype=float).dropna()
        close = close[~close.index.duplicated(keep="first")].sort_index()
        if len(close) > INDEX_LOOKBACK + 21:
            series[path.stem] = close
    return series


def compute_deep_drawdown_breadth_series_pit():
    """Breadth_DD(t) = fraction des titres MEMBRES de l'indice a la date t
    (appartenance point-in-time) et cotes ce jour-la dont le prix est >=20%
    sous leur plus haut glissant 252j (fenetre pleine requise).

    Seule difference avec le cycle d'origine : le denominateur et le numerateur
    sont restreints aux membres REELS a la date t, au lieu de la liste NDX-100
    de 2026 appliquee retroactivement.
    """
    series = load_prices_pit()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    close = P.values
    T, n_tickers = P.shape
    exists = np.isfinite(close)

    rolling_high = np.full((T, n_tickers), np.nan)
    has_full = np.zeros((T, n_tickers), dtype=bool)
    for i in range(INDEX_LOOKBACK, T):
        window = close[i - INDEX_LOOKBACK + 1:i + 1]
        has_full[i] = np.isfinite(window).all(axis=0)
        with np.errstate(all="ignore"):
            rolling_high[i] = np.nanmax(window, axis=0)
    deep_dd = np.where(has_full, close <= DD_THRESHOLD * rolling_high, False)

    breadth = np.full(T, np.nan)
    coverage = []
    for i in range(T):
        if P.index[i] < COMPOSITION_START:
            continue
        members = tickers_as_of_date(P.index[i])
        member_cols = np.array([tickers[j] in members for j in range(n_tickers)])
        listed_row = exists[i] & member_cols
        n_listed = int(listed_row.sum())
        if n_listed > 0:
            breadth[i] = int((deep_dd[i] & listed_row).sum()) / n_listed
            coverage.append(n_listed / max(1, len(members)))

    return pd.Series(breadth, index=P.index), (float(np.mean(coverage)) if coverage else float("nan")), len(tickers)


def combined_position(r: np.ndarray, gate_aligned: np.ndarray) -> np.ndarray:
    gate_r = gate_aligned[:-1]
    vol_ann = pd.Series(r).rolling(VOL_WINDOW).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        vt_exposure = TARGET_VOL_ANNUAL / vol_lagged
    vt_exposure = np.clip(vt_exposure, 1.0, CAP)
    vt_exposure = np.nan_to_num(vt_exposure, nan=1.0)
    pos = np.where(gate_r, vt_exposure, 1.0)
    return np.nan_to_num(pos, nan=1.0)


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_idx = pd.to_datetime(df["date"])
    bh_full = np.log(close[1:] / close[:-1])

    breadth_dd, coverage, n_tickers = compute_deep_drawdown_breadth_series_pit()
    median_dd = breadth_dd.rolling(MEDIAN_WINDOW).median()
    # `breadth >= median` rend False (et non NaN) la ou breadth est NaN. Or
    # `prices_pit` couvre 1985-2026 alors que la breadth PIT n'existe qu'a partir
    # de COMPOSITION_START : sans ce masque, la fenetre testable demarrerait en
    # 1985 avec 30 ans ou la porte est eteinte faute de signal, ce qui diluerait
    # le test au lieu de le restreindre. On force donc NaN la ou le signal
    # n'existe pas, pour reproduire la convention du cycle d'origine
    # ("echantillon restreint a la periode ou la breadth est disponible").
    signal_defined = breadth_dd.notna() & median_dd.notna()
    gate_series = (breadth_dd >= median_dd).where(signal_defined)
    gate_series_filled = gate_series.fillna(False)

    gate_aligned_raw = gate_series.reindex(dates_idx.values, method="ffill")
    gate_aligned = gate_series_filled.reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)

    pos_full = combined_position(bh_full, gate_aligned)

    valid_mask = gate_aligned_raw.notna().values
    first_valid = int(np.argmax(valid_mask)) if valid_mask.any() else len(valid_mask)
    start = max(first_valid, VOL_WINDOW)

    bh_t = bh_full[start:]
    pos = pos_full[start:]
    dates_t = dates_idx.values[1:][start:]

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
    verdict = sharpe_ok and ret_ok
    gate_active = (pos > 1.0)

    lines = [
        "# Résultat — Breadth de drawdown profond, univers POINT-IN-TIME (pré-enregistré)",
        "",
        "Réutilisation stricte (Règle 7) du cycle d'origine : **aucun paramètre modifié**. "
        "Seul l'univers du SIGNAL change — appartenance NDX-100 résolue à chaque date "
        "(`tickers_as_of_date`) au lieu de la liste 2026 appliquée rétroactivement.",
        "",
        f"`position(t) = clip({TARGET_VOL_ANNUAL:.0%} / vol_réalisée_{VOL_WINDOW}j(t-1), 1.0, {CAP}x)` "
        f"si Breadth_DD(t) ≥ sa médiane glissante {MEDIAN_WINDOW}j, sinon 1.0x. "
        f"Coûts {COST_BPS:.0f} bps.",
        "",
        f"Univers PIT : {n_tickers} tickers disponibles. Couverture moyenne "
        f"(membres avec prix / membres réels) : {100*coverage:.1f}%.",
        f"{len(bh_t)} séances testables ({pd.Timestamp(dates_t[0]).date()} → {pd.Timestamp(dates_t[-1]).date()}).",
        "",
        f"%j porte drawdown profond active : {100*gate_active.mean():.1f}%",
        f"Position moyenne : {pos.mean():.2f}x",
        f"Breadth drawdown profond moyenne : {100*np.nanmean(breadth_dd.values):.1f}%",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold (NDX) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Overlay gaté breadth DD (univers PIT)** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100*ret_ov:+.1f}%** | {me_ov['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay > Buy&Hold : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > Buy&Hold : {'OUI' if ret_ok else 'non'}",
        "",
    ]
    if verdict:
        lines.append("**PASS — critère renforcé (Sharpe ET rendement) atteint sur univers point-in-time.**")
    else:
        lines.append("**FAIL — critère renforcé (Sharpe ET rendement) NON atteint sur univers point-in-time.**")
    lines.append("")
    lines.append("Ce résultat ne remplace pas celui du cycle d'origine : les deux coexistent, "
                 "comme les 7 paires `*_pit_universe` déjà committées. La comparaison des deux "
                 "mesure l'effet du biais du survivant sur ce candidat.")
    lines.append("")

    out = ROOT / "results" / "nonml_deep_drawdown_breadth_vol_targeting_overlay_pit_universe_result.md"
    out.write_text("\n".join(lines), encoding="utf-8")

    np.savez(ROOT / "results" / "nonml_deep_drawdown_breadth_vol_targeting_overlay_pit_universe_pnl.npz",
             pos=pos, r_asset=bh_t, dates=dates_t, cost_bps=COST_BPS)

    print("\n".join(lines))
    print(f"Écrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
