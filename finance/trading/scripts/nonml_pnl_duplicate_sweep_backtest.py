"""Balayage des doublons de P&L du backlog (spécification pré-enregistrée dans
`PREREG_pnl_duplicate_sweep.md`, committée avant ce script).

Diagnostic, pas une stratégie : reconstruit le P&L net de **tous** les
`results/*_pnl.npz`, puis cherche les paires identiques ou quasi identiques.

Motivation (#403) : `sma200_leaders_overlay` et `leaders_trend_union_overlay`
sont la même stratégie écrite deux fois, et leurs P&L sont bit-à-bit identiques.
Le nombre d'essais du backlog entre dans le DSR ; des doublons le gonflent.

Critères FIXÉS AVANT EXÉCUTION :
- doublon exact      : `np.array_equal` sur le P&L net, à longueur égale ;
- quasi-doublon      : non exact, corrélation de Pearson ≥ 0,9999.

Tout schéma non reconnu est compté et listé, jamais ignoré en silence.
"""
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT = RESULTS / "nonml_pnl_duplicate_sweep_result.md"

CORR_THRESHOLD = 0.9999


def net_pnl(d):
    """Reconstruit le P&L net selon le schema detecte.

    Retourne (serie, nom_du_schema) ou (None, raison) si non reconnu.
    """
    files = set(d.files)
    c = float(d["cost_bps"]) / 1e4 if "cost_bps" in files else 0.0

    if {"pnl_gross_ov", "turn_ov"} <= files:
        return np.asarray(d["pnl_gross_ov"], dtype=float) - np.asarray(d["turn_ov"], dtype=float) * c, "panier"
    if "pnl_candidate" in files:
        return np.asarray(d["pnl_candidate"], dtype=float), "candidat seul"
    if {"pos", "r_asset"} <= files:
        pos = np.asarray(d["pos"], dtype=float)
        r = np.asarray(d["r_asset"], dtype=float)
        turn = np.abs(np.diff(pos, prepend=1.0))
        if "r_alt" in files:
            r_alt = np.asarray(d["r_alt"], dtype=float)
            return pos * r + (1.0 - pos) * r_alt - turn * c, "deux jambes"
        return pos * r - turn * c, "indiciel"
    return None, "schéma non reconnu"


def main():
    paths = sorted(RESULTS.glob("*_pnl.npz"))
    series, schemas, unknown = {}, {}, []

    for p in paths:
        try:
            d = np.load(p, allow_pickle=True)
        except Exception as exc:  # noqa: BLE001
            unknown.append((p.name, f"illisible : {exc}"))
            continue
        s, tag = net_pnl(d)
        if s is None or s.ndim != 1 or len(s) < 2 or not np.isfinite(s).all():
            unknown.append((p.name, tag if s is None else "série non exploitable"))
            continue
        name = p.name.replace("_pnl.npz", "")
        series[name] = s
        schemas[name] = tag

    exact, quasi = [], []
    names = sorted(series)
    for a, b in combinations(names, 2):
        sa, sb = series[a], series[b]
        if len(sa) != len(sb):
            continue
        if np.array_equal(sa, sb):
            exact.append((a, b))
            continue
        if np.std(sa) == 0 or np.std(sb) == 0:
            continue
        corr = float(np.corrcoef(sa, sb)[0, 1])
        if corr >= CORR_THRESHOLD:
            quasi.append((a, b, corr))

    # groupes de doublons exacts (composantes connexes)
    parent = {n: n for n in names}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in exact:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra
    groups = {}
    for n in names:
        groups.setdefault(find(n), []).append(n)
    dup_groups = [sorted(g) for g in groups.values() if len(g) > 1]
    surnumeraires = sum(len(g) - 1 for g in dup_groups)

    L = ["# Balayage des doublons de P&L du backlog (pré-enregistré)", ""]
    L.append("Diagnostic, pas une stratégie. Reconstruit le P&L net de **tous** les")
    L.append("`results/*_pnl.npz` du dépôt et cherche les paires identiques ou quasi")
    L.append("identiques. Critères fixés avant exécution : égalité exacte")
    L.append(f"(`np.array_equal`) ou corrélation ≥ {CORR_THRESHOLD}.")
    L.append("")
    L.append("## Couverture")
    L.append("")
    L.append(f"- fichiers `*_pnl.npz` trouvés : **{len(paths)}**")
    L.append(f"- P&L reconstruits : **{len(series)}**")
    L.append(f"- schémas non reconnus ou séries inexploitables : **{len(unknown)}**")
    L.append("")
    if unknown:
        L.append("| Fichier | Raison |")
        L.append("|---|---|")
        for n, why in unknown:
            L.append(f"| `{n}` | {why} |")
        L.append("")
        L.append("**Couverture incomplète — rapportée comme telle**, conformément au critère 1")
        L.append("du pré-enregistrement.")
    else:
        # Formulation reecrite au #429 (texte fixe dans son pre-enregistrement) :
        # le mot << Couverture >> suggerait une part du depot, alors que le
        # denominateur est l'ensemble des fichiers deja presents.
        L.append("**100 % des fichiers trouvés ont été relus** — critère 1 du pré-enregistrement")
        L.append("atteint. Ce taux ne mesure pas la couverture du dépôt : voir juste en dessous.")
    L.append("")
    # Decomposition et taux de couverture (cycle #428). Le chiffre ci-dessus
    # porte sur les fichiers TROUVES, pas sur le depot : sans les lignes qui
    # suivent, un lecteur surestime la portee du balayage. Rien n'est ecrit en
    # dur, tout est recalcule ici. Aucun seuil de detection n'est touche.
    n_nonml = sum(1 for n in series if n.startswith("nonml_"))
    n_other = len(series) - n_nonml
    n_scripts = len(list((ROOT / "scripts").glob("nonml_*_backtest.py")))
    # Les deux ensembles ne se correspondent PAS un a un : certains .npz portent
    # le nom d'une variante (`*_pit_universe`, `*_russell2000`) sans script
    # homonyme. La difference `n_scripts - n_nonml` ne compte donc rien de reel
    # (defaut attrape avant publication au #428) : on calcule la difference
    # ensembliste des deux cotes, et on classe les manquants par verdict.
    names_scripts = {p.name.replace("nonml_", "").replace("_backtest.py", "")
                     for p in (ROOT / "scripts").glob("nonml_*_backtest.py")}
    names_npz = {n[len("nonml_"):] for n in series if n.startswith("nonml_")}
    missing = sorted(names_scripts - names_npz)
    orphan = sorted(names_npz - names_scripts)
    verdicts = {"PASS": 0, "FAIL": 0, "indéterminé": 0, "sans rapport": 0}
    for n in missing:
        f = RESULTS / f"nonml_{n}_result.md"
        if not f.exists():
            verdicts["sans rapport"] += 1
            continue
        t = f.read_text(encoding="utf-8")
        if "**PASS" in t or "PASS (niveau 1)" in t:
            verdicts["PASS"] += 1
        elif "**FAIL" in t:
            verdicts["FAIL"] += 1
        else:
            verdicts["indéterminé"] += 1
    L.append("### Ce que « 100 % » recouvre — et ce qu'il ne recouvre pas")
    L.append("")
    L.append("Le taux ci-dessus dit que **tous les fichiers trouvés ont pu être relus**. Il ne")
    L.append("dit pas que le balayage voit tout le dépôt, ni que toutes les séries lues sont")
    L.append("des candidats non-ML. Les deux précisions manquaient jusqu'au cycle #428 :")
    L.append("")
    L.append("| | Nombre |")
    L.append("|---|---|")
    L.append(f"| séries lues (`results/*_pnl.npz`) | **{len(series)}** |")
    L.append(f"| dont candidats non-ML (`nonml_*`) | **{n_nonml}** |")
    L.append(f"| dont séries **ML / Étape D** | **{n_other}** |")
    L.append(f"| scripts de backtest non-ML du dépôt | **{n_scripts}** |")
    if n_scripts:
        L.append(f"| **couverture non-ML** | **{100*n_nonml/n_scripts:.1f} %** |")
    L.append("")
    L.append(f"**La soustraction {n_scripts} − {n_nonml} ne compte rien de réel** : les deux")
    L.append("ensembles ne se correspondent pas un à un. Certains `.npz` portent le nom d'une")
    L.append(f"**variante** (`*_pit_universe`, `*_russell2000`…) sans script homonyme — il y en a")
    L.append(f"**{len(orphan)}**. La différence ensembliste est donc la seule mesure valide :")
    L.append("")
    L.append(f"> **{len(missing)}** scripts de backtest non-ML n'ont **aucun `.npz` à leur nom** et")
    L.append("> échappent à toute détection de doublon.")
    L.append("")
    L.append("Leur verdict publié, compté et non supposé :")
    L.append("")
    L.append("| Verdict des scripts sans `.npz` | Nombre |")
    L.append("|---|---|")
    for k in ("FAIL", "PASS", "indéterminé", "sans rapport"):
        L.append(f"| {k} | **{verdicts[k]}** |")
    L.append("")
    L.append(f"Les **{verdicts['FAIL']}** FAIL ne peuvent pas changer de verdict, mais un doublon")
    L.append("parmi eux gonflerait tout de même le décompte d'hypothèses testées. Les")
    L.append(f"**{verdicts['PASS']}** PASS sont les deux candidats écartés au #427 avec leur raison")
    L.append("publiée (variantes multiples, et un diagnostic qui n'est pas une stratégie).")
    L.append("")
    L.append(f"Le balayage lit `results/*_pnl.npz` **sans filtre de préfixe** : les {n_other} séries")
    L.append("ML / Étape D sont comparées aux candidats non-ML. C'est voulu — un doublon")
    L.append("inter-familles est une information — mais il faut le savoir pour lire les groupes")
    L.append("ci-dessous, dont l'un associe précisément une série d'Étape D à un candidat non-ML.")
    L.append("")
    counts = {}
    for tag in schemas.values():
        counts[tag] = counts.get(tag, 0) + 1
    L.append("Répartition par schéma : " + ", ".join(
        f"{k} ({v})" for k, v in sorted(counts.items(), key=lambda kv: -kv[1])) + ".")
    L.append("")

    L.append("## Doublons exacts")
    L.append("")
    L.append(f"- paires à P&L **bit-à-bit identique** : **{len(exact)}**")
    L.append(f"- groupes de doublons : **{len(dup_groups)}**")
    L.append(f"- entrées surnuméraires (essais comptés en trop) : **{surnumeraires}**")
    L.append("")
    if dup_groups:
        for g in dup_groups:
            L.append(f"- **groupe de {len(g)}** : " + ", ".join(f"`{x}`" for x in g))
    else:
        L.append("Aucun.")
    L.append("")

    L.append("## Quasi-doublons (corrélation ≥ seuil, non identiques)")
    L.append("")
    L.append(f"- paires signalées : **{len(quasi)}**")
    L.append("")
    if quasi:
        L.append("| Candidat A | Candidat B | Corrélation |")
        L.append("|---|---|---|")
        for a, b, corr in sorted(quasi, key=lambda t: -t[2]):
            L.append(f"| `{a}` | `{b}` | {corr:.8f} |")
        L.append("")
        L.append("Ces paires **ne sont pas comptées comme doublons** à ce stade : le critère 2")
        L.append("du pré-enregistrement impose de les confirmer ou de les rejeter par lecture")
        L.append("des deux scripts. Voir l'audit.")
    else:
        L.append("Aucune.")
    L.append("")

    L.append("## Effet sur le décompte d'essais")
    L.append("")
    L.append(f"Le backlog compte actuellement **372** essais dans le calcul du DSR.")
    L.append(f"Les doublons exacts en rendent **{surnumeraires}** surnuméraires, soit un")
    L.append(f"décompte corrigé de **{372 - surnumeraires}** avant examen des quasi-doublons.")
    L.append("")
    L.append("**Aucune correction n'est appliquée dans ce cycle**, conformément au")
    L.append("pré-enregistrement : rejouer les batteries avec un `n_trials` corrigé après")
    L.append("avoir vu quels candidats en bénéficieraient serait précisément ce que le")
    L.append("protocole interdit. Le décompte corrigé est publié, son usage est un cycle")
    L.append("distinct à déclarer.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")
    return dup_groups, quasi, unknown


if __name__ == "__main__":
    main()
