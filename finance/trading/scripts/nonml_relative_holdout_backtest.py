"""Hors-echantillon RELATIF au benchmark — la piste C refaite (#459).

Specification pre-enregistree dans `PREREG_relative_holdout.md`, committee
AVANT toute mesure.

Le #458 mesurait le Sharpe **absolu** et concluait a tort a une persistance :
Buy & Hold faisait mieux sur la meme fenetre. Ce cycle mesure l'**edge** —
Sharpe(strategie) moins Sharpe(benchmark), sur la MEME fenetre — avec les memes
decoupes, pour que seule la metrique change.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import nonml_pnl_duplicate_sweep_backtest as sw  # noqa: E402
import nonml_verdict  # noqa: E402

OUT = RESULTS / "nonml_relative_holdout_result.md"

DECOUPES = [252, 504]        # IDENTIQUES au #458, volontairement
MIN_SEANCES = 756


def sharpe_ann(s):
    s = np.asarray(s, float)
    return float(s.mean() / s.std() * np.sqrt(252)) if s.std() > 0 else 0.0


def strategie_et_benchmark(d):
    """(serie de la strategie, serie du benchmark) selon le schema porte."""
    f = set(d.files)
    c = float(d["cost_bps"]) / 1e4 if "cost_bps" in f else 0.0
    s, _ = sw.net_pnl(d)
    if s is None:
        return None, None, "schéma non reconstructible"
    if "r_asset" in f:                                   # indiciel / deux jambes
        return np.asarray(s, float), np.asarray(d["r_asset"], float), "indiciel"
    if {"pnl_gross_bh", "turn_bh"} <= f:                 # panier
        bh = np.asarray(d["pnl_gross_bh"], float) - np.asarray(d["turn_bh"], float) * c
        return np.asarray(s, float), bh, "panier"
    if "pnl_ref" in f:                                   # troisieme schema (#444)
        return np.asarray(s, float), np.asarray(d["pnl_ref"], float), "troisième schéma"
    return None, None, "aucun benchmark identifiable"


def main():
    retenus, exclus = {}, []
    for p in sorted(RESULTS.glob("nonml_*_pnl.npz")):
        nom = p.name[len("nonml_"):-len("_pnl.npz")]
        rap = RESULTS / f"nonml_{nom}_result.md"
        if not rap.exists():
            continue
        if nonml_verdict.verdict_of(rap.read_text(encoding="utf-8")) != "PASS":
            continue
        try:
            d = np.load(p, allow_pickle=True)
            s, b, tag = strategie_et_benchmark(d)
        except Exception as exc:  # noqa: BLE001
            exclus.append((nom, f"illisible : {exc}"))
            continue
        if s is None or b is None:
            exclus.append((nom, tag))
            continue
        n = min(len(s), len(b))
        if n < MIN_SEANCES:
            exclus.append((nom, f"trop court ({n} < {MIN_SEANCES})"))
            continue
        if not np.isfinite(s[-n:]).all() or not np.isfinite(b[-n:]).all():
            exclus.append((nom, "série inexploitable"))
            continue
        retenus[nom] = (s[-n:], b[-n:], tag)

    L = ["# Hors-échantillon **relatif au benchmark** — la piste C refaite "
         "(pré-enregistré)", ""]
    L.append("Le #458 mesurait le Sharpe **absolu** et concluait à tort à une persistance :")
    L.append("Buy & Hold faisait **mieux** sur la même fenêtre. Ce cycle mesure l'**edge**,")
    L.append("avec les **mêmes découpes**, pour que seule la métrique change.")
    L.append("")
    L.append("> **Un edge n'est pas une performance.** Gagner 30 % dans un marché qui gagne")
    L.append("> 35 % n'est pas un edge — c'est exactement ce que le #458 n'a pas su voir.")
    L.append("")

    L.append("## Couverture")
    L.append("")
    L.append(f"- PASS retenus : **{len(retenus)}**")
    L.append(f"- exclus : **{len(exclus)}**")
    L.append("")
    if exclus:
        raisons = {}
        for _, why in exclus:
            cle = why.split(" (")[0]
            raisons[cle] = raisons.get(cle, 0) + 1
        L.append("| Raison d'exclusion | Nombre |")
        L.append("|---|---|")
        for why, k in sorted(raisons.items(), key=lambda t: -t[1]):
            L.append(f"| {why} | **{k}** |")
        L.append("")
    schemas = {}
    for _, (_, _, tag) in retenus.items():
        schemas[tag] = schemas.get(tag, 0) + 1
    L.append("Benchmarks employés, par schéma : "
             + ", ".join(f"**{k}** ({v})" for k, v in sorted(schemas.items())))
    L.append("")

    resume = {}
    for h in DECOUPES:
        rows = []
        for nom, (s, b, _) in retenus.items():
            if len(s) <= h + 60:
                continue
            e_av = sharpe_ann(s[:-h]) - sharpe_ann(b[:-h])
            e_ap = sharpe_ann(s[-h:]) - sharpe_ann(b[-h:])
            rows.append((nom, e_av, e_ap))
        if not rows:
            continue
        ea = np.array([r[1] for r in rows])
        ep = np.array([r[2] for r in rows])
        pos = float((ep > 0).mean())
        contract = float((ep < ea).mean())
        resume[h] = (float(np.median(ea)), float(np.median(ep)), pos, contract, len(rows))

        L.append(f"## Découpe : {h} dernières séances"
                 f"{' *(principale)*' if h == DECOUPES[0] else ' *(secondaire)*'}")
        L.append("")
        L.append(f"Candidats évaluables : **{len(rows)}**")
        L.append("")
        L.append("| | Avant la fenêtre | Sur la fenêtre |")
        L.append("|---|---|---|")
        L.append(f"| **edge médian** | **{np.median(ea):+.2f}** | **{np.median(ep):+.2f}** |")
        L.append(f"| edge moyen | {ea.mean():+.2f} | {ep.mean():+.2f} |")
        L.append(f"| 1ᵉʳ quartile | {np.percentile(ea, 25):+.2f} | {np.percentile(ep, 25):+.2f} |")
        L.append(f"| 3ᵉ quartile | {np.percentile(ea, 75):+.2f} | {np.percentile(ep, 75):+.2f} |")
        L.append("")
        L.append(f"- fraction à **edge positif** sur la fenêtre : **{100*pos:.1f} %**")
        L.append(f"- fraction dont l'**edge se contracte** : **{100*contract:.1f} %**")
        L.append("")
        L.append("Les cinq plus fortes contractions :")
        L.append("")
        for nom, a, b_ in sorted(rows, key=lambda r: r[2] - r[1])[:5]:
            L.append(f"- `{nom}` — edge {a:+.2f} → **{b_:+.2f}**")
        L.append("")
        L.append("Les cinq meilleurs edges sur la fenêtre :")
        L.append("")
        for nom, a, b_ in sorted(rows, key=lambda r: -r[2])[:5]:
            L.append(f"- `{nom}` — edge {a:+.2f} → **{b_:+.2f}**")
        L.append("")

    # --- Confrontation aux predictions -------------------------------------
    h0 = DECOUPES[0]
    med_av, med_ap, pos0, contract0, n0 = resume[h0]
    q1 = med_ap <= 0
    q2 = pos0 < 0.50
    q3 = contract0 > 0.50

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    L.append(f"Sur la découpe principale ({h0} séances, {n0} candidats) :")
    L.append("")
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| edge médian sur la fenêtre ≤ 0 | ≤ 0 | {med_ap:+.2f} | "
             f"{'**vérifiée**' if q1 else '**réfutée**'} |")
    L.append(f"| fraction à edge positif < 50 % | < 50 % | {100*pos0:.1f} % | "
             f"{'**vérifiée**' if q2 else '**réfutée**'} |")
    L.append(f"| plus de la moitié se contractent | > 50 % | {100*contract0:.1f} % | "
             f"{'**vérifiée**' if q3 else '**réfutée**'} |")
    L.append("")
    n_ok = sum([q1, q2, q3])
    L.append(f"**{n_ok} sur 3.** *(Au #458 : 0 sur 3.)*")
    L.append("")

    L.append("## Lecture")
    L.append("")
    L.append("Le changement de métrique renverse le tableau du #458 : là où le Sharpe")
    L.append("**absolu** montait, l'**edge** — la seule grandeur qui mesure quelque chose —")
    L.append(f"est de **{med_ap:+.2f}** en médiane sur la fenêtre récente.")
    L.append("")
    if q1 and q2:
        L.append("**Les stratégies ne battent pas leur benchmark sur la période récente.**")
        L.append("C'est la troisième confirmation indépendante, après le **0/29** de la")
        L.append("batterie (#457) et le constat post-hoc du #458.")
        L.append("")
        L.append("Et c'est cohérent avec ce que `CLAUDE.md` établit depuis l'Étape B :")
        L.append("**Buy & Hold reste la meilleure stratégie testée**.")
    else:
        L.append("**Le résultat ne suit pas entièrement mes prédictions.** Publié tel quel.")
        L.append("")
        L.append("Un edge qui **apparaît** quand on change de métrique mérite plus de")
        L.append("méfiance qu'un edge qui disparaît : avant d'y voir une découverte, il")
        L.append("faudrait vérifier que le benchmark retenu par schéma est bien le bon.")
    L.append("")

    L.append("## Ce que ce cycle ne prouve pas")
    L.append("")
    L.append("- **La fenêtre reste contaminée par la sélection.** Ces stratégies ont été")
    L.append("  choisies en connaissant tout l'échantillon, fenêtre récente comprise. Un")
    L.append("  edge nul y est attendu même si un edge avait existé — et un edge positif")
    L.append("  n'y prouverait rien.")
    L.append("- **Aucun verdict n'est réécrit**, aucune stratégie promue ni retirée.")
    L.append("- Le rapport confondu du #458 **reste publié**, avec son diagnostic : ce")
    L.append("  cycle ne l'efface pas, il le complète.")
    L.append("")

    L.append("")
    L.append("> **Rapport dépendant du dépôt** — ce document décrit l'état du dépôt à la date")
    L.append("> de son exécution. Il change à chaque cycle qui ajoute un fichier : c'est voulu,")
    L.append("> et ce n'est pas une péremption de résultat (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()
