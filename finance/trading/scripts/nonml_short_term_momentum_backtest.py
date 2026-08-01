"""Backtest — Momentum court terme, 1 semaine (spécification pré-enregistrée
dans PREREG_short_term_momentum.md, committée avant ce script). n_trials=1,
aucune dépendance ML. Soumis à la règle de succès renforcée. Réutilise la
construction d'univers dynamique du cycle #4/#5 -- seul le sens du tri
change (tercile SUPÉRIEUR au lieu d'inférieur).
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from prediction import trading_metrics  # noqa: E402

PRICES_DIR = ROOT / "data" / "pead" / "prices"
SIGNAL_WINDOW = 5
REBAL_EVERY = 5
COST_BPS = 5.0
TERCILE = 1.0 / 3.0


def load_prices(prices_dir=None, panel_start=None):
    """`prices_dir` / `panel_start` (cycle #164) : sources optionnelles. `None`
    par defaut = comportement d'origine (#14) strictement inchange."""
    series = {}
    for path in sorted((prices_dir or PRICES_DIR).glob("*.json")):
        payload = json.loads(path.read_text())
        if "error" in payload:
            continue
        ts = pd.to_datetime(payload["ts"], unit="s").normalize()
        close = pd.Series(payload["close"], index=ts, dtype=float).dropna()
        close = close[~close.index.duplicated(keep="first")].sort_index()
        if panel_start is not None:
            close = close[close.index >= pd.Timestamp(panel_start)]
        if len(close) > SIGNAL_WINDOW + REBAL_EVERY + 10:
            series[path.stem] = close
    return series


def build_universe(prices_dir=None, panel_start=None):
    series = load_prices(prices_dir, panel_start)
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    return P


def lag_one_day(W):
    """Convention d'execution CAUSALE : le poids decide a la cloture de t-1 est
    celui detenu pendant la seance t. Correction de la fuite « meme barre »
    documentee dans `results/nonml_same_bar_execution_audit.md` (01/08/2026)."""
    out = np.zeros_like(W)
    out[1:] = W[:-1]
    return out


def main(prices_dir=None, panel_start=None, membership_fn=None,
         rebal_anchor=None, out_suffix="", header_note=None, causal=True):
    """Arguments optionnels (cycle #164, pre-enregistres dans
    PREREG_short_term_momentum_pit_universe.md) : univers POINT-IN-TIME.
    `membership_fn(timestamp) -> set[str]` restreint, a CHAQUE date de
    rebalancement, les titres eligibles ET la reference equiponderee aux
    membres reels de l'indice ce jour-la.

    CORRECTION 01/08/2026 -- fuite d'execution « meme barre » : le signal
    close(t)/close(t-5)-1 servait a selectionner des titres qui encaissaient
    ensuite le rendement DU JOUR t, deja contenu dans ce signal. `causal=True`
    (defaut) decale l'execution d'un jour ; `causal=False` reproduit le
    comportement fautif d'origine, uniquement pour l'audit qui le chiffre."""
    P = build_universe(prices_dir, panel_start)
    T, n_tickers = P.shape
    close = P.values
    exists = np.isfinite(close)
    R = np.log(P / P.shift(1)).values
    R[0, :] = 0.0
    R_safe = np.nan_to_num(R, nan=0.0)

    signal = np.full((T, n_tickers), np.nan)
    for i in range(SIGNAL_WINDOW, T):
        with np.errstate(all="ignore", invalid="ignore"):
            signal[i] = close[i] / close[i - SIGNAL_WINDOW] - 1.0
        signal[i, ~(exists[i] & exists[i - SIGNAL_WINDOW])] = np.nan

    tickers = list(P.columns)
    weights_winners = np.zeros((T, n_tickers))
    weights_bh = np.zeros((T, n_tickers))
    start = SIGNAL_WINDOW
    if rebal_anchor is not None:
        start = max(start, int(P.index.searchsorted(pd.Timestamp(rebal_anchor))))
    rebal_dates = list(range(start, T, REBAL_EVERY))
    coverage = []
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        s = signal[t]
        elig = np.where(np.isfinite(s))[0]
        listed = exists[t]
        if membership_fn is not None:
            members = membership_fn(P.index[t])
            in_index = np.array([tk in members for tk in tickers])
            elig = np.array([j for j in elig if in_index[j]], dtype=int)
            listed = listed & in_index
            coverage.append((P.index[t], len(members), int(listed.sum())))
        # TERCILE s'applique au nombre de titres REELLEMENT dans l'univers a
        # cette date (identique a l'origine quand membership_fn is None).
        n_ref = n_tickers if membership_fn is None else len(elig)
        n_top = max(1, int(round(n_ref * TERCILE)))
        n_top_t = min(n_top, len(elig))
        if n_top_t > 0:
            top_idx = elig[np.argsort(-s[elig])[:n_top_t]]  # les PLUS HAUTS rendements (winners)
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top_t
            weights_winners[t:end] = w
        if listed.sum() > 0:
            weights_bh[t:end] = listed.astype(float) / listed.sum()

    if causal:
        weights_winners = lag_one_day(weights_winners)
        weights_bh = lag_one_day(weights_bh)

    pnl_w = (weights_winners[start:] * R_safe[start:]).sum(axis=1)
    pnl_b = (weights_bh[start:] * R_safe[start:]).sum(axis=1)
    turn_w = np.abs(np.diff(weights_winners[start:], axis=0, prepend=weights_winners[start:start+1])).sum(axis=1) / 2.0
    turn_b = np.abs(np.diff(weights_bh[start:], axis=0, prepend=weights_bh[start:start+1])).sum(axis=1) / 2.0
    pnl_w = pnl_w - turn_w * (COST_BPS / 1e4)
    pnl_b = pnl_b - turn_b * (COST_BPS / 1e4)

    me_w, me_b = trading_metrics(pnl_w), trading_metrics(pnl_b)
    equity_w = np.cumprod(1.0 + pnl_w)
    equity_b = np.cumprod(1.0 + pnl_b)
    ret_w, ret_b = equity_w[-1] - 1.0, equity_b[-1] - 1.0

    sharpe_ok = me_w["sharpe_ann"] > me_b["sharpe_ann"]
    ret_ok = ret_w > ret_b
    verdict = sharpe_ok and ret_ok

    lines = [
        "# Résultat — Momentum court terme, 1 semaine, winners (pré-enregistré, règle renforcée)",
        "",
        f"Univers : {n_tickers} tickers NDX-100, {T - start} séances testables "
        f"({P.index[start].date()} → {P.index[-1].date()}), signal = rendement 5j, "
        f"rebalancement hebdomadaire, tercile SUPÉRIEUR ({n_top} titres).",
        "",
        *( [header_note, ""] if header_note else [] ),
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold équipondéré (univers) | {me_b['sharpe_ann']:+.2f} | {100*ret_b:+.1f}% | "
        f"{me_b['max_drawdown_pct']:.1f}% |",
        f"| **Winners (tercile sup., momentum)** | **{me_w['sharpe_ann']:+.2f}** | "
        f"**{100*ret_w:+.1f}%** | {me_w['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe winners > Buy&Hold : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement total winners > Buy&Hold : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé (Sharpe ET rendement) "
        f"{'atteint' if verdict else 'NON atteint'}.**",
        "",
        "**Comparaison directe avec le cycle #5** (même signal, même univers, tercile "
        "opposé) : à mettre en regard de `results/nonml_short_term_reversal_result.md` "
        "(losers : Sharpe -1.02, rendement -83.6%).",
    ]

    if coverage:
        cov = pd.DataFrame(coverage, columns=["date", "membres", "investissables"])
        cov["couverture"] = cov["investissables"] / cov["membres"]
        cov["annee"] = pd.to_datetime(cov["date"]).dt.year
        lines += ["", "## Biais résiduel de l'univers point-in-time (mesuré, non estimé)", "",
                  "| Année | Rebal. | Membres réels (moy.) | Investissables (moy.) | Couverture moy. |",
                  "|---|---|---|---|---|"]
        for year, g in cov.groupby("annee"):
            lines.append(f"| {year} | {len(g)} | {g['membres'].mean():.0f} | "
                         f"{g['investissables'].mean():.1f} | {100*g['couverture'].mean():.1f}% |")
        lines += ["", f"**Couverture moyenne : {100*cov['couverture'].mean():.1f}% "
                  f"(minimum {100*cov['couverture'].min():.1f}%)**, contre 42-68 % pour la liste "
                  "de 2026 appliquée rétroactivement (cf. `results/nonml_ndx100_universe_census.md`). "
                  "Le résidu correspond aux sociétés retirées de la cote dont la série de prix "
                  "n'est plus exposée par la source — biais restant orienté à la hausse, mais "
                  "réduit d'un ordre de grandeur et mesuré.", ""]

    out = ROOT / "results" / f"nonml_short_term_momentum_result{out_suffix}.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


PIT_NOTE = (
    "**Univers POINT-IN-TIME (cycle #164)** — à chaque rebalancement, seuls les titres "
    "réellement membres du NDX-100 ce jour-là sont éligibles, **et la référence "
    "équipondérée est construite sur ce même univers réel**. Corrige le biais du "
    "survivant qui affectait le #14 d'origine (liste des membres de 2026 appliquée "
    "rétroactivement, couverture 68 % en 2022 / 42 % en 2015 — cf. "
    "`results/nonml_ndx100_universe_census.md`). Aucun paramètre du #14 ne change "
    "(SIGNAL_WINDOW=5, REBAL_EVERY=5, TERCILE=1/3, coût 5 bps). Pré-enregistré dans "
    "`PREREG_short_term_momentum_pit_universe.md`."
)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--pit":
        sys.path.insert(0, str(ROOT / "scripts"))
        from ndx100_membership import tickers_as_of_date  # noqa: E402
        main(prices_dir=ROOT / "data" / "pead" / "prices_pit",
             panel_start="2014-01-01",
             membership_fn=tickers_as_of_date,
             rebal_anchor="2015-01-01",
             out_suffix="_pit_universe",
             header_note=PIT_NOTE)
    else:
        main()
