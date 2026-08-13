"""Backtest — Overlay vol-targeting gaté par la position moyenne dans le range
annuel, univers de titres POINT-IN-TIME (spécification pré-enregistrée dans
`PREREG_market_concentration_vol_targeting_overlay_pit_universe.md`, committée avant
ce script).

Réutilisation stricte (Règle 7) du cycle d'origine (#102) : **aucun paramètre
modifié**. Seul l'univers change — à chaque date, seuls les titres réellement
membres du NDX-100 entrent dans le calcul du HHI.

Le P&L n'est **pas** un panier : les deux jambes sont l'indice NDX-100 lui-même.
Conventions de P&L rétablies au #404.

Le piège du #396 est traité par un masque explicite **et** par une garde qui lève
une exception si la fenêtre testable démarre avant la composition point-in-time.
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
CONC_WINDOW = 60
MEDIAN_WINDOW = 252
MIN_LISTED = 10
COST_BPS = 5.0
CAP = 2.0
VOL_WINDOW = 20
TARGET_VOL_ANNUAL = 0.20
ANNUALIZATION = np.sqrt(252)


def load_all_prices_pit():
    series = {}
    for path in sorted(PRICES_PIT_DIR.glob("*.json")):
        payload = json.loads(path.read_text())
        if "error" in payload:
            continue
        ts = pd.to_datetime(payload["ts"], unit="s").normalize()
        close = pd.Series(payload["close"], index=ts, dtype=float).dropna()
        close = close[~close.index.duplicated(keep="first")].sort_index()
        if len(close) > CONC_WINDOW + 21:
            series[path.stem] = close
    return series


def compute_concentration_series_pit():
    """Concentration(t) = HHI des parts de contribution POSITIVE au rendement
    cumule CONC_WINDOW jours, calcule sur les seuls MEMBRES du NDX-100 a la
    date t.

    Convention du cycle d'origine CONSERVEE : si aucune contribution n'est
    positive sur la fenetre, HHI = 1/n (concentration minimale, parts egales).

    NaN avant le 01/01/2015 ou si moins de MIN_LISTED membres eligibles.
    Retourne aussi la couverture moyenne et le nombre moyen de titres retenus
    (le HHI depend de n, point signale au pre-enregistrement).
    """
    series = load_all_prices_pit()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    close = P.values
    T, n_tickers = P.shape
    tickers = list(P.columns)

    cum_ret = np.full((T, n_tickers), np.nan)
    cum_ret[CONC_WINDOW:] = close[CONC_WINDOW:] / close[:-CONC_WINDOW] - 1.0
    eligible = np.isfinite(cum_ret)

    conc = np.full(T, np.nan)
    coverage, n_used = [], []
    for t in range(CONC_WINDOW, T):
        if P.index[t] < COMPOSITION_START:
            continue
        members = tickers_as_of_date(P.index[t])
        if not members:
            continue
        member_cols = np.array([tickers[j] in members for j in range(n_tickers)])
        elig_t = eligible[t] & member_cols
        n_elig = int(elig_t.sum())
        if n_elig < MIN_LISTED:
            continue
        contrib = np.clip(cum_ret[t, elig_t], 0.0, None)
        total = contrib.sum()
        if total <= 0:
            conc[t] = 1.0 / n_elig
        else:
            shares = contrib / total
            conc[t] = float(np.sum(shares ** 2))
        coverage.append(n_elig / max(1, len(members)))
        n_used.append(n_elig)

    cov = float(np.mean(coverage)) if coverage else float("nan")
    n_mean = float(np.mean(n_used)) if n_used else float("nan")
    return pd.Series(conc, index=P.index), cov, n_mean


def build_gate(conc):
    """Porte : la concentration doit etre SOUS sa mediane glissante (marche
    large). Masque EXPLICITE du piege du #396, present des la premiere
    execution comme exige par le pre-enregistrement."""
    median_conc = conc.rolling(MEDIAN_WINDOW).median()
    signal_defined = conc.notna() & median_conc.notna()
    return (conc <= median_conc).where(signal_defined)


def combined_position(r: np.ndarray, gate_aligned: np.ndarray) -> np.ndarray:
    """INCHANGE par rapport au cycle d'origine."""
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

    conc, cov, n_mean = compute_concentration_series_pit()
    gate_series = build_gate(conc)

    gate_aligned_raw = gate_series.reindex(dates_idx.values, method="ffill")
    gate_aligned = gate_series.fillna(False).reindex(
        dates_idx.values, method="ffill").fillna(False).values.astype(bool)

    pos_full = combined_position(bh_full, gate_aligned)

    valid_mask = gate_aligned_raw.notna().values
    first_valid = int(np.argmax(valid_mask)) if valid_mask.any() else len(valid_mask)
    start = max(first_valid, VOL_WINDOW)

    # Garde EXECUTABLE du piege du #396 (leçon du #405).
    start_date = dates_idx.iloc[1:].iloc[start]
    if start_date < COMPOSITION_START:
        raise SystemExit(
            f"PIEGE DU #396 : la fenetre testable demarre le {start_date.date()}, "
            "anterieurement a la composition point-in-time. Resultat invalide, "
            "a corriger avant tout commit."
        )

    bh_t = bh_full[start:]
    pos = pos_full[start:]

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
        "# Résultat — concentration du marché (HHI), univers POINT-IN-TIME (pré-enregistré)",
        "",
        "Réutilisation stricte (Règle 7) du cycle d'origine (#102) : **aucun paramètre "
        "modifié**. Seul l'univers change — à chaque date, seuls les titres réellement "
        "membres du NDX-100 entrent dans le calcul du HHI.",
        "",
        "**Le P&L n'est pas un panier** : les deux jambes sont l'indice NDX-100 lui-même. "
        "L'univers titres n'alimente que la porte.",
        "",
        f"Couverture moyenne (titres éligibles / membres réels) : {100*cov:.1f}%. "
        f"{len(bh_t)} séances testables ({start_date.date()} → {dates_idx.iloc[-1].date()}).",
        "",
        f"%j porte concentration active : {100*gate_active.mean():.1f}%",
        f"Position exposition moyenne : {pos.mean():.2f}x",
        f"Concentration (HHI) moyenne observée : {np.nanmean(conc.values):.4f} "
        f"(sur {n_mean:.0f} titres en moyenne — le HHI dépend de n, cf. PREREG)",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold (NDX) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | "
        f"{me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Overlay gaté concentration (PIT)** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100*ret_ov:+.1f}%** | {me_ov['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay > BH : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > BH : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé (Sharpe ET rendement) "
        f"{'atteint' if verdict else 'NON atteint'} sur univers point-in-time.**",
        "",
        "Ce résultat ne remplace pas celui du cycle d'origine : les deux coexistent. "
        "Leur comparaison mesure l'effet du biais du survivant sur ce candidat.",
        "",
    ]

    out = ROOT / "results" / "nonml_market_concentration_vol_targeting_overlay_pit_universe_result.md"
    out.write_text("\n".join(lines), encoding="utf-8")

    np.savez(
        ROOT / "results" / "nonml_market_concentration_vol_targeting_overlay_pit_universe_pnl.npz",
        pos=pos, r_asset=bh_t, dates=dates_idx.values[1:][start:], cost_bps=COST_BPS,
    )

    print("\n".join(lines))
    print(f"Écrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
