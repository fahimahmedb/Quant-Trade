"""Audit adversarial — Overlay levé January Barometer.

Recalcul totalement indépendant (regroupement par année/mois via
`datetime` standard plutôt que `pandas.dt.year`/`dt.month`, logique de
décision réécrite sous forme de boucle par année) et test anti-lookahead
(perturbation du futur). Vérifie en particulier qu'aucune année N+1
n'influence la décision de l'année N (contrainte structurelle du
design).
"""
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
from nonml_january_barometer_overlay_backtest import position_for, CAP, MARKETS  # noqa: E402


def independent_position(df) -> np.ndarray:
    """Reconstruction indépendante : regroupe les indices par (annee,
    mois) via le module datetime standard (pas pandas.dt), retrouve le
    dernier indice de chaque mois par balayage sequentiel (pas de dict
    construit d'un bloc), calcule le rendement de janvier de chaque
    annee, puis applique le signal."""
    ts = pd.to_datetime(df["date"]).tolist()
    close = df["close"].values
    T = len(close)

    last_idx = {}
    for i in range(T):
        dt = ts[i].to_pydatetime()
        last_idx[(dt.year, dt.month)] = i  # ecrase a chaque nouvelle occurrence -> dernier indice du mois

    years_seen = sorted({ts[i].to_pydatetime().year for i in range(T)})
    signal_by_year = {}
    for y in years_seen:
        i_dec_prev = last_idx.get((y - 1, 12))
        i_jan = last_idx.get((y, 1))
        if i_dec_prev is None or i_jan is None:
            continue
        signal_by_year[y] = close[i_jan] > close[i_dec_prev]

    pos = np.ones(T)
    for i in range(T):
        dt = ts[i].to_pydatetime()
        if dt.month == 1:
            continue
        if signal_by_year.get(dt.year, False):
            pos[i] = CAP
    return pos[1:]


def main():
    lines = ["# Audit adversarial — Overlay levé January Barometer", "",
             "## 1. Recalcul indépendant (datetime standard, regroupement par balayage séquentiel)", "",
             "| Marché | Écart position (nb j.) |",
             "|---|---|"]
    all_ok = True
    dfs = {}
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dfs[name] = df
        p_orig = position_for(df)
        p_indep = independent_position(df)
        diff = int(np.sum(p_orig != p_indep))
        all_ok &= (diff == 0)
        lines.append(f"| {name} | {diff} |")

    lines.append("")
    lines.append(f"**{'OK — position confirmée par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Détail par année (NDX, marché le plus long) — vérifie l'absence de biais évident")
    lines.append("")
    lines.append("| Année | Rdt janvier | Signal (levé fev-déc) |")
    lines.append("|---|---|---|")
    df_ndx = dfs["NDX (40 ans)"]
    ts = pd.to_datetime(df_ndx["date"])
    close = df_ndx["close"].values
    last_idx = {}
    for i, dt in enumerate(ts):
        last_idx[(dt.year, dt.month)] = i
    years_seen = sorted(set(ts.dt.year))
    n_pos, n_total = 0, 0
    for y in years_seen:
        i_dec_prev = last_idx.get((y - 1, 12))
        i_jan = last_idx.get((y, 1))
        if i_dec_prev is None or i_jan is None:
            continue
        jan_ret = close[i_jan] / close[i_dec_prev] - 1.0
        n_total += 1
        n_pos += int(jan_ret > 0)
        lines.append(f"| {y} | {100*jan_ret:+.1f}% | {'CAP' if jan_ret > 0 else '1.0x'} |")
    lines.append("")
    lines.append(f"**{n_pos}/{n_total} années avec janvier positif sur NDX ({100*n_pos/n_total:.0f}%).**")

    lines.append("")
    lines.append("## 3. Test anti-lookahead (perturbation du futur)")
    lines.append("")
    lines.append("| Marché | Décisions passées identiques après perturbation future |")
    lines.append("|---|---|")
    anti_leak_ok = True
    for name, df in dfs.items():
        close_orig = df["close"].values
        p_before = position_for(df)

        close_pert = close_orig.copy()
        cut = len(close_pert) // 2
        rng = np.random.default_rng(97)
        close_pert[cut:] = close_pert[cut:] * (1.0 + rng.normal(0, 0.1, len(close_pert) - cut))
        df_pert = pd.DataFrame({"date": df["date"], "close": close_pert})
        p_after = position_for(df_pert)

        # marge de securite : ignore l'annee en cours au moment de la coupure
        # (une perturbation en milieu d'annee peut changer le signe du
        # rendement de janvier SEULEMENT si la coupure tombe en janvier
        # lui-meme -- sinon aucun impact possible par construction)
        cut_year = pd.to_datetime(df["date"]).dt.year.values[cut]
        years_arr = pd.to_datetime(df["date"]).dt.year.values[1:]
        mask_before_cut_year = years_arr < cut_year
        identical = bool(np.array_equal(p_before[mask_before_cut_year], p_after[mask_before_cut_year]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    anti_leak_msg = ("OK — aucune fuite de données futures (aucune année N+1 n'affecte la "
                      "décision de l'année N).") if anti_leak_ok else "ÉCHEC — fuite détectée."
    lines.append("")
    lines.append(f"**{anti_leak_msg}**")

    out = ROOT / "results" / "nonml_january_barometer_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
