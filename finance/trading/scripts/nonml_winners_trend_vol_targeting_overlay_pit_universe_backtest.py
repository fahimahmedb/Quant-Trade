"""Backtest — Winners momentum court terme + overlay combiné tendance +
vol-targeting, univers de titres POINT-IN-TIME (spécification pré-enregistrée
dans `PREREG_winners_trend_vol_targeting_overlay_pit_universe.md`, committée
avant ce script).

Réutilisation stricte (Règle 7) du cycle d'origine (#47) : **aucun paramètre
modifié**. Seul l'univers de sélection des Winners change — appartenance NDX-100
résolue à chaque date de rebalancement.

Architecture de **panier** : le biais du survivant agit sur les deux jambes, le
candidat comme sa référence (portefeuille Winners 1,0×).

Exécution causale (#166/#167) — critique ici : le signal est un momentum à
5 jours, profil pour lequel le #253 a montré qu'une fuite « même barre » est
destructrice.
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
SIGNAL_WINDOW = 5
REBAL_EVERY = 5
COST_BPS = 5.0
TERCILE = 1.0 / 3.0
CAP = 2.0
INDEX_LOOKBACK = 252
INDEX_THRESHOLD = 0.95
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
        if len(close) > SIGNAL_WINDOW + REBAL_EVERY:
            series[path.stem] = close
    return series


def index_trend_series() -> pd.Series:
    """INCHANGE : signal de tendance sur l'INDICE, sans rapport avec l'univers
    titres."""
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    rolling_max = pd.Series(close).rolling(INDEX_LOOKBACK).max().values
    near_high = close >= INDEX_THRESHOLD * rolling_max
    return pd.Series(near_high, index=pd.to_datetime(df["date"]).values)


def lag_one_day(W):
    out = np.zeros_like(W)
    out[1:] = W[:-1]
    return out


def build_weights():
    series = load_prices_pit()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    T, n_tickers = P.shape
    tickers = list(P.columns)
    close = P.values
    exists = np.isfinite(close)

    signal = np.full((T, n_tickers), np.nan)
    for i in range(SIGNAL_WINDOW, T):
        with np.errstate(all="ignore", invalid="ignore"):
            signal[i] = close[i] / close[i - SIGNAL_WINDOW] - 1.0
        signal[i, ~(exists[i] & exists[i - SIGNAL_WINDOW])] = np.nan

    n_top = max(1, int(round(n_tickers * TERCILE)))
    W = np.zeros((T, n_tickers))
    # Masque EXPLICITE des dates ou l'appartenance PIT est definie (piege #396).
    investable = np.zeros(T, dtype=bool)
    coverage = []

    rebal_dates = list(range(SIGNAL_WINDOW, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        if P.index[t] < COMPOSITION_START:
            continue
        members = tickers_as_of_date(P.index[t])
        if not members:
            continue
        member_cols = np.array([tickers[j] in members for j in range(n_tickers)])
        s = signal[t]
        elig = np.where(np.isfinite(s) & member_cols)[0]
        n_top_t = min(n_top, len(elig))
        if n_top_t > 0:
            top_idx = elig[np.argsort(-s[elig])[:n_top_t]]
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top_t
            W[t:end] = w
            investable[t:end] = True
            coverage.append(len(elig) / max(1, len(members)))

    cov = float(np.mean(coverage)) if coverage else float("nan")
    return P, tickers, W, investable, cov


def main(causal=True):
    P, tickers, W, investable, cov = build_weights()
    R = (P / P.shift(1) - 1.0).values.copy()
    R[0, :] = 0.0
    R_safe = np.nan_to_num(R, nan=0.0)

    trend = index_trend_series()
    trend_aligned = trend.reindex(P.index, method="ffill").fillna(False).values.astype(bool)

    pnl_winners_raw = (W * R_safe).sum(axis=1)
    vol_ann = pd.Series(pnl_winners_raw).rolling(VOL_WINDOW).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        vt_exposure = TARGET_VOL_ANNUAL / vol_lagged
    vt_exposure = np.clip(vt_exposure, 1.0, CAP)
    vt_exposure = np.nan_to_num(vt_exposure, nan=1.0)

    exposure = np.where(trend_aligned, vt_exposure, 1.0)

    weights_base = W
    weights_lev = W * exposure[:, None]
    if causal:
        weights_base = lag_one_day(weights_base)
        weights_lev = lag_one_day(weights_lev)
        trend_aligned = np.concatenate(([False], trend_aligned[:-1]))

    # La volatilite du portefeuille doit etre estimee sur une fenetre
    # entierement contenue dans la periode investissable, sinon les zeros
    # anterieurs ecrasent l'ecart-type. Transposition directe du
    # `max(SIGNAL_WINDOW, VOL_WINDOW)` de l'original.
    inv_lag = np.concatenate(([False], investable[:-1]))
    first = int(np.argmax(inv_lag)) if inv_lag.any() else len(P)
    start2 = max(SIGNAL_WINDOW, VOL_WINDOW, first + VOL_WINDOW)

    # Garde EXECUTABLE du piege du #396 (leçon du #405).
    start_date = P.index[start2]
    if start_date < COMPOSITION_START:
        raise SystemExit(
            f"PIEGE DU #396 : la fenetre testable demarre le {start_date.date()}, "
            "anterieurement a la composition point-in-time. Resultat invalide."
        )

    pnl_base = (weights_base[start2:] * R_safe[start2:]).sum(axis=1)
    pnl_lev = (weights_lev[start2:] * R_safe[start2:]).sum(axis=1)

    turn_base = np.abs(np.diff(weights_base[start2:], axis=0,
                               prepend=weights_base[start2:start2 + 1])).sum(axis=1) / 2.0
    turn_lev = np.abs(np.diff(weights_lev[start2:], axis=0,
                              prepend=weights_lev[start2:start2 + 1])).sum(axis=1) / 2.0
    pnl_gross_bh_, pnl_gross_ov_ = pnl_base.copy(), pnl_lev.copy()
    pnl_base = pnl_base - turn_base * (COST_BPS / 1e4)
    pnl_lev = pnl_lev - turn_lev * (COST_BPS / 1e4)

    me_base = trading_metrics(np.log1p(pnl_base))
    me_lev = trading_metrics(np.log1p(pnl_lev))
    ret_base = np.cumprod(1.0 + pnl_base)[-1] - 1.0
    ret_lev = np.cumprod(1.0 + pnl_lev)[-1] - 1.0

    sharpe_ok = me_lev["sharpe_ann"] > me_base["sharpe_ann"]
    ret_ok = ret_lev > ret_base
    verdict = sharpe_ok and ret_ok

    lines = [
        "# Résultat — Winners court terme + overlay tendance/vol-targeting, univers POINT-IN-TIME (pré-enregistré)",
        "",
        "Réutilisation stricte (Règle 7) du cycle d'origine (#47) : **aucun paramètre "
        "modifié**. Seul l'univers de sélection des Winners change — appartenance NDX-100 "
        "résolue à chaque date de rebalancement. Exécution causale (#166/#167).",
        "",
        "Référence = portefeuille Winners 1,0×, **pas** Buy&Hold — le biais du survivant "
        "affecte donc les deux jambes.",
        "",
        f"Univers PIT : {len(tickers)} tickers, couverture moyenne {100*cov:.1f}%. "
        f"{len(pnl_base)} séances testables ({start_date.date()} → {P.index[-1].date()}). "
        f"Overlay actif {100*float(trend_aligned[start2:].mean()):.1f}% du temps.",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Winners 1.0x (référence) | {me_base['sharpe_ann']:+.2f} | "
        f"{100*ret_base:+.1f}% | {me_base['max_drawdown_pct']:.1f}% |",
        f"| **Winners + overlay tendance+vol-targeting** | **{me_lev['sharpe_ann']:+.2f}** | "
        f"**{100*ret_lev:+.1f}%** | {me_lev['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay > référence : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > référence : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé (Sharpe ET rendement) "
        f"{'atteint' if verdict else 'NON atteint'} sur univers point-in-time.**",
        "",
    ]
    if verdict:
        lines.append("**⚠️ L'avertissement du #14 n'est PAS levé par ce cycle**, comme annoncé "
                     "au pré-enregistrement : ce portage teste l'**univers**, pas la **période**. "
                     "Le portefeuille Winners affiche un edge extrême potentiellement propre au "
                     "bull market IA/semiconducteurs, et cette fenêtre reste dominée par ce "
                     "même marché. Un maintien lève le doute sur l'univers, rien de plus.")
        lines.append("")
    lines.append("Ce résultat ne remplace pas celui du cycle d'origine : les deux coexistent. "
                 "Leur comparaison mesure l'effet du biais du survivant sur ce candidat.")
    lines.append("")

    out = ROOT / "results" / "nonml_winners_trend_vol_targeting_overlay_pit_universe_result.md"
    out.write_text("\n".join(lines), encoding="utf-8")

    np.savez(ROOT / "results" / "nonml_winners_trend_vol_targeting_overlay_pit_universe_pnl.npz",
             pnl_gross_ov=pnl_gross_ov_, pnl_gross_bh=pnl_gross_bh_,
             turn_ov=turn_lev, turn_bh=turn_base,
             dates=np.asarray(P.index)[start2:], cost_bps=COST_BPS)

    print("\n".join(lines))
    print(f"Écrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
