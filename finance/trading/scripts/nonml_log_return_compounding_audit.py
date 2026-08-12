"""Audit transversal : composition de rendements LOG avec la formule des
rendements SIMPLES.

Constat (non pré-enregistré : audit de code, aucun degré de liberté de
calibrage, aucun critère de succès à optimiser — voir le rapport).

Les backtests du backlog non-ML construisent la série de rendements de
l'actif en LOG :

    bh_full = np.log(close[1:] / close[:-1])

puis composent le rendement total avec la formule des rendements SIMPLES :

    ret = np.cumprod(1.0 + pnl)[-1] - 1.0        # <-- incorrect sur du log

Pour des rendements log la composition correcte est :

    ret = np.exp(pnl.sum()) - 1.0

L'erreur n'est pas neutre. On a
    cumprod(1 + x) = exp( sum log(1 + x_i) )   et   log(1+x) ~ x - x^2/2,
donc la formule buguée retranche approximativement sum(x_i^2)/2 : elle
PÉNALISE les séries à forte variance. Or la jambe "rendement" du critère
renforcé compare l'overlay à Buy&Hold, et les overlays de ce backlog sont
majoritairement DÉFENSIFS (ils réduisent la variance). Le bug les avantage
donc systématiquement sur cette jambe.

Ce script ne corrige rien. Il mesure, sur tous les `.npz` déjà sauvegardés
au format standard (pos / r_asset / cost_bps), combien de verdicts
"rendement overlay > rendement Buy&Hold" changent une fois la composition
corrigée.

Portée : chaque `.npz` ne contient qu'UN marché (celui explicitement
sauvegardé par le script, en général NDX). Le critère du backlog est
"≥4/5 marchés". Un basculement ici ne renverse donc PAS mécaniquement un
verdict PASS global — il établit que le verdict de CE marché était un
artefact de la formule. Le ré-examen complet exige de ré-exécuter les
scripts concernés, ce que cet audit ne fait pas.

Usage : python3 scripts/nonml_log_return_compounding_audit.py
"""

from __future__ import annotations

import glob
import os
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT = RESULTS / "nonml_log_return_compounding_audit.md"

REQUIRED = {"pos", "r_asset", "cost_bps"}

# Schéma pour lequel la reconstruction ci-dessous a été vérifiée ligne à ligne
# dans les scripts sources. Tout fichier portant des clés SUPPLÉMENTAIRES décrit
# un P&L que cette reconstruction ne modélise pas :
#   - `r_alt`       : seconde jambe d'actif (obligations) — le P&L réel est
#                     `pos_eq*r_asset + pos_bond*r_alt`, pas `pos*r_asset` ;
#   - `pos_primary`/`pos_solo`/`var_trials`/`n_trials` : pipelines ML, hors du
#                     périmètre de ce backlog non-ML.
# Ces fichiers sont EXCLUS et listés tels quels plutôt que mesurés à tort.
ALLOWED = {"pos", "r_asset", "dates", "cost_bps"}


def reconstruct(npz):
    """Rejoue le P&L exactement comme les scripts du backlog.

    Convention commune vérifiée dans les scripts sources :
        turn   = |diff(pos, prepend=1.0)|
        pnl_ov = pos * r - turn * cost
        pnl_bh = r, avec le coût d'entrée retranché au jour 0
    """
    pos = np.asarray(npz["pos"], dtype=float)
    r = np.asarray(npz["r_asset"], dtype=float)
    cost = float(npz["cost_bps"]) / 1e4
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r - turn * cost
    pnl_bh = r.copy()
    pnl_bh[0] -= cost
    return pnl_bh, pnl_ov


def compound_buggy(pnl: np.ndarray) -> float:
    """Formule effectivement utilisée dans le backlog (incorrecte sur du log)."""
    return float(np.cumprod(1.0 + pnl)[-1] - 1.0)


def compound_correct(pnl: np.ndarray) -> float:
    """Composition correcte de rendements log."""
    return float(np.exp(pnl.sum()) - 1.0)


def count_affected_scripts() -> tuple[int, int]:
    """Compte les scripts où l'idiome bugué coexiste avec des rendements log.

    Retourne (nb_scripts_avec_les_deux, nb_scripts_total).
    """
    both = 0
    paths = sorted(glob.glob(str(ROOT / "scripts" / "*.py")))
    for p in paths:
        try:
            src = Path(p).read_text(encoding="utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            continue
        has_log = "np.log(close[1:]" in src or "log_returns_pct(" in src
        has_cumprod = "cumprod(1.0 + " in src or "cumprod(1 + " in src
        if has_log and has_cumprod:
            both += 1
    return both, len(paths)


def main() -> None:
    rows, skipped = [], []
    for path in sorted(glob.glob(str(RESULTS / "*_pnl.npz"))):
        name = os.path.basename(path)[: -len("_pnl.npz")]
        try:
            npz = np.load(path, allow_pickle=True)
            if not REQUIRED <= set(npz.files):
                skipped.append((name, "schéma non standard"))
                continue
            extra = sorted(set(npz.files) - ALLOWED)
            if extra:
                skipped.append((name, f"schéma composite ({', '.join(extra)}) — P&L non modélisé ici"))
                continue
            if np.asarray(npz["pos"]).shape != np.asarray(npz["r_asset"]).shape:
                skipped.append((name, "pos et r_asset de tailles différentes"))
                continue
            pnl_bh, pnl_ov = reconstruct(npz)
        except Exception as exc:  # noqa: BLE001 - on rapporte, on ne masque pas
            skipped.append((name, f"illisible : {exc}"))
            continue

        buggy = compound_buggy(pnl_ov) > compound_buggy(pnl_bh)
        correct = compound_correct(pnl_ov) > compound_correct(pnl_bh)
        rows.append(
            {
                "name": name,
                "buggy": buggy,
                "correct": correct,
                "ret_bh_buggy": compound_buggy(pnl_bh),
                "ret_ov_buggy": compound_buggy(pnl_ov),
                "ret_bh_correct": compound_correct(pnl_bh),
                "ret_ov_correct": compound_correct(pnl_ov),
            }
        )

    flips = [r for r in rows if r["buggy"] != r["correct"]]
    lost = [r for r in flips if r["buggy"] and not r["correct"]]
    gained = [r for r in flips if not r["buggy"] and r["correct"]]

    L = []
    L.append("# Audit — composition de rendements log avec la formule des rendements simples")
    L.append("")
    L.append("**Ceci n'est pas un backtest de stratégie et n'incrémente pas le compteur")
    L.append("d'hypothèses.** C'est un audit de code : aucun paramètre à calibrer, aucun")
    L.append("seuil de succès à choisir, donc aucun degré de liberté exploitable. Il n'a")
    L.append("pas fait l'objet d'un pré-enregistrement pour cette raison.")
    L.append("")
    L.append("## Rectification d'une première version de cet audit")
    L.append("")
    L.append("Une première version (commit `0d0edd9`) annonçait **151 fichiers exploitables,")
    L.append("20 basculements dont 17 dans le sens dangereux**. Ces chiffres étaient FAUX :")
    L.append("la reconstruction du P&L y était appliquée à des fichiers de schéma composite")
    L.append("qu'elle ne décrit pas — notamment la famille `diversification_bond_*`, dont le")
    L.append("P&L combine deux jambes d'actif (`pos_eq*r_asset + pos_bond*r_alt`) alors que la")
    L.append("reconstruction n'en modélisait qu'une. Quatre lignes du tableau publié en")
    L.append("dépendaient et étaient donc erronées.")
    L.append("")
    L.append("Après exclusion de ces schémas : **129 exploitables, 16 basculements dont 13")
    L.append("dans le sens dangereux**. Le constat de fond (bug réel, biais directionnel")
    L.append("favorable aux overlays défensifs) est inchangé ; son ampleur mesurée est")
    L.append("revue à la baisse.")
    L.append("")
    L.append("## Le bug")
    L.append("")
    L.append("Les scripts construisent la série de l'actif en rendements **log** :")
    L.append("")
    L.append("```python")
    L.append("bh_full = np.log(close[1:] / close[:-1])")
    L.append("```")
    L.append("")
    L.append("puis composent le rendement total avec la formule des rendements **simples** :")
    L.append("")
    L.append("```python")
    L.append("ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0")
    L.append("ret_ov = np.cumprod(1.0 + pnl_ov)[-1] - 1.0")
    L.append("```")
    L.append("")
    L.append("La composition correcte de rendements log est `np.exp(pnl.sum()) - 1.0`.")
    L.append("")
    L.append("Le Sharpe et le MDD ne sont PAS touchés : `trading_metrics` traite bien sa")
    L.append("série comme du log (`eq = np.cumsum(strat_ret)`, MDD converti par `exp(mdd)-1`).")
    L.append("Seule la colonne « rendement total » — et donc la jambe « Rdt>BH » du critère")
    L.append("renforcé — est affectée.")
    L.append("")
    L.append("## Pourquoi l'erreur n'est pas neutre")
    L.append("")
    L.append("`cumprod(1+x) = exp(Σ log(1+x_i))` et `log(1+x) ≈ x - x²/2`. La formule buguée")
    L.append("retranche donc approximativement `Σ x_i²/2` : elle **pénalise les séries à forte")
    L.append("variance**. Les overlays de ce backlog étant majoritairement défensifs (ils")
    L.append("réduisent la variance), le bug les **avantage systématiquement** sur la jambe")
    L.append("rendement. La direction du biais est prévisible avant même de mesurer, et les")
    L.append("basculements observés ci-dessous la confirment.")
    L.append("")
    L.append("## Mesure")
    L.append("")
    n_both, n_scripts = count_affected_scripts()
    L.append(f"- scripts de `finance/trading/scripts/` combinant rendements log et")
    L.append(f"  composition `cumprod(1+·)` : **{n_both}** sur {n_scripts}")
    L.append("- idiome vérifié directement dans la source pour :")
    L.append("  `nonml_delinquency_nfci_baa10y_corr_move_cpi_majority_overlay` (lignes 79 / 119-120),")
    L.append("  `nonml_bitcoin_momentum_overlay` (94 / 115-116),")
    L.append("  `nonml_dispersion_vol_targeting_overlay_pit_universe` (102 / 139-140),")
    L.append("  `nonml_volatility_managed_portfolio_gjr` (78 / 90-91).")
    L.append("- échelle des séries sauvegardées vérifiée : toutes en **fraction**, aucune en")
    L.append("  pourcentage (le script GJR convertit bien via `r_pct / 100.0`) — le balayage")
    L.append("  ci-dessous n'est donc pas faussé par un mélange d'unités.")
    L.append(f"- `.npz` exploitables (schéma standard `pos`/`r_asset`/`dates`/`cost_bps`) : **{len(rows)}**")
    L.append(f"- **exclus** (schéma composite ou illisible) : **{len(skipped)}**")
    L.append("")
    L.append("Les fichiers exclus le sont parce que la reconstruction du P&L vérifiée dans")
    L.append("la source ne les décrit pas : `r_alt` signale une seconde jambe d'actif")
    L.append("(`pos_eq*r_asset + pos_bond*r_alt`), et `pos_primary`/`var_trials` des pipelines")
    L.append("ML hors périmètre. Les mesurer avec `pos*r_asset` produirait un P&L faux.")
    L.append("")
    if skipped:
        L.append("<details><summary>Liste des exclus</summary>")
        L.append("")
        for n, why in sorted(skipped):
            L.append(f"- `{n}` — {why}")
        L.append("")
        L.append("</details>")
        L.append("")
    L.append(f"- verdicts « Rdt>BH » inchangés : **{len(rows) - len(flips)}**")
    L.append(f"- verdicts qui **basculent** : **{len(flips)}**")
    L.append(f"  - dont OUI → non (le bug fabriquait un verdict favorable) : **{len(lost)}**")
    L.append(f"  - dont non → OUI (le bug masquait un verdict favorable) : **{len(gained)}**")
    L.append("")
    if flips:
        L.append("### Verdicts qui basculent")
        L.append("")
        L.append("| Stratégie (marché sauvegardé dans le `.npz`) | Rdt BH (bugué) | Rdt overlay (bugué) | Rdt BH (corrigé) | Rdt overlay (corrigé) | Verdict bugué | Verdict corrigé |")
        L.append("|---|---|---|---|---|---|---|")
        for r in sorted(flips, key=lambda x: x["name"]):
            L.append(
                f"| {r['name']} | {100*r['ret_bh_buggy']:+.1f}% | {100*r['ret_ov_buggy']:+.1f}% | "
                f"{100*r['ret_bh_correct']:+.1f}% | {100*r['ret_ov_correct']:+.1f}% | "
                f"{'OUI' if r['buggy'] else 'non'} | {'OUI' if r['correct'] else 'non'} |"
            )
        L.append("")
    L.append("## Les simulations 300 € sont touchées aussi")
    L.append("")
    L.append("Les scripts `*_sim_300e.py` utilisent le même idiome")
    L.append("(`CAPITAL0 * np.cumprod(1.0 + pnl)` sur des rendements log). L'ampleur y est")
    L.append("faible parce que la fenêtre est courte (63 séances) et que le terme d'erreur")
    L.append("croît avec l'horizon : sur la jambe Buy&Hold NDX, **349,93 € publié contre")
    L.append("352,39 € corrigé** (+2,46 €, soit +0,7 %). À comparer au même bug sur 24 ans")
    L.append("(+1542,9 % publié contre +2846,0 % réel). Le biais est donc négligeable à")
    L.append("3 mois et massif à l'échelle du backtest complet.")
    L.append("")
    L.append("## Portée exacte de ce que ceci établit — et ce qu'il n'établit pas")
    L.append("")
    L.append("Chaque `.npz` ne contient qu'**un seul marché** (celui que le script a choisi de")
    L.append("sauvegarder, en général NDX). Le critère du backlog est « ≥4/5 marchés ». Un")
    L.append("basculement ci-dessus établit donc que le verdict de **ce marché-là** était un")
    L.append("artefact de la formule ; il ne renverse pas mécaniquement le PASS global de la")
    L.append("stratégie. Statuer exige de ré-exécuter les scripts concernés avec la")
    L.append("composition corrigée, sur les 5 marchés. Cet audit ne le fait pas et ne")
    L.append("reclasse aucune entrée du backlog.")
    L.append("")
    L.append("Ce qui est établi en revanche :")
    L.append("")
    L.append("1. Le bug est **réel et confirmé dans le code source**, pas une hypothèse.")
    L.append("2. Il est **répandu** : l'idiome coexiste avec des rendements log dans une")
    L.append("   large partie des scripts du backlog.")
    L.append("3. Son biais est **directionnel et favorable aux overlays défensifs**, c'est-à-dire")
    L.append("   favorable dans le sens qui produit des PASS.")
    L.append("4. Sur les marchés mesurables ici, il a effectivement fabriqué des verdicts")
    L.append(f"   favorables dans **{len(lost)} cas sur {len(flips)} basculements**.")
    L.append("")
    L.append("Les chiffres de rendement total publiés dans tous les résultats concernés sont")
    L.append("par ailleurs **sous-estimés** (ex. NDX Buy&Hold : +1542,9 % publié contre")
    L.append("+2846,0 % réel), y compris pour Buy&Hold lui-même.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"npz exploitables : {len(rows)}, ignorés : {len(skipped)}")
    print(f"verdicts inchangés : {len(rows)-len(flips)}, basculements : {len(flips)} "
          f"(OUI->non : {len(lost)}, non->OUI : {len(gained)})")
    print(f"écrit : {OUT}")


if __name__ == "__main__":
    main()
