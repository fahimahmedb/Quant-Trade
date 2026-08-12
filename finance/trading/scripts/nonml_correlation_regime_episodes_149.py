"""Comportement de #149 pendant les 21 épisodes historiques de corrélation
actions/obligations élevée (spécification pré-enregistrée dans
PREREG_correlation_regime_episodes_149.md, committée avant ce script). PAS
un nouveau cycle du backlog non-ML -- question de politique opérationnelle
Voie A.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from prediction import trading_metrics  # noqa: E402

COST_BPS = 5.0

EPISODES = [
    ("1985-12-30", "1986-06-05"), ("1986-09-11", "1986-12-08"), ("1986-12-16", "1987-01-30"),
    ("1987-04-08", "1987-08-12"), ("1987-08-31", "1987-10-16"), ("1988-02-23", "1988-04-12"),
    ("1988-04-14", "1989-08-03"), ("1990-05-01", "1991-01-04"), ("1991-02-14", "1991-05-02"),
    ("1991-06-05", "1991-07-15"), ("1993-07-01", "1993-08-23"), ("1994-02-23", "1994-07-18"),
    ("1994-08-11", "1994-12-06"), ("1996-08-01", "1996-11-08"), ("1997-08-22", "1997-10-15"),
    ("1999-08-11", "1999-11-22"), ("2021-03-03", "2021-07-16"), ("2022-10-04", "2022-11-03"),
    ("2022-11-10", "2023-01-23"), ("2023-11-02", "2023-12-26"), ("2026-05-04", "2026-07-13"),
]


def total_return_pct(pnl):
    # pnl est en rendements LOG : composition par exp(somme).
    return 100.0 * (np.exp(pnl[np.isfinite(pnl)].sum()) - 1.0)


def main():
    d = np.load(ROOT / "results" / "nonml_cash_rate_correction_defensive_vol_targeting_44_pnl.npz", allow_pickle=True)
    pos, r_asset, r_alt = d["pos"], d["r_asset"], d["r_alt"]
    dates = pd.to_datetime(d["dates"])

    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov_full = pos * r_asset + (1.0 - pos) * r_alt - turn * (COST_BPS / 1e4)
    pnl_bh_full = r_asset.copy()
    pnl_bh_full[0] -= COST_BPS / 1e4

    lines = [
        "# Comportement de #149 pendant les 21 épisodes historiques de corrélation élevée",
        "",
        "Spécification pré-enregistrée. Fenêtre de #149 : "
        f"{dates[0].date()} → {dates[-1].date()} ({len(dates)} séances).",
        "",
        "| Épisode | Séances couvertes | Sharpe overlay | Sharpe BH | MDD overlay | MDD BH | MDD overlay pire que BH |",
        "|---|---|---|---|---|---|---|",
    ]

    n_worse = 0
    n_covered = 0
    sharpe_diffs = []
    for d0, d1 in EPISODES:
        mask = (dates >= pd.Timestamp(d0)) & (dates <= pd.Timestamp(d1))
        n = int(mask.sum())
        if n < 5:
            lines.append(f"| {d0}→{d1} | {n} (hors couverture #149) | -- | -- | -- | -- | -- |")
            continue
        n_covered += 1
        m_ov = trading_metrics(pnl_ov_full[mask])
        m_bh = trading_metrics(pnl_bh_full[mask])
        worse = m_ov["max_drawdown_pct"] < m_bh["max_drawdown_pct"] - 1.0  # tolerance 1pt
        if worse:
            n_worse += 1
        sharpe_diffs.append(m_ov["sharpe_ann"] - m_bh["sharpe_ann"])
        lines.append(
            f"| {d0}→{d1} | {n} | {m_ov['sharpe_ann']:+.2f} | {m_bh['sharpe_ann']:+.2f} | "
            f"{m_ov['max_drawdown_pct']:.1f}% | {m_bh['max_drawdown_pct']:.1f}% | {'OUI' if worse else 'non'} |"
        )

    lines += [
        "",
        f"Épisodes couverts par la fenêtre de #149 : {n_covered}/21.",
        f"Épisodes où le MDD overlay est pire que BH : {n_worse}/{n_covered}.",
        f"Sharpe overlay - Sharpe BH médian sur ces épisodes : {np.median(sharpe_diffs):+.2f}.",
        "",
        (
            "**Le mécanisme reste défensif même pendant les épisodes de corrélation "
            "élevée (le portage protège indépendamment du timing de corrélation) : "
            "le kill-switch §3.2 est une précaution supplémentaire, pas une "
            "correction d'un comportement observé comme dangereux.**"
            if n_worse == 0 else
            f"**Le mécanisme devient contre-productif sur {n_worse}/{n_covered} épisodes "
            "de corrélation élevée -- le kill-switch §3.2 est justifié empiriquement, "
            "pas seulement par prudence théorique.**"
        ),
        "",
        "Ne change aucun verdict Règle 9 déjà rendu sur #149 (reste 3/5, SPA et DSR "
        "à n_trials=125 toujours en échec).",
    ]

    out = ROOT / "results" / "nonml_correlation_regime_episodes_149.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
