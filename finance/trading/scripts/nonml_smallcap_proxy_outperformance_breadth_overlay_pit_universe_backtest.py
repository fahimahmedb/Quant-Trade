"""Backtest — Overlay vol-targeting gaté par la breadth de surperformance des
« petites capitalisations » (proxy volatilité idiosyncratique), univers de
titres POINT-IN-TIME (spécification pré-enregistrée dans
`PREREG_smallcap_proxy_outperformance_breadth_overlay_pit_universe.md`,
committée avant ce script).

Réutilisation stricte (Règle 7) du cycle d'origine (#123) : **aucun paramètre
modifié**. Seul l'univers servant à calculer la breadth change — `data/pead/prices/`
(liste NDX-100 de 2026 appliquée rétroactivement) devient `data/pead/prices_pit/`,
et à chaque date seuls les titres membres de l'indice à cette date entrent dans
le calcul.

Particularité de ce candidat : le P&L n'est **pas** un panier de titres. Les deux
jambes sont l'indice NDX-100 lui-même. L'univers titres n'alimente que le SIGNAL.
Les conventions de P&L (rendements log, `exp(Σ) − 1`, `trading_metrics` sur la
série log) sont celles rétablies au #404 et ne sont pas retouchées ici.

**Limite de données assumée, identique à l'origine** : aucune capitalisation
boursière disponible ; « petite capitalisation » est un PROXY (moitié supérieure
par volatilité idiosyncratique glissante 60 j).
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
IDIO_VOL_WINDOW = 60
MOM_WINDOW = 21
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
        if len(close) > IDIO_VOL_WINDOW + MOM_WINDOW + 21:
            series[path.stem] = close
    return series


def compute_smallcap_breadth_series_pit():
    """Breadth_Small(t) sur l'univers POINT-IN-TIME.

    Identique au calcul d'origine, a une restriction pres : a chaque date, seuls
    les titres MEMBRES du NDX-100 a cette date sont eligibles. Avant le
    01/01/2015 aucune appartenance n'est connue -> breadth non definie (NaN),
    et non pas False : c'est ce masque explicite qui evite le piege du #396.

    Retourne aussi le nombre moyen de membres eligibles, pour le rapport.
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

    log_ret = np.log(P / P.shift(1)).values

    idio_vol = np.full((T, n_tickers), np.nan)
    for i in range(IDIO_VOL_WINDOW, T):
        window = log_ret[i - IDIO_VOL_WINDOW + 1:i + 1]
        # fenetre PLEINE requise (pre-enregistre a l'origine, conserve)
        has_full = np.isfinite(window).all(axis=0)
        with np.errstate(all="ignore"):
            vol_partial = np.nanstd(window, axis=0, ddof=1)
        idio_vol[i] = np.where(has_full, vol_partial, np.nan)

    c_lag = np.full((T, n_tickers), np.nan)
    c_lag[MOM_WINDOW:] = close[:-MOM_WINDOW]
    with np.errstate(invalid="ignore", divide="ignore"):
        mom_raw = close / c_lag - 1.0
    mom = np.where(np.isfinite(close) & np.isfinite(c_lag), mom_raw, np.nan)

    breadth = np.full(T, np.nan)
    n_members_used = []
    for i in range(T):
        if P.index[i] < COMPOSITION_START:
            continue
        members = tickers_as_of_date(P.index[i])
        if not members:
            continue
        member_cols = np.array([tickers[j] in members for j in range(n_tickers)])
        elig = np.isfinite(idio_vol[i]) & np.isfinite(mom[i]) & member_cols
        n_elig = int(elig.sum())
        if n_elig < MIN_LISTED:
            continue
        idio_elig = idio_vol[i][elig]
        mom_elig = mom[i][elig]
        median_mom_all = np.median(mom_elig)
        thresh_idio = np.median(idio_elig)
        small_mask = idio_elig >= thresh_idio
        n_small = int(small_mask.sum())
        if n_small == 0:
            continue
        breadth[i] = int((mom_elig[small_mask] > median_mom_all).sum()) / n_small
        n_members_used.append(n_elig / max(1, len(members)))

    cov = float(np.mean(n_members_used)) if n_members_used else float("nan")
    return pd.Series(breadth, index=P.index), cov


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

    breadth_small, cov = compute_smallcap_breadth_series_pit()
    median_small = breadth_small.rolling(MEDIAN_WINDOW).median()
    # PIEGE DU #396, rencontre a nouveau ici et corrige AVANT tout resultat
    # committe : `breadth >= median` rend False (et non NaN) la ou la breadth
    # est indefinie. Le script d'origine s'en sortait par accident, son univers
    # `prices/` demarrant tard ; `prices_pit/` remonte a 1985, si bien que la
    # fenetre testable partait 30 ans trop tot avec une porte fermee par defaut.
    # Masque EXPLICITE : la porte est indefinie tant que le signal l'est.
    signal_defined = breadth_small.notna() & median_small.notna()
    gate_series = (breadth_small >= median_small).where(signal_defined)
    gate_series_filled = gate_series.fillna(False)

    gate_aligned_raw = gate_series.reindex(dates_idx.values, method="ffill")
    gate_aligned = gate_series_filled.reindex(
        dates_idx.values, method="ffill").fillna(False).values.astype(bool)

    pos_full = combined_position(bh_full, gate_aligned)

    valid_mask = gate_aligned_raw.notna().values
    first_valid = int(np.argmax(valid_mask)) if valid_mask.any() else len(valid_mask)
    start = max(first_valid, VOL_WINDOW)

    bh_t = bh_full[start:]
    pos = pos_full[start:]

    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * bh_t - turn * (COST_BPS / 1e4)
    pnl_bh = bh_t.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    # Conventions retablies au #404 : pnl est deja en unites LOG.
    me_bh = trading_metrics(pnl_bh)
    me_ov = trading_metrics(pnl_ov)
    ret_bh = np.exp(pnl_bh.sum()) - 1.0
    ret_ov = np.exp(pnl_ov.sum()) - 1.0

    sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_ov > ret_bh
    verdict = sharpe_ok and ret_ok
    gate_active = (pos > 1.0)

    lines = [
        "# Résultat — breadth de surperformance « petites caps » proxy, univers POINT-IN-TIME (pré-enregistré)",
        "",
        "Réutilisation stricte (Règle 7) du cycle d'origine (#123) : **aucun paramètre "
        "modifié**. Seul l'univers servant à calculer la breadth change — à chaque date, "
        "seuls les titres réellement membres du NDX-100 entrent dans le calcul.",
        "",
        "**Limite de données assumée, identique à l'origine** : aucune capitalisation "
        "boursière disponible ; « petite capitalisation » est un PROXY (moitié supérieure "
        "par volatilité idiosyncratique glissante 60 j).",
        "",
        "**Le P&L n'est pas un panier** : les deux jambes sont l'indice NDX-100 lui-même. "
        "L'univers titres n'alimente que le signal — c'est le seul canal par lequel le biais "
        "du survivant peut agir ici.",
        "",
        f"Couverture moyenne (titres éligibles / membres réels) : {100*cov:.1f}%. "
        f"{len(bh_t)} séances testables ({dates_idx.iloc[1:].iloc[start].date()} → "
        f"{dates_idx.iloc[-1].date()}).",
        "",
        f"%j porte surperformance petites caps active : {100*gate_active.mean():.1f}%",
        f"Position moyenne : {pos.mean():.2f}x",
        f"Breadth surperformance moyenne : {100*np.nanmean(breadth_small.values):.1f}%",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold (NDX) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | "
        f"{me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Overlay gaté breadth petites caps (PIT)** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100*ret_ov:+.1f}%** | {me_ov['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay > BH : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > BH : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS (niveau 1)' if verdict else 'FAIL'} — critère renforcé "
        f"{'atteint' if verdict else 'NON atteint'} sur univers point-in-time.**",
        "",
    ]
    if verdict:
        lines.append("**PASS niveau 1 seulement — pas un verdict final (Règle 9).** Pour mémoire, "
                     "la batterie renforcée du candidat d'origine donne **1/5**.")
        lines.append("")
    lines.append("Ce résultat ne remplace pas celui du cycle d'origine : les deux coexistent. "
                 "Leur comparaison mesure l'effet du biais du survivant sur ce candidat.")
    lines.append("")

    out = ROOT / "results" / "nonml_smallcap_proxy_outperformance_breadth_overlay_pit_universe_result.md"
    out.write_text("\n".join(lines), encoding="utf-8")

    np.savez(
        ROOT / "results" / "nonml_smallcap_proxy_outperformance_breadth_overlay_pit_universe_pnl.npz",
        pos=pos, r_asset=bh_t, dates=dates_idx.values[1:][start:], cost_bps=COST_BPS,
    )

    print("\n".join(lines))
    print(f"Écrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
