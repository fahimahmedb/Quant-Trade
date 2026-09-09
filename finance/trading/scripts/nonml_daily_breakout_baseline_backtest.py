"""Backtest — Stratégie A : Daily Breakout (baseline, trades discrets)
(spécification pré-enregistrée dans PREREG_daily_breakout_baseline.md,
committée avant ce script). Moteur de simulation trade-par-trade (entrée
/ stop / cible), différent des overlays à exposition continue du reste
du backlog. n_trials=1, aucune dépendance ML, aucun paramètre ajusté
après résultat.
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

COST_BPS = 5.0  # par transition (entrée, sortie) — ajout méthodologique, cf. PREREG
RISK_PCT = 0.005  # 0.5% de l'equity courante par trade
SL_MULT = 1.5
TP_MULT = 3.0
SMA_WINDOW = 50
BREAKOUT_WINDOW = 20
RSI_LO, RSI_HI = 50.0, 75.0
INITIAL_CAPITAL = 5000.0
START = 55  # 50 SMA + marge de securite, cf. PREREG

DATA_PATH = REPO_ROOT / "data" / "nasdaq_composite_daily.txt"


def compute_indicators(df: pd.DataFrame) -> dict:
    close = df["close"]
    high = df["high"]
    sma50 = close.rolling(SMA_WINDOW).mean()
    breakout_level = high.rolling(BREAKOUT_WINDOW).max().shift(1)
    rsi14 = _rsi(close, 14)
    atr14 = _atr(df, 14)
    return {
        "sma50": sma50.values,
        "breakout_level": breakout_level.values,
        "rsi14": rsi14.values,
        "atr14": atr14.values,
    }


def simulate(df: pd.DataFrame, ind: dict) -> dict:
    """Simulation jour par jour, état = position ouverte ou non.

    Retourne l'equity quotidienne (mark-to-market), la liste des trades,
    et le masque des jours en position.
    """
    open_ = df["open"].values
    high = df["high"].values
    low = df["low"].values
    close = df["close"].values
    n = len(df)

    sma50, breakout_level, rsi14, atr14 = (
        ind["sma50"], ind["breakout_level"], ind["rsi14"], ind["atr14"]
    )

    equity = np.empty(n)
    equity[:START] = INITIAL_CAPITAL
    in_position_mask = np.zeros(n, dtype=bool)

    cash = INITIAL_CAPITAL
    pos = None  # dict: entry_idx, entry_price, stop, tp, units
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

    # position ouverte en fin d'echantillon : deja marquee au marche ci-dessus
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
    sim = simulate(df, ind)

    equity = sim["equity"][START:]
    strat_ret = np.diff(np.log(equity))
    close = df["close"].values
    bh_ret = buy_hold_returns(close, START)
    # aligner les longueurs (equity a START..n-1 -> diff = n-1-START valeurs; bh identique)
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

    lines = [
        "# Résultat — Stratégie A : Daily Breakout (baseline, pré-enregistré)",
        "",
        f"Composite (5 ans), {n_common} séances testables (à partir de la {START+1}e). "
        f"Long only, entrée open(t+1) si close>SMA50 ET breakout 20j (high, décalé 1j) "
        f"ET RSI14∈[{RSI_LO:.0f},{RSI_HI:.0f}]. Stop={SL_MULT}×ATR14, TP={TP_MULT}×ATR14 (2R). "
        f"Risque {100*RISK_PCT:.1f}% equity/trade, coûts {COST_BPS:.0f}bps/transition, "
        f"capital initial {INITIAL_CAPITAL:.0f}€.",
        "",
        "## Résultat agrégé (net de coûts)",
        "",
        "| | Stratégie A | Buy & Hold |",
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
        f"- Sharpe A > Sharpe B&H : {'OUI' if sharpe_ok else 'non'}",
        f"- Rendement A > B&H : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
        f"{'atteint' if verdict else 'NON atteint'} (bat B&H simultanément en Sharpe ET rendement).**",
    ]

    out = ROOT / "results" / "nonml_daily_breakout_baseline_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
