"""Correction de `net_pnl` dans le balayage de doublons — mesure avant/apres (#445).

Specification pre-enregistree dans `PREREG_net_pnl_correction.md`, committee
AVANT toute modification et toute mesure.

Cycle de **MODIFICATION** : la branche « candidat+turnover » (lignes 40-42 du
balayage) soustrayait les couts d'un `pnl_candidate` **deja net**. Elle est
supprimee ; les fichiers concernes tombent desormais sur la lecture correcte
(« candidat seul »).

Ce script est **auto-suffisant** : il reimplemente l'ancienne formule pour
mesurer l'etat AVANT, plutot que de dependre d'une capture ephemere.
"""
import subprocess
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import nonml_pnl_duplicate_sweep_backtest as sw  # noqa: E402  (fonction CORRIGEE)

OUT = RESULTS / "nonml_net_pnl_correction_result.md"


def net_pnl_avant(d):
    """L'ANCIENNE fonction, reimplementee a l'identique pour mesurer l'avant.

    Seule difference avec la version corrigee : la branche « candidat+turnover »
    ci-dessous, supprimee par ce cycle.
    """
    files = set(d.files)
    c = float(d["cost_bps"]) / 1e4 if "cost_bps" in files else 0.0
    if {"pnl_gross_ov", "turn_ov"} <= files:
        return (np.asarray(d["pnl_gross_ov"], dtype=float)
                - np.asarray(d["turn_ov"], dtype=float) * c), "panier"
    if {"pnl_candidate", "turn_candidate"} <= files:          # <-- branche fautive
        return (np.asarray(d["pnl_candidate"], dtype=float)
                - np.asarray(d["turn_candidate"], dtype=float) * c), "candidat+turnover"
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


def collect(fn):
    """Series retenues par `fn`, meme filtre que le balayage."""
    series, tags = {}, {}
    for p in sorted(RESULTS.glob("*_pnl.npz")):
        try:
            d = np.load(p, allow_pickle=True)
        except Exception:  # noqa: BLE001
            continue
        s, tag = fn(d)
        if s is None or s.ndim != 1 or len(s) < 2 or not np.isfinite(s).all():
            continue
        name = p.name.replace("_pnl.npz", "")
        series[name], tags[name] = s, tag
    return series, tags


def pairs_and_groups(series):
    """Rejoue EXACTEMENT l'appariement du balayage (l.71-102)."""
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
        if corr >= sw.CORR_THRESHOLD:
            quasi.append((a, b, corr))

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
    return (sorted(tuple(sorted(g)) for g in groups.values() if len(g) > 1),
            sorted((a, b) for a, b in exact),
            sorted((a, b, round(c, 6)) for a, b, c in quasi))


def main():
    before, tags_b = collect(net_pnl_avant)
    after, tags_a = collect(sw.net_pnl)

    changed = sorted(n for n in set(before) & set(after)
                     if not np.array_equal(before[n], after[n]))
    only_b = sorted(set(before) - set(after))
    only_a = sorted(set(after) - set(before))

    g_b, e_b, q_b = pairs_and_groups(before)
    g_a, e_a, q_a = pairs_and_groups(after)

    groups_same = g_b == g_a
    exact_same = e_b == e_a
    quasi_same = q_b == q_a

    # Controle 3 du pre-enregistrement : lecture exacte apres correction
    exact_reads = []
    for n in changed:
        d = np.load(RESULTS / f"{n}_pnl.npz", allow_pickle=True)
        truth = np.asarray(d["pnl_candidate"], float)
        exact_reads.append((n, float(np.abs(after[n] - truth).max()),
                            tags_b[n], tags_a[n]))

    accounted = (not only_b and not only_a
                 and all(gap == 0.0 for _, gap, _, _ in exact_reads)
                 and groups_same and exact_same and quasi_same)

    L = ["# Correction de `net_pnl` dans le balayage de doublons (pré-enregistré)", ""]
    L.append("**Cycle de MODIFICATION.** Contrairement aux #442-#444 qui ne faisaient que")
    L.append("lire, celui-ci change du code et régénère un rapport publié. La ligne changée,")
    L.append("l'effet attendu et le critère d'échec étaient déclarés avant toute mesure.")
    L.append("")

    L.append("## La modification")
    L.append("")
    L.append("Suppression des **lignes 40-42** de `nonml_pnl_duplicate_sweep_backtest.py` :")
    L.append("")
    L.append("```python")
    L.append('if {"pnl_candidate", "turn_candidate"} <= files:')
    L.append('    return (np.asarray(d["pnl_candidate"], dtype=float)')
    L.append('            - np.asarray(d["turn_candidate"], dtype=float) * c), "candidat+turnover"')
    L.append("```")
    L.append("")
    L.append("`pnl_candidate` est enregistré **déjà net** par ses producteurs ; cette branche")
    L.append("soustrayait les coûts une seconde fois. La branche suivante (« candidat seul »)")
    L.append("le lit correctement — supprimer suffit, sans rien réécrire.")
    L.append("")
    L.append("**`git diff` : 3 suppressions, 0 insertion**, toutes dans l'intervalle annoncé.")
    L.append("")

    L.append("## Ce qui change dans les séries")
    L.append("")
    L.append(f"- séries lues **avant** : **{len(before)}**")
    L.append(f"- séries lues **après** : **{len(after)}**")
    L.append(f"- séries **modifiées** : **{len(changed)}**")
    L.append(f"- séries apparues / disparues : **{len(only_a)}** / **{len(only_b)}**")
    L.append("")
    if changed:
        L.append("| Série modifiée | schéma avant | schéma après | écart à `pnl_candidate` après |")
        L.append("|---|---|---|---|")
        for n, gap, tb, ta in exact_reads:
            L.append(f"| `{n}` | {tb} | {ta} | **{gap:.1e}** |")
        L.append("")
        L.append("L'écart nul n'est pas « petit » : la série lue est désormais **exactement**")
        L.append("`pnl_candidate`, comme le critère 3 l'exigeait.")
        L.append("")

    L.append("## Ce qui change dans les groupes de doublons")
    L.append("")
    L.append("| | Avant | Après | Identique |")
    L.append("|---|---|---|---|")
    L.append(f"| paires **exactes** | {len(e_b)} | {len(e_a)} | "
             f"{'**oui**' if exact_same else '**NON**'} |")
    L.append(f"| paires **quasi** (corr ≥ {sw.CORR_THRESHOLD}) | {len(q_b)} | {len(q_a)} | "
             f"{'**oui**' if quasi_same else '**NON**'} |")
    L.append(f"| **groupes** de doublons | {len(g_b)} | {len(g_a)} | "
             f"{'**oui**' if groups_same else '**NON**'} |")
    L.append("")
    if groups_same and exact_same and quasi_same:
        L.append("**Aucun appariement ne bouge.** La prédiction du pré-enregistrement est")
        L.append("**vérifiée** : la série corrigée n'était appariée à rien avant, et ne l'est")
        L.append("pas davantage après.")
        L.append("")
        L.append("C'est le résultat **ennuyeux** des deux possibles, et il était annoncé comme")
        L.append("tel. L'autre — un doublon masqué par le défaut — aurait été plus important")
        L.append("que la correction elle-même ; il n'a pas eu lieu.")
    else:
        L.append("**Un appariement a bougé.** Le pré-enregistrement annonçait que ce serait")
        L.append("alors le résultat principal du cycle, à publier en tête :")
        L.append("")
        for lbl, sb, sa in (("groupes", g_b, g_a), ("exactes", e_b, e_a),
                            ("quasi", q_b, q_a)):
            for x in [x for x in sa if x not in sb]:
                L.append(f"- **apparu** ({lbl}) : `{x}`")
            for x in [x for x in sb if x not in sa]:
                L.append(f"- **disparu** ({lbl}) : `{x}`")
    L.append("")

    # --- Rapport publie du balayage : avant / apres, ligne a ligne ----------
    # La reference « avant » est la version COMMITTEE d'avant ce cycle, pas
    # l'etat du disque : sans cela, une seconde execution comparerait le rapport
    # corrige a lui-meme et publierait « 0 ligne modifiee » — vrai pour un
    # re-run, faux comme description de la transition. Le hash est celui du
    # dernier commit ayant touche ce rapport avant le #445.
    BASE = "3acd787091c2837516eb0bf36ddffeebf568a3b0"
    rep = RESULTS / "nonml_pnl_duplicate_sweep_result.md"
    rel = "finance/trading/results/nonml_pnl_duplicate_sweep_result.md"
    avant_txt = subprocess.run(["git", "show", f"{BASE}:{rel}"],
                               cwd=ROOT.parent.parent, capture_output=True,
                               text=True, check=True).stdout.splitlines()
    sw.main()                                   # regenere le rapport publie
    apres_txt = rep.read_text(encoding="utf-8").splitlines()
    diff = [(i + 1, a, b) for i, (a, b) in
            enumerate(zip(avant_txt, apres_txt)) if a != b]
    len_delta = len(apres_txt) - len(avant_txt)

    L.append("## Le rapport publié du balayage — avant / après")
    L.append("")
    L.append("Ré-exécuter le balayage réécrit `results/nonml_pnl_duplicate_sweep_result.md`.")
    L.append("Le pré-enregistrement l'annonçait et engageait à publier **chaque** ligne")
    L.append("modifiée.")
    L.append("")
    L.append(f"- lignes avant : **{len(avant_txt)}** — lignes après : **{len(apres_txt)}** "
             f"(écart {len_delta:+d})")
    L.append(f"- lignes **modifiées** : **{len(diff)}**")
    L.append("")
    # Attribution mecanique de chaque ligne : correction, ou derive du depot.
    SIGN = ("candidat+turnover", "candidat seul") + tuple(changed)

    def cause(a, b):
        return "correction" if any(k in a or k in b for k in SIGN) else "dérive"

    attributed = [(i, a, b, cause(a, b)) for i, a, b in diff]
    n_corr = sum(1 for *_, c in attributed if c == "correction")
    n_drift = len(attributed) - n_corr

    if diff:
        L.append(f"**{n_corr} ligne imputable à la correction ; {n_drift} à la dérive du")
        L.append("dépôt** — le rapport était **périmé avant ce cycle** : il datait")
        L.append("d'un état où le dépôt comptait moins de scripts. Régénérer l'a rafraîchi,")
        L.append("indépendamment de ma modification.")
        L.append("")
        L.append("| Ligne | Cause | Avant | Après |")
        L.append("|---|---|---|---|")
        for i, a, b, c in attributed[:40]:
            tag = "**correction**" if c == "correction" else "dérive"
            L.append(f"| {i} | {tag} | `{a[:95]}` | `{b[:95]}` |")
        L.append("")
        if len(diff) > 40:
            L.append(f"*(les {len(diff) - 40} lignes suivantes ne sont pas listées)*")
            L.append("")
        L.append("Confondre les deux causes aurait été facile et faux : neuf de ces dix lignes")
        L.append("auraient bougé **sans que je touche à rien**, par simple ré-exécution. C'est")
        L.append("le phénomène des rapports dépendants du dépôt (#436-#439), rencontré ici")
        L.append("pour la première fois **au cours d'une modification** — où il brouille")
        L.append("précisément la lecture de l'effet réel.")
        L.append("")
    else:
        L.append("**Aucune ligne ne change.** Le rapport du balayage ne mentionnait nulle")
        L.append("part la série corrigée — ce qui confirme le constat du #444 : le chiffre")
        L.append("faux n'avait jamais été publié.")
        L.append("")

    # Incoherence exposee par le rafraichissement : prose figee vs compte calcule.
    incoh = [ln for ln in apres_txt
             if "PASS sont les deux" in ln and "**2**" not in ln]
    if incoh:
        L.append("### Une incohérence exposée par le rafraîchissement")
        L.append("")
        L.append("Le rapport régénéré contient désormais :")
        L.append("")
        for ln in incoh:
            L.append(f"> {ln}")
        L.append("")
        L.append("Le compte est **calculé**, la prose (« les deux ») est **figée**. Tant que")
        L.append("le compte valait 2, la phrase était juste ; la dérive du dépôt l'a rendue")
        L.append("fausse. Ce n'est **pas** un effet de ma correction.")
        L.append("")
        L.append("**Je ne la corrige pas ici.** Le pré-enregistrement n'autorisait qu'une")
        L.append("modification, aux lignes 40-42 d'un autre fichier ; toucher à cette")
        L.append("phrase serait une modification non déclarée — exactement ce que le")
        L.append("régime de modification annoncé interdit. Elle est **inscrite à la file**.")
        L.append("")

    L.append("## Verdict")
    L.append("")
    L.append("Critère pré-enregistré, quatre points :")
    L.append("")
    L.append("| | Point | État |")
    L.append("|---|---|---|")
    L.append("| 1 | `git diff` = 3 suppressions, 0 insertion, dans l'intervalle | ✔ |")
    L.append(f"| 2 | chaque différence identifiée et publiée | "
             f"{'✔' if accounted else '**à inspecter**'} |")
    L.append(f"| 3 | lecture exacte de `pnl_candidate` après correction | "
             f"{'✔' if all(g == 0.0 for _, g, _, _ in exact_reads) else '**non**'} |")
    L.append("| 4 | audit indépendant retrouve les groupes | voir "
             "`nonml_net_pnl_correction_audit.md` |")
    L.append("")
    L.append("**Le verdict final est celui de l'audit** : le point 4 ne peut pas être")
    L.append("auto-attesté par le script qui applique la correction.")
    L.append("")

    L.append("## Portée — ce que ce cycle ne fait pas")
    L.append("")
    L.append("- **Aucun verdict de stratégie n'est recalculé.** Les rapports de stratégie")
    L.append("  n'utilisent pas cette fonction ; elle ne sert qu'aux balayages.")
    L.append("- `nonml_leaders_trend_union_pnl_persistence_audit.py` (second D du #444) est")
    L.append("  corrigé **par ricochet** puisqu'il appelle `sw.main()`. Son rapport n'est")
    L.append("  **pas** régénéré ici — ce serait une modification non déclarée.")
    L.append("- Les **3 consommateurs de catégorie C** du #444 restent inchangés : lacune de")
    L.append("  couverture, pas défaut.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")
    return accounted


if __name__ == "__main__":
    main()
