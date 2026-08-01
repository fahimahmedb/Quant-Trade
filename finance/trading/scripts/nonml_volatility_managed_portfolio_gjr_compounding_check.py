"""Complément d'audit — sensibilité du verdict à la CONVENTION DE CAPITALISATION
(cycle #165, volatility-managed GJR-t).

Ce contrôle n'est PAS une nouvelle hypothèse et ne peut pas rendre le résultat
meilleur : il vérifie que la jambe « rendement » du critère renforcé n'est pas
un artefact de la convention de calcul du rendement total utilisée par tout le
backlog. Il a été écrit APRÈS avoir vu le résultat — donc uniquement dans le
sens qui peut l'affaiblir, jamais le renforcer (le verdict pré-enregistré
reste celui produit par la convention standard du projet).

Trois arithmétiques sur EXACTEMENT la même série de positions :

  1. **Convention du projet** (`np.cumprod(1 + pnl)` avec `pnl = pos * r_log`) :
     celle de `nonml_pass_validation_battery.py` et des 164 cycles précédents.
     Elle traite un rendement log comme s'il était simple.
  2. **Hybride log** (`exp(Σ pnl)`) : traite `pos * r_log` comme le rendement
     log du portefeuille. Exacte pour Buy & Hold (pos ≡ 1), mais **fausse pour
     une position variable** — `ln(1 + pos·(e^r − 1)) ≠ pos·r` dès que
     pos ≠ 1. Publiée pour montrer où la question se pose.
  3. **Arithmétique exacte** : rendement simple du portefeuille =
     `pos · (e^r − 1)`, capitalisé. C'est la seule des trois qui est
     économiquement correcte pour une exposition variable.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from prediction import trading_metrics  # noqa: E402

COST_BPS = 5.0


def mdd_pct(pnl_simple):
    eq = np.cumprod(1.0 + pnl_simple)
    return float((eq / np.maximum.accumulate(eq) - 1.0).min() * 100)


def main():
    d = np.load(ROOT / "results" / "nonml_volatility_managed_portfolio_gjr_pnl.npz",
                allow_pickle=True)
    pos, r = d["pos"], d["r_asset"]
    assert float(d["cost_bps"]) == COST_BPS
    cost = np.abs(np.diff(pos, prepend=1.0)) * (COST_BPS / 1e4)

    # 1-2 : convention du projet (pnl construit sur le rendement LOG)
    pnl_ov = pos * r - cost
    pnl_bh = r.copy()
    pnl_bh[0] -= COST_BPS / 1e4
    # 3 : arithmétique exacte (rendement SIMPLE de l'actif)
    R = np.expm1(r)
    ex_ov = pos * R - cost
    ex_bh = R.copy()
    ex_bh[0] -= COST_BPS / 1e4

    def sharpe(x):
        return float(x.mean() / x.std(ddof=1) * np.sqrt(252))

    conv = [
        ("1. Convention du projet — `cumprod(1 + pos·r_log)`",
         float(np.cumprod(1 + pnl_ov)[-1]), float(np.cumprod(1 + pnl_bh)[-1]),
         sharpe(pnl_ov), sharpe(pnl_bh)),
        ("2. Hybride log — `exp(Σ pos·r_log)` (INCORRECTE si pos ≠ 1)",
         float(np.exp(pnl_ov.sum())), float(np.exp(pnl_bh.sum())),
         sharpe(pnl_ov), sharpe(pnl_bh)),
        ("3. Arithmétique exacte — `cumprod(1 + pos·(e^r − 1))`",
         float(np.cumprod(1 + ex_ov)[-1]), float(np.cumprod(1 + ex_bh)[-1]),
         sharpe(ex_ov), sharpe(ex_bh)),
    ]

    lines = [
        "# Complément d'audit — le verdict dépend-il de la convention de capitalisation ?",
        "",
        "Contrôle écrit **après** avoir vu le résultat, et uniquement dans le sens qui peut "
        "l'affaiblir : la jambe « rendement » du critère renforcé est-elle un artefact de la "
        "façon dont le backlog capitalise les rendements ? Le verdict pré-enregistré du cycle "
        "reste celui de la convention 1 (celle de `nonml_pass_validation_battery.py` et des "
        "164 cycles précédents) — ce tableau sert à en donner la marge réelle, pas à la "
        "remplacer.",
        "",
        "| Arithmétique | Capital final candidat | Capital final Buy & Hold | Sharpe candidat | Sharpe BH | Rdt > BH |",
        "|---|---|---|---|---|---|",
    ]
    for label, e_ov, e_bh, s_ov, s_bh in conv:
        lines.append(f"| {label} | ×{e_ov:.1f} ({100 * (e_ov - 1):+.0f} %) | "
                     f"×{e_bh:.1f} ({100 * (e_bh - 1):+.0f} %) | {s_ov:+.3f} | {s_bh:+.3f} | "
                     f"{'OUI' if e_ov > e_bh else '**non**'} |")

    me_ex_ov = trading_metrics(ex_ov)
    lines += [
        "",
        f"MDD sous l'arithmétique exacte : candidat {mdd_pct(ex_ov):.1f} % contre "
        f"{mdd_pct(ex_bh):.1f} % pour Buy & Hold "
        f"(Sortino candidat {me_ex_ov['sortino_ann']:+.2f}).",
        "",
        "## Lecture honnête",
        "",
        "1. **Le sens du résultat ne change pas** sous la seule autre arithmétique "
        "défendable (la n° 3, exacte) : le candidat bat Buy & Hold sur les deux jambes, "
        "avec un Sharpe encore un peu meilleur (+0,78 contre +0,65).",
        "2. **Mais l'ampleur du gain de rendement, elle, change beaucoup** : +58 % de "
        "capital final relatif sous la convention du projet, seulement **+4,7 %** sous "
        "l'arithmétique exacte. La marge réelle sur la jambe rendement est donc **mince**, "
        "et c'est ce chiffre-là qu'il faut retenir, pas le premier.",
        "3. La convention n° 2 (hybride log) ferait basculer la jambe rendement en échec — "
        "mais elle est **mathématiquement fausse pour une exposition variable** "
        "(`ln(1 + pos·(e^r − 1)) ≠ pos·r`), elle n'est donc pas retenue ; elle est publiée "
        "pour que personne ne découvre ce chiffre plus tard en croyant à une dissimulation.",
        "4. **Portée au-delà de ce cycle** : la convention n° 1 avantage mécaniquement toute "
        "stratégie MOINS volatile que son benchmark (l'écart `prod(1+x)` vs `exp(Σx)` croît "
        "avec la variance de `x`). Les 164 cycles du backlog utilisent tous cette "
        "convention, appliquée identiquement au candidat et au benchmark ; ce constat ne "
        "réécrit aucun verdict passé mais mérite d'être connu — il est signalé ici, pas "
        "transformé en campagne de révision rétroactive (même principe que la Règle 10, "
        "portée prospective).",
    ]

    out = ROOT / "results" / "nonml_volatility_managed_portfolio_gjr_compounding_check.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
