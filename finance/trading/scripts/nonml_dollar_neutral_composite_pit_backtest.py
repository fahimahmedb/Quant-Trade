"""Backtest — Portefeuille long/short dollar-neutre composite (Piste A
de RECHERCHE_dsr_par_construction.md), univers POINT-IN-TIME réel du
NDX-100 (spécification pré-enregistrée dans
PREREG_dollar_neutral_composite_pit.md, committée avant ce script).
n_trials=1, aucune dépendance ML.

Composite ÉQUIPONDÉRÉ de 4 signaux déjà pré-enregistrés et testés
individuellement (Règle 7, formules inchangées à la lettre) :
- #4  52-week-high : ratio(t) = close(t) / max(close[t-251:t+1])
- #73 Momentum 12-1 : close(t-21)/close(t-252) - 1
- #82 Momentum de constance : consistency_at() du #82
- #15 Low-vol (SIGNE INVERSÉ) : -std(rendements simples, fenêtre 60j)

Pondération continue z-score dollar-neutre : w = (z - mean(z)) /
sum(|z - mean(z)|) * 2, rebalancement 21j, ancrage 2015-01-01,
exécution causale (lag_one_day), coûts 5 bps sur le turnover.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prediction import trading_metrics  # noqa: E402
from ndx100_membership import tickers_as_of_date  # noqa: E402
from nonml_momentum_consistency_backtest import consistency_at, N_BLOCKS, BLOCK_LEN  # noqa: E402

PRICES_PIT_DIR = ROOT / "data" / "pead" / "prices_pit"

LOOKBACK_52W = 252
LOOKBACK_MOM = 252
SKIP_MOM = 21
LOOKBACK_CONSISTENCY = N_BLOCKS * BLOCK_LEN  # 252
VOL_WINDOW = 60
REBAL_EVERY = 21
COST_BPS = 5.0
REBAL_ANCHOR = "2015-01-01"
MIN_ELIGIBLE = 30
GROSS_EXPOSURE = 2.0


def lag_one_day(W: np.ndarray) -> np.ndarray:
    out = np.zeros_like(W)
    out[1:] = W[:-1]
    return out


def load_prices() -> dict:
    series = {}
    for path in sorted(PRICES_PIT_DIR.glob("*.json")):
        payload = json.loads(path.read_text())
        if "error" in payload:
            continue
        ts = pd.to_datetime(payload["ts"], unit="s").normalize()
        close = pd.Series(payload["close"], index=ts, dtype=float).dropna()
        close = close[~close.index.duplicated(keep="first")].sort_index()
        max_lb = max(LOOKBACK_52W, LOOKBACK_MOM, LOOKBACK_CONSISTENCY, VOL_WINDOW)
        if len(close) > max_lb + REBAL_EVERY:
            series[path.stem] = close
    return series


def zscore(x: np.ndarray) -> np.ndarray:
    """z-score cross-sectionnel sur les valeurs finies uniquement (ddof=0)."""
    out = np.full_like(x, np.nan)
    valid = np.isfinite(x)
    if valid.sum() < 2:
        return out
    mu = x[valid].mean()
    sd = x[valid].std(ddof=0)
    if sd <= 0:
        return out
    out[valid] = (x[valid] - mu) / sd
    return out


def main():
    series = load_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    T, n_tickers = P.shape
    close = P.values
    R = np.log(P / P.shift(1)).values
    R[0, :] = 0.0
    R_safe = np.nan_to_num(R, nan=0.0)
    simple_ret = P.pct_change(fill_method=None).values

    # --- Signal 1 : 52-week-high ratio ---
    rolling_max = np.full((T, n_tickers), np.nan)
    has_full_window = np.zeros((T, n_tickers), dtype=bool)
    for i in range(LOOKBACK_52W, T):
        window = close[i - LOOKBACK_52W + 1:i + 1]
        has_full_window[i] = np.isfinite(window).all(axis=0)
        with np.errstate(all="ignore"):
            rolling_max[i] = np.nanmax(window, axis=0)
    sig_52w = np.where(has_full_window, close / rolling_max, np.nan)

    # --- Signal 2 : momentum 12-1 ---
    sig_mom = np.full((T, n_tickers), np.nan)
    for i in range(LOOKBACK_MOM, T):
        c_skip = close[i - SKIP_MOM]
        c_lookback = close[i - LOOKBACK_MOM]
        with np.errstate(all="ignore"):
            m = c_skip / c_lookback - 1.0
        valid = np.isfinite(c_skip) & np.isfinite(c_lookback)
        sig_mom[i, valid] = m[valid]

    # --- Signal 3 : momentum de constance (#82) ---
    sig_consistency = np.full((T, n_tickers), np.nan)
    for i in range(LOOKBACK_CONSISTENCY, T):
        sig_consistency[i] = consistency_at(close, i)

    # --- Signal 4 : low-vol (signe inversé) ---
    vol = pd.DataFrame(simple_ret).rolling(VOL_WINDOW).std().values
    sig_low_vol = np.where(np.isfinite(vol), -vol, np.nan)

    weights = np.zeros((T, n_tickers))
    weights_bh = np.zeros((T, n_tickers))

    first_rebal = max(LOOKBACK_52W, LOOKBACK_MOM, LOOKBACK_CONSISTENCY, VOL_WINDOW,
                       int(P.index.searchsorted(pd.Timestamp(REBAL_ANCHOR))))
    rebal_dates = list(range(first_rebal, T, REBAL_EVERY))
    membership_log = []

    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        members = tickers_as_of_date(P.index[t])
        member_mask = np.array([tickers[j] in members for j in range(n_tickers)])

        all_signals_finite = (
            np.isfinite(sig_52w[t]) & np.isfinite(sig_mom[t]) &
            np.isfinite(sig_consistency[t]) & np.isfinite(sig_low_vol[t])
        )
        eligible = np.where(member_mask & all_signals_finite)[0]
        membership_log.append((P.index[t], len(members), len(eligible)))

        if len(eligible) > 0:
            weights_bh[t:end, eligible] = 1.0 / len(eligible)

        if len(eligible) < MIN_ELIGIBLE:
            continue  # portefeuille a plat sur cette periode (declare au PREREG)

        z1 = zscore(sig_52w[t, eligible])
        z2 = zscore(sig_mom[t, eligible])
        z3 = zscore(sig_consistency[t, eligible])
        z4 = zscore(sig_low_vol[t, eligible])
        z_composite = np.nanmean(np.vstack([z1, z2, z3, z4]), axis=0)

        w_raw = z_composite - np.nanmean(z_composite)
        gross = np.nansum(np.abs(w_raw))
        if gross <= 0:
            continue
        w = w_raw / gross * GROSS_EXPOSURE

        w_full = np.zeros(n_tickers)
        w_full[eligible] = w
        weights[t:end] = w_full

    weights = lag_one_day(weights)
    weights_bh = lag_one_day(weights_bh)

    start = first_rebal
    pnl_sleeve = (weights[start:] * R_safe[start:]).sum(axis=1)
    pnl_bh = (weights_bh[start:] * R_safe[start:]).sum(axis=1)
    turn_sleeve = np.abs(np.diff(weights[start:], axis=0, prepend=weights[start:start + 1])).sum(axis=1) / 2.0
    turn_bh = np.abs(np.diff(weights_bh[start:], axis=0, prepend=weights_bh[start:start + 1])).sum(axis=1) / 2.0
    pnl_sleeve_net = pnl_sleeve - turn_sleeve * (COST_BPS / 1e4)
    pnl_bh_net = pnl_bh - turn_bh * (COST_BPS / 1e4)

    dates_test = P.index[start:]

    me_sleeve = trading_metrics(pnl_sleeve_net)
    me_bh = trading_metrics(pnl_bh_net)
    ret_sleeve = float(np.cumprod(1.0 + pnl_sleeve_net)[-1] - 1.0)
    ret_bh = float(np.cumprod(1.0 + pnl_bh_net)[-1] - 1.0)

    sharpe_daily = pnl_sleeve_net.mean() / pnl_sleeve_net.std() if pnl_sleeve_net.std() > 0 else float("nan")
    tstat = sharpe_daily * np.sqrt(len(pnl_sleeve_net))

    ok_sharpe_pos = me_sleeve["sharpe_ann"] > 0
    ok_tstat = tstat > 2
    verdict = ok_sharpe_pos and ok_tstat

    corr_mkt = float(np.corrcoef(pnl_sleeve_net, pnl_bh_net)[0, 1])

    avg_coverage = np.mean([n_e / max(1, n_m) for _, n_m, n_e in membership_log])
    n_active_periods = sum(1 for _, _, n_e in membership_log if n_e >= MIN_ELIGIBLE)

    lines = [
        "# Résultat — Portefeuille long/short dollar-neutre composite (#4+#73+#82+#15), univers PIT (pré-enregistré)",
        "",
        f"Univers PIT : {n_tickers} tickers avec prix PIT disponibles. Couverture moyenne "
        f"éligibles/membres : {100*avg_coverage:.1f}%. {len(rebal_dates)} dates de rebalancement, "
        f"dont {n_active_periods} avec ≥{MIN_ELIGIBLE} titres éligibles (portefeuille actif). "
        f"{T - start} séances testables ({dates_test[0].date()} → {dates_test[-1].date()}). "
        "Poids continus dollar-neutre (z-score composite #4+#73+#82+(-#15) équipondéré, "
        f"Σ|w|={GROSS_EXPOSURE:.0f}), rebalancement 21j, exécution causale. Coûts 5 bps sur turnover.",
        "",
        "| | Sharpe ann. | Sharpe journalier | t-stat | Rendement total net | MDD |",
        "|---|---|---|---|---|---|",
        f"| Buy&Hold équipondéré (univers PIT, contexte) | {me_bh['sharpe_ann']:+.2f} | — | — | "
        f"{100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Sleeve L/S dollar-neutre composite** | **{me_sleeve['sharpe_ann']:+.2f}** | "
        f"{sharpe_daily:+.4f} | **{tstat:+.2f}** | {100*ret_sleeve:+.1f}% | {me_sleeve['max_drawdown_pct']:.1f}% |",
        "",
        f"Corrélation quotidienne sleeve vs Buy&Hold PIT : {corr_mkt:+.3f} (proche de 0 attendu pour un "
        "portefeuille dollar-neutre).",
        "",
        f"1. Sharpe annualisé > 0 : {'OUI' if ok_sharpe_pos else 'non'}",
        f"2. t-stat > 2 : {'OUI' if ok_tstat else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré (Sharpe>0 ET t-stat>2, "
        f"réutilisé du #PEAD) {'atteint' if verdict else 'NON atteint'}.**",
        "",
        "**Limite non modélisée, rappelée ici** : aucun coût d'emprunt de titres ni contrainte "
        "de disponibilité/rappel de prêt sur la jambe courte (situation la plus favorable "
        "possible sur cet univers de méga-capitalisations liquides, mais pas nulle en réalité).",
    ]

    out = ROOT / "results" / "nonml_dollar_neutral_composite_pit_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")

    np.savez(ROOT / "results" / "nonml_dollar_neutral_composite_pit_pnl.npz",
             pnl_candidate=pnl_sleeve_net, turn_candidate=turn_sleeve,
             pnl_ref=pnl_bh_net, turn_ref=turn_bh,
             dates=dates_test.values, cost_bps=COST_BPS)

    return verdict


if __name__ == "__main__":
    main()
