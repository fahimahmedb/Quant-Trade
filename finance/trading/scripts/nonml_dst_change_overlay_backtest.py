"""Backtest — Effet du changement d'heure DST (Kamstra, Kramer & Levi
2000, "Losing Sleep at the Market"), overlay défensif (spécification
pré-enregistrée dans PREREG_dst_change_overlay.md, committée avant ce
script). n_trials=1, aucune dépendance ML. Règle de succès renforcée
sur 5 marchés (≥4/5).

Règles de changement d'heure sourcées AVANT tout calcul (voir PREREG
pour les références légales complètes) : succession de 4 règles US
1970-2006 (+ exceptions 1974/1975) puis règle 2007+, et règle UE
harmonisée depuis 1996 pour DAX. Aucune donnée externe.
"""
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402

COST_BPS = 5.0
CUT = 0.5

MARKETS = {
    "Composite (5 ans)": ("nasdaq_composite_daily.txt", "US"),
    "NDX (40 ans)": ("nasdaq100_daily.txt", "US"),
    "Russell 2000": ("russell2000_daily.txt", "US"),
    "S&P 500": ("sp500_daily.txt", "US"),
    "DAX": ("dax_daily.txt", "EU"),
}

SUNDAY = 6  # date.weekday() : lundi=0 ... dimanche=6


def nth_sunday(year: int, month: int, n: int) -> date:
    d = date(year, month, 1)
    offset = (SUNDAY - d.weekday()) % 7
    first_sunday = d + timedelta(days=offset)
    return first_sunday + timedelta(days=7 * (n - 1))


def last_sunday(year: int, month: int) -> date:
    if month == 12:
        next_month_first = date(year + 1, 1, 1)
    else:
        next_month_first = date(year, month + 1, 1)
    d = next_month_first - timedelta(days=1)
    offset = (d.weekday() - SUNDAY) % 7
    return d - timedelta(days=offset)


def us_dst_dates(year: int) -> tuple[date, date]:
    """Regles officielles US, sourcees AVANT calcul (voir PREREG)."""
    if year == 1974:
        return date(1974, 1, 6), date(1974, 10, 27)
    if year == 1975:
        return date(1975, 2, 23), date(1975, 10, 26)
    if 1970 <= year <= 1986:
        return last_sunday(year, 4), last_sunday(year, 10)
    if 1987 <= year <= 2006:
        return nth_sunday(year, 4, 1), last_sunday(year, 10)
    return nth_sunday(year, 3, 2), nth_sunday(year, 11, 1)


def eu_dst_dates(year: int) -> tuple[date, date]:
    """Regle UE harmonisee depuis 1996 (voir PREREG) -- DAX commence en 1999, toujours applicable."""
    return last_sunday(year, 3), last_sunday(year, 10)


def dst_monday_mask(dates: pd.DatetimeIndex, region: str) -> np.ndarray:
    """True le PREMIER jour de bourse strictement posterieur a chaque
    dimanche de transition DST (printemps ou automne), data-driven a
    partir du calendrier de bourse reel (pas juste 'le lundi' -- gere
    les jours feries qui decalent le premier jour ouvre)."""
    years = sorted(set(dates.year))
    transition_sundays = []
    for y in years:
        fn = us_dst_dates if region == "US" else eu_dst_dates
        spring, fall = fn(y)
        transition_sundays.append(spring)
        transition_sundays.append(fall)
    # inclut aussi l'annee precedente/suivante pour les transitions a cheval sur les bornes
    for y in [min(years) - 1, max(years) + 1]:
        fn = us_dst_dates if region == "US" else eu_dst_dates
        spring, fall = fn(y)
        transition_sundays.append(spring)
        transition_sundays.append(fall)

    dates_np = dates.values.astype("datetime64[D]")
    mask = np.zeros(len(dates), dtype=bool)
    for sunday in transition_sundays:
        sunday_np = np.datetime64(sunday)
        after = dates_np > sunday_np
        if after.any():
            idx = int(np.argmax(after))  # premier True (dates triees croissant)
            mask[idx] = True
    return mask


def main():
    lines = [
        "# Résultat — Effet du changement d'heure DST, overlay défensif (pré-enregistré)",
        "",
        f"`position(t) = {CUT}x` le premier jour de bourse suivant chaque transition DST "
        f"(printemps et automne, règles US ou UE selon le marché), `1.0x` sinon. Coûts {COST_BPS:.0f} bps.",
        "",
        "| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    n_markets, n_success = 0, 0

    for name, (fname, region) in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        dates = pd.DatetimeIndex(df["date"].values)
        bh_full = np.log(close[1:] / close[:-1])

        mask_full = dst_monday_mask(dates, region)
        mask = mask_full[:-1]
        assert len(mask) == len(bh_full)

        pos = np.where(mask, CUT, 1.0)
        frac_cut = float(mask.mean())

        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl_ov = pos * bh_full - turn * (COST_BPS / 1e4)
        pnl_bh = bh_full.copy()
        pnl_bh[0] -= COST_BPS / 1e4

        me_bh = trading_metrics(pnl_bh)
        me_ov = trading_metrics(pnl_ov)
        ret_bh = np.exp(pnl_bh.sum()) - 1.0
        ret_ov = np.exp(pnl_ov.sum()) - 1.0

        sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
        ret_ok = ret_ov > ret_bh
        n_markets += 1
        n_success += int(sharpe_ok and ret_ok)

        lines.append(
            f"| {name} | {len(bh_full)} | {100*frac_cut:.2f}% | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | "
            f"{me_bh['max_drawdown_pct']:.1f}% | {me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | "
            f"{me_ov['max_drawdown_pct']:.1f}% | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

        if name == "NDX (40 ans)":
            dates_pnl = dates.values[1:]
            np.savez(ROOT / "results" / "nonml_dst_change_overlay_pnl.npz",
                     pos=pos, r_asset=bh_full, dates=dates_pnl, cost_bps=COST_BPS)

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_dst_change_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
