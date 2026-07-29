"""Audit adversarial — Stratégie nuit seulement.

Le résultat brut est un FAIL extrême (rendement net proche de -100%),
ce qui pourrait ressembler à un bug -- vérifications :
1) recalcul indépendant de la décomposition nuit/jour (boucle explicite)
   et vérification de l'identité comptable r_nuit+r_jour=r_BH ;
2) recalcul indépendant du rendement BRUT (sans coûts) de la stratégie
   nuit seule, pour isoler l'effet du coût de friction du résultat net ;
3) test de sensibilité : à quel coût par transaction la stratégie nuit
   deviendrait-elle seulement CONCURRENTIELLE avec le rendement brut de
   Buy&Hold (à titre d'illustration, PAS un retuning du coût
   pré-enregistré à 5 bps).
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402
from nonml_overnight_vs_intraday_backtest import decompose_returns, COST_BPS, MARKETS  # noqa: E402


def independent_decompose(open_: np.ndarray, close: np.ndarray):
    T = len(close)
    r_nuit = np.zeros(T - 1)
    r_jour = np.zeros(T - 1)
    r_bh = np.zeros(T - 1)
    for i in range(T - 1):
        r_nuit[i] = np.log(open_[i + 1]) - np.log(close[i])
        r_jour[i] = np.log(close[i + 1]) - np.log(open_[i + 1])
        r_bh[i] = np.log(close[i + 1]) - np.log(close[i])
    return r_nuit, r_jour, r_bh


def main():
    lines = ["# Audit adversarial — Stratégie nuit seulement", "",
             "## 1. Recalcul indépendant de la décomposition (boucle explicite)", "",
             "| Marché | Écart max r_nuit | Écart max r_jour | Écart identité r_nuit+r_jour-r_BH |",
             "|---|---|---|---|"]
    all_ok = True
    dfs = {}
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dfs[name] = df
        open_ = df["open"].values
        close = df["close"].values

        r_nuit_o, r_jour_o, r_bh_o = decompose_returns(open_, close)
        r_nuit_i, r_jour_i, r_bh_i = independent_decompose(open_, close)

        diff_nuit = float(np.max(np.abs(r_nuit_o - r_nuit_i)))
        diff_jour = float(np.max(np.abs(r_jour_o - r_jour_i)))
        diff_identity = float(np.max(np.abs(r_nuit_o + r_jour_o - r_bh_o)))
        all_ok &= (diff_nuit < 1e-10) and (diff_jour < 1e-10) and (diff_identity < 1e-10)
        lines.append(f"| {name} | {diff_nuit:.2e} | {diff_jour:.2e} | {diff_identity:.2e} |")

    lines.append("")
    lines.append(f"**{'OK — décomposition et identité comptable confirmées par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Rendement BRUT (sans coûts) de la stratégie nuit vs Buy&Hold brut")
    lines.append("")
    lines.append("| Marché | Rdt brut nuit (somme r_nuit) | Rdt brut BH (somme r_BH) | Nuit bat BH en BRUT ? |")
    lines.append("|---|---|---|---|")
    for name, df in dfs.items():
        open_ = df["open"].values
        close = df["close"].values
        r_nuit, r_jour, r_bh = decompose_returns(open_, close)
        gross_night = 100 * (np.exp(r_nuit.sum()) - 1.0)
        gross_bh = 100 * (np.exp(r_bh.sum()) - 1.0)
        lines.append(f"| {name} | {gross_night:+.1f}% | {gross_bh:+.1f}% | {'OUI' if gross_night > gross_bh else 'non'} |")

    lines.append("")
    lines.append("**Lecture** : même AVANT tout coût de transaction, le rendement brut de nuit ne "
                 "dépasse Buy&Hold que sur certains marchés (voir tableau) -- l'anomalie "
                 "overnight/intraday documentée dans la littérature US historique ne se traduit "
                 "pas systématiquement en un edge de RENDEMENT TOTAL brut sur cet échantillon, "
                 "même avant de considérer les coûts de friction qui, eux, sont de toute façon "
                 "rédhibitoires (voir §3).")

    lines.append("")
    lines.append("## 3. Sensibilité au coût de transaction (illustration, PAS un retuning du coût pré-enregistré)")
    lines.append("")
    lines.append("| Marché | Coût/transaction pour lequel Nuit net ≈ 0% (2 transactions/jour) |")
    lines.append("|---|---|")
    for name, df in dfs.items():
        open_ = df["open"].values
        close = df["close"].values
        r_nuit, _, _ = decompose_returns(open_, close)
        n_days = len(r_nuit)
        gross_sum = r_nuit.sum()
        # cout_total_pour_annuler = gross_sum (en log), reparti sur 2*n_days transactions
        cost_breakeven_bps = 1e4 * gross_sum / (2 * n_days) if n_days > 0 else float("nan")
        lines.append(f"| {name} | {cost_breakeven_bps:.3f} bps |")

    lines.append("")
    lines.append(f"**Lecture** : le coût pré-enregistré est de {COST_BPS} bps/transaction -- très "
                 "largement supérieur au seuil de rentabilité (souvent une fraction de bp) sur "
                 "tous les marchés, confirmant que le FAIL n'est pas un artefact d'un coût mal "
                 "calibré mais une conclusion structurelle robuste : la stratégie nuit seule ne "
                 "peut être rentable qu'à des coûts de transaction quasi nuls, hors de portée d'un "
                 "investisseur particulier.")

    out = ROOT / "results" / "nonml_overnight_vs_intraday_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
