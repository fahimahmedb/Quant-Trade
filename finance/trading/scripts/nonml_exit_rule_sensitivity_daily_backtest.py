"""Backtest — Expérience C' : sensibilité de la Stratégie A à la règle de
sortie (spécification pré-enregistrée dans
PREREG_exit_rule_sensitivity_daily.md, committée avant ce script). Entrée
strictement identique à la Stratégie A (`nonml_daily_breakout_baseline_
backtest.py`) ; seule la sortie change, sur 6 variantes déclarées en bloc.
n_trials=6, correction DSR appliquée à chaque variante. Aucune dépendance
ML, aucun paramètre ajusté après résultat.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sstats

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import _rsi, _atr, trading_metrics, dsr  # noqa: E402

COST_BPS = 5.0
RISK_PCT = 0.005
SL_MULT = 1.5
SMA_WINDOW = 50
SMA20_WINDOW = 20
BREAKOUT_WINDOW = 20
RSI_LO, RSI_HI = 50.0, 75.0
INITIAL_CAPITAL = 5000.0
START = 55  # identique a la Strategie A (memes regles d'entree)
TIME_STOP_DAYS = 10
DSR_SEUIL = 0.95

DATA_PATH = REPO_ROOT / "data" / "nasdaq_composite_daily.txt"

VARIANTS = [
    ("TP=2R (référence A)", "fixed_tp", 2.0, None),
    ("TP=3R", "fixed_tp", 3.0, None),
    ("TP=4R", "fixed_tp", 4.0, None),
    ("Trailing stop (chandelier, pas de TP)", "trailing", None, None),
    ("Pas de TP, sortie rupture tendance (close<SMA20)", "trend_break", None, None),
    ("Time stop 10j (structure TP=2R)", "time_stop", 2.0, TIME_STOP_DAYS),
]


def compute_indicators(df: pd.DataFrame) -> dict:
    close = df["close"]
    high = df["high"]
    sma50 = close.rolling(SMA_WINDOW).mean()
    sma20 = close.rolling(SMA20_WINDOW).mean()
    breakout_level = high.rolling(BREAKOUT_WINDOW).max().shift(1)
    rsi14 = _rsi(close, 14)
    atr14 = _atr(df, 14)
    return {
        "sma50": sma50.values, "sma20": sma20.values,
        "breakout_level": breakout_level.values,
        "rsi14": rsi14.values, "atr14": atr14.values,
    }


def simulate(df: pd.DataFrame, ind: dict, exit_mode: str,
             tp_r: float | None, time_stop_days: int | None) -> dict:
    open_ = df["open"].values
    high = df["high"].values
    low = df["low"].values
    close = df["close"].values
    n = len(df)

    sma50, sma20, breakout_level, rsi14, atr14 = (
        ind["sma50"], ind["sma20"], ind["breakout_level"], ind["rsi14"], ind["atr14"]
    )

    equity = np.empty(n)
    equity[:START] = INITIAL_CAPITAL
    in_position_mask = np.zeros(n, dtype=bool)

    cash = INITIAL_CAPITAL
    pos = None
    pending_entry = False
    trades = []

    for t in range(START, n):
        equity_before = cash if pos is None else cash + pos["units"] * close[t - 1]

        if pending_entry and pos is None:
            entry_price = open_[t]
            entry_atr = pending_entry_atr
            stop = entry_price - SL_MULT * entry_atr
            tp = entry_price + tp_r * SL_MULT * entry_atr if tp_r is not None else None
            risk_amount = RISK_PCT * equity_before
            risk_per_unit = entry_price - stop
            units = risk_amount / risk_per_unit if risk_per_unit > 0 else 0.0
            notional_entry = units * entry_price
            cost_entry = notional_entry * (COST_BPS / 1e4)
            cash -= notional_entry + cost_entry
            pos = {
                "entry_idx": t, "entry_price": entry_price, "stop": stop,
                "tp": tp, "units": units, "entry_atr": entry_atr,
                "cost_entry": cost_entry, "notional_entry": notional_entry,
                "hh_since_entry": -np.inf,
            }
            pending_entry = False

        if pos is not None:
            in_position_mask[t] = True
            if exit_mode == "trailing" and pos["hh_since_entry"] > -np.inf:
                eff_stop = max(pos["stop"], pos["hh_since_entry"] - SL_MULT * pos["entry_atr"])
            else:
                eff_stop = pos["stop"]

            hit_sl = low[t] <= eff_stop
            hit_tp = (pos["tp"] is not None) and (high[t] >= pos["tp"])
            exit_price, exit_reason = None, None
            if hit_sl and hit_tp:
                exit_price, exit_reason = eff_stop, "SL"
            elif hit_sl:
                exit_price, exit_reason = eff_stop, "SL"
            elif hit_tp:
                exit_price, exit_reason = pos["tp"], "TP"
            elif exit_mode == "trend_break" and close[t] < sma20[t]:
                exit_price, exit_reason = close[t], "TREND_BREAK"
            elif exit_mode == "time_stop" and (t - pos["entry_idx"]) >= time_stop_days:
                exit_price, exit_reason = close[t], "TIME_STOP"

            if exit_price is not None:
                notional_exit = pos["units"] * exit_price
                cost_exit = notional_exit * (COST_BPS / 1e4)
                proceeds = notional_exit - cost_exit
                cash += proceeds
                pnl = proceeds - pos["notional_entry"] - pos["cost_entry"]
                r_multiple = (exit_price - pos["entry_price"]) / (pos["entry_price"] - pos["stop"])
                trades.append({
                    "entry_idx": pos["entry_idx"], "exit_idx": t,
                    "entry_price": pos["entry_price"], "exit_price": exit_price,
                    "units": pos["units"], "pnl": pnl, "r_multiple": r_multiple,
                    "reason": exit_reason, "holding_days": t - pos["entry_idx"],
                })
                pos = None
            else:
                if exit_mode == "trailing":
                    pos["hh_since_entry"] = max(pos["hh_since_entry"], high[t])

        if pos is None:
            signal = (
                close[t] > sma50[t]
                and close[t] > breakout_level[t]
                and RSI_LO <= rsi14[t] <= RSI_HI
                and not np.isnan(sma50[t]) and not np.isnan(breakout_level[t])
            )
            if signal and t + 1 < n:
                pending_entry = True
                pending_entry_atr = atr14[t]

        equity[t] = cash if pos is None else cash + pos["units"] * close[t]

    open_at_end = pos is not None
    return {
        "equity": equity, "trades": trades,
        "in_position_mask": in_position_mask, "open_at_end": open_at_end,
    }


def buy_hold_returns(close: np.ndarray, start: int) -> np.ndarray:
    close_t = close[start - 1:]
    r = np.log(close_t[1:] / close_t[:-1])
    r[0] -= COST_BPS / 1e4
    return r


def main():
    df = load_ohlc(str(DATA_PATH))
    quality_report(df)
    ind = compute_indicators(df)
    close = df["close"].values
    bh_ret_full = buy_hold_returns(close, START)

    results = []
    for name, mode, tp_r, tsd in VARIANTS:
        sim = simulate(df, ind, mode, tp_r, tsd)
        equity = sim["equity"][START:]
        strat_ret = np.diff(np.log(equity))
        n_common = min(len(strat_ret), len(bh_ret_full))
        strat_ret = strat_ret[:n_common]
        bh_ret = bh_ret_full[:n_common]

        me_strat = trading_metrics(strat_ret)
        me_bh = trading_metrics(bh_ret)
        ret_strat = float(equity[-1] / equity[0] - 1.0)
        ret_bh = float(np.exp(bh_ret.sum()) - 1.0)
        sharpe_ok = me_strat["sharpe_ann"] > me_bh["sharpe_ann"]
        ret_ok = ret_strat > ret_bh
        verdict = sharpe_ok and ret_ok

        trades = sim["trades"]
        n_trades = len(trades)
        wins = [tr for tr in trades if tr["pnl"] > 0]
        hit_rate = len(wins) / n_trades if n_trades else float("nan")
        avg_r = float(np.mean([tr["r_multiple"] for tr in trades])) if n_trades else float("nan")

        sr_daily = float(strat_ret.mean() / strat_ret.std()) if strat_ret.std() > 0 else 0.0
        skew = float(sstats.skew(strat_ret))
        kurt = float(sstats.kurtosis(strat_ret))  # excess

        results.append({
            "name": name, "n_trades": n_trades, "hit_rate": hit_rate, "avg_r": avg_r,
            "sharpe_ann": me_strat["sharpe_ann"], "ret_pct": 100 * ret_strat,
            "mdd_pct": me_strat["max_drawdown_pct"], "bh_sharpe": me_bh["sharpe_ann"],
            "bh_ret_pct": 100 * ret_bh, "sharpe_ok": sharpe_ok, "ret_ok": ret_ok,
            "verdict": verdict, "sr_daily": sr_daily, "skew": skew, "kurt": kurt,
            "T": n_common,
        })

    sr_family = np.array([r["sr_daily"] for r in results])
    var_trials = float(sr_family.var(ddof=1))
    n_trials = len(results)
    for r in results:
        d = dsr(r["sr_daily"], r["T"], var_trials, n_trials, r["skew"], r["kurt"])
        r["dsr"] = d["dsr"]

    lines = [
        "# Résultat — Expérience C' : sensibilité de la Stratégie A à la règle de sortie",
        "",
        "Entrée identique à la Stratégie A (close>SMA50, breakout 20j, RSI14∈[50,75], "
        f"entrée open(t+1)), Composite pré-enregistré, {results[0]['T']} séances testables "
        f"(à partir de la {START+1}e). Seule la sortie change, 6 variantes, n_trials=6, "
        f"DSR appliqué (seuil {DSR_SEUIL}).",
        "",
        "| Variante | Trades | Hit rate | R moyen | Sharpe | Rdt total | MDD | Sharpe>BH | Rdt>BH | PASS naïf | DSR |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        hr = f"{100*r['hit_rate']:.1f}%" if not np.isnan(r["hit_rate"]) else "N/A"
        ar = f"{r['avg_r']:+.2f}R" if not np.isnan(r["avg_r"]) else "N/A"
        lines.append(
            f"| {r['name']} | {r['n_trades']} | {hr} | {ar} | {r['sharpe_ann']:+.2f} | "
            f"{r['ret_pct']:+.1f}% | {r['mdd_pct']:.1f}% | {'OUI' if r['sharpe_ok'] else 'non'} | "
            f"{'OUI' if r['ret_ok'] else 'non'} | {'PASS' if r['verdict'] else 'FAIL'} | {r['dsr']:.3f} |"
        )

    lines.append("")
    lines.append(f"Référence Buy & Hold sur le même échantillon : Sharpe {results[0]['bh_sharpe']:+.2f}, "
                 f"rendement total {results[0]['bh_ret_pct']:+.1f}%.")
    lines.append("")

    n_pass_naif = sum(1 for r in results if r["verdict"])
    n_pass_dsr = sum(1 for r in results if r["verdict"] and r["dsr"] > DSR_SEUIL)
    lines.append(f"**{n_pass_naif}/6 variantes PASS naïf (bat B&H en Sharpe ET rendement) ; "
                 f"{n_pass_dsr}/6 PASS naïf ET DSR>{DSR_SEUIL}.**")
    lines.append("")
    if n_pass_dsr > 0:
        lines.append("**Réponse à la question posée : NON, ce n'est pas (uniquement) le "
                     "take-profit court qui tue la stratégie** — au moins une variante de "
                     "sortie élargie/adaptative passe le critère renforcé ET le seuil DSR "
                     "(voir tableau).")
    elif n_pass_naif > 0:
        lines.append("**Réponse à la question posée : partiellement** — au moins une variante "
                     "bat B&H naïvement, mais aucune ne résiste à la correction DSR à "
                     f"n_trials=6 (DSR≤{DSR_SEUIL}) : impossible de distinguer un vrai edge "
                     "d'un artefact de sélection sur 6 essais.")
    else:
        lines.append("**Réponse à la question posée : NON** — aucune des 6 variantes de sortie "
                     "(TP élargi, trailing, rupture de tendance, time stop) ne bat Buy & Hold "
                     "simultanément en Sharpe et en rendement sur cet échantillon. Le "
                     "take-profit court (2R) n'est pas le facteur limitant identifiable : "
                     "élargir ou supprimer le TP ne suffit pas à transformer la Stratégie A "
                     "en signal profitable net de coûts. Cohérent avec la conclusion déjà "
                     "établie du repo (aucun signal actif testé ne bat B&H sur le Composite).")

    out = ROOT / "results" / "nonml_exit_rule_sensitivity_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
