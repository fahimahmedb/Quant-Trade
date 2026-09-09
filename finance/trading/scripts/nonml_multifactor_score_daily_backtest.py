"""Backtest — Stratégie B : Score multi-facteurs /10 (daily, trades discrets)
(spécification pré-enregistrée dans PREREG_multifactor_score_daily.md,
committée avant ce script). Réutilise le même moteur d'exécution que la
Stratégie A (nonml_daily_breakout_baseline_backtest.py) pour une
comparaison A vs B directe : seule la génération du signal diffère.
n_trials=1, aucune dépendance ML, aucun paramètre ajusté après résultat.
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
from prediction import _rsi, _atr, trading_metrics  # noqa: E402

COST_BPS = 5.0
RISK_PCT = 0.005
SL_MULT = 1.5
TP_MULT = 3.0
SMA20_WINDOW = 20
SMA50_WINDOW = 50
SMA200_WINDOW = 200
BREAKOUT20_WINDOW = 20
BREAKOUT50_WINDOW = 50
MOMENTUM_WINDOW = 20
RSI_LO, RSI_HI = 50.0, 75.0
SCORE_THRESHOLD = 7
INITIAL_CAPITAL = 5000.0
START = 205  # SMA200 (facteur le plus long) + marge de securite, cf. PREREG

DATA_PATH = REPO_ROOT / "data" / "nasdaq_composite_daily.txt"


def compute_score(df: pd.DataFrame) -> dict:
    close = df["close"]
    high = df["high"]

    sma20 = close.rolling(SMA20_WINDOW).mean()
    sma50 = close.rolling(SMA50_WINDOW).mean()
    sma200 = close.rolling(SMA200_WINDOW).mean()
    breakout20 = high.rolling(BREAKOUT20_WINDOW).max().shift(1)
    breakout50 = high.rolling(BREAKOUT50_WINDOW).max().shift(1)
    rsi14 = _rsi(close, 14)
    atr14 = _atr(df, 14)
    close_prev = close.shift(1)
    close_mom = close.shift(MOMENTUM_WINDOW)

    f_trend1 = (close > sma50).astype(float)
    f_trend2 = (sma50 > sma200).astype(float)
    f_struct1 = (close > close_prev).astype(float)
    f_struct2 = (close > sma20).astype(float)
    f_brk20 = (close > breakout20).astype(float)
    f_brk50 = (close > breakout50).astype(float)
    f_volume = pd.Series(0.0, index=df.index)  # structurellement 0, cf. PREREG (pas de volume utilisable)
    f_rsi = ((rsi14 >= RSI_LO) & (rsi14 <= RSI_HI)).astype(float)
    f_mom = (close > close_mom).astype(float) * 2.0

    score = (
        f_trend1 + f_trend2 + f_struct1 + f_struct2
        + f_brk20 + f_brk50 + f_volume + f_rsi + f_mom
    )
    # NaN tant qu'un facteur necessaire n'est pas encore defini (amorcage)
    warm_mask = sma200.isna() | breakout50.isna() | rsi14.isna() | atr14.isna() | close_mom.isna()
    score = score.where(~warm_mask, np.nan)

    return {
        "score": score.values,
        "atr14": atr14.values,
    }


def simulate(df: pd.DataFrame, sig: dict) -> dict:
    open_ = df["open"].values
    high = df["high"].values
    low = df["low"].values
    close = df["close"].values
    n = len(df)

    score, atr14 = sig["score"], sig["atr14"]

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
            tp = entry_price + TP_MULT * entry_atr
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
            }
            pending_entry = False

        if pos is not None:
            in_position_mask[t] = True
            hit_sl = low[t] <= pos["stop"]
            hit_tp = high[t] >= pos["tp"]
            exit_price, exit_reason = None, None
            if hit_sl and hit_tp:
                exit_price, exit_reason = pos["stop"], "SL (priorité meme-jour)"
            elif hit_sl:
                exit_price, exit_reason = pos["stop"], "SL"
            elif hit_tp:
                exit_price, exit_reason = pos["tp"], "TP"

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
                    "reason": exit_reason,
                    "holding_days": t - pos["entry_idx"],
                })
                pos = None

        if pos is None:
            signal = (not np.isnan(score[t])) and score[t] >= SCORE_THRESHOLD
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
    sig = compute_score(df)
    sim = simulate(df, sig)

    equity = sim["equity"][START:]
    strat_ret = np.diff(np.log(equity))
    close = df["close"].values
    bh_ret = buy_hold_returns(close, START)
    n_common = min(len(strat_ret), len(bh_ret))
    strat_ret = strat_ret[:n_common]
    bh_ret = bh_ret[:n_common]

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
    losses = [tr for tr in trades if tr["pnl"] <= 0]
    hit_rate = len(wins) / n_trades if n_trades else float("nan")
    avg_r = float(np.mean([tr["r_multiple"] for tr in trades])) if n_trades else float("nan")
    gains = sum(tr["pnl"] for tr in wins)
    losses_sum = -sum(tr["pnl"] for tr in losses)
    profit_factor = gains / losses_sum if losses_sum > 0 else float("nan")
    n_sl = sum(1 for tr in trades if tr["reason"].startswith("SL"))
    n_tp = sum(1 for tr in trades if tr["reason"] == "TP")
    pct_in_position = float(sim["in_position_mask"][START:START + n_common].mean())

    score_valid = sig["score"][START:]
    score_valid = score_valid[~np.isnan(score_valid)]
    n_score6 = int((score_valid == 6).sum())
    n_score_ge8 = int((score_valid >= 8).sum())
    max_score_seen = float(np.nanmax(sig["score"][START:])) if len(score_valid) else float("nan")

    lines = [
        "# Résultat — Stratégie B : Score multi-facteurs /10 (daily, pré-enregistré)",
        "",
        f"Composite (5 ans), {n_common} séances testables (à partir de la {START+1}e, amorçage SMA200). "
        f"Long only, entrée open(t+1) si score(t)≥{SCORE_THRESHOLD}/10 (facteur Volume structurellement "
        f"toujours 0/1, cf. PREREG — score max atteignable = 9/10). Stop={SL_MULT}×ATR14, "
        f"TP={TP_MULT}×ATR14 (2R fixe, pas de BE ni trailing). Risque {100*RISK_PCT:.1f}% equity/trade, "
        f"coûts {COST_BPS:.0f}bps/transition, capital initial {INITIAL_CAPITAL:.0f}€.",
        "",
        "## Résultat agrégé (net de coûts)",
        "",
        "| | Stratégie B | Buy & Hold |",
        "|---|---|---|",
        f"| Sharpe annualisé | {me_strat['sharpe_ann']:+.2f} | {me_bh['sharpe_ann']:+.2f} |",
        f"| Rendement total | {100*ret_strat:+.1f}% | {100*ret_bh:+.1f}% |",
        f"| Max drawdown | {me_strat['max_drawdown_pct']:.1f}% | {me_bh['max_drawdown_pct']:.1f}% |",
        f"| Calmar | {me_strat['calmar']:.2f} | {me_bh['calmar']:.2f} |",
        f"| % jours en position | {100*pct_in_position:.1f}% | 100.0% |",
        "",
        "## Statistiques de trades",
        "",
        f"- Nombre de trades : **{n_trades}**",
        f"- Taux de réussite : {100*hit_rate:.1f}%" if n_trades else "- Taux de réussite : N/A (aucun trade)",
        f"- R moyen par trade : {avg_r:+.2f}R" if n_trades else "- R moyen par trade : N/A",
        f"- Profit factor : {profit_factor:.2f}" if n_trades and np.isfinite(profit_factor) else "- Profit factor : N/A",
        f"- Sorties stop / take-profit : {n_sl} / {n_tp}",
        f"- Position ouverte en fin d'échantillon : {'oui' if sim['open_at_end'] else 'non'}",
        "",
        "## Score — informations descriptives (non-décisionnelles)",
        "",
        f"- Score maximum observé sur l'échantillon : {max_score_seen:.0f}/10",
        f"- Séances à score=6 (setup faible, non tradées, seuil décisionnel = ≥7 uniquement) : {n_score6}",
        f"- Séances à score≥8 (signal très fort) : {n_score_ge8}",
        "",
        f"- Sharpe B > Sharpe B&H : {'OUI' if sharpe_ok else 'non'}",
        f"- Rendement B > B&H : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
        f"{'atteint' if verdict else 'NON atteint'} (bat B&H simultanément en Sharpe ET rendement, seuil ≥7/10).**",
    ]

    out = ROOT / "results" / "nonml_multifactor_score_daily_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
