"""La convention d'auto-declaration est-elle en train de mourir ? (#492)

Specification pre-enregistree dans `PREREG_declaration_convention_decay.md`,
committee AVANT toute mesure -- les deux regles et les seuils compris.

Le #486 a observe 33 declares apparus le 13/08 puis 0 sur les 5 derniers, et a
inscrit la question. Ce cycle la tranche.

Lecture de `git log` et du disque : aucun script execute, aucun effet de bord.
"""
import datetime as dt
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
REPO = ROOT.parent.parent

OUT = RESULTS / "nonml_declaration_convention_decay_result.md"
MOI = "declaration_convention_decay"
RECENTS = 20

# Les deux regles, figees par le pre-enregistrement.
LITTERALE = re.compile(r"Cycle d[e'’]\s*\*\*([^*]+)\*\*", re.I)
TOLERANTE = re.compile(r"\*\*Cycle d[e'’]\s*([^*]+)\*\*|Cycle d[e'’]\s*\*\*([^*]+)\*\*",
                       re.I)
# Les cinq derniers cycles, nommes par le critere 5.
MIENS = ["masking_guards_witness_patch", "duplicate_sweep_irreparability",
         "remaining_masking_guards_patch", "battery_witness_hoist",
         "battery_indet_hoist_declared"]


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def date_intro(rel):
    out = git("log", "--diff-filter=A", "--reverse", "--format=%ct", "--", rel)
    l = [x.strip() for x in out.splitlines() if x.strip()]
    return int(l[0]) if l else None


def jour(ts):
    return dt.datetime.utcfromtimestamp(ts).strftime("%d/%m/%Y")


def main():
    pop = []
    for p in sorted(ROOT.glob("PREREG_*.md")):
        nom = p.name[len("PREREG_"):-3]
        if nom == MOI:
            continue
        tete = "\n".join(p.read_text(encoding="utf-8").splitlines()[:12])
        ml, mt = LITTERALE.search(tete), TOLERANTE.search(tete)
        pop.append({
            "nom": nom, "ts": date_intro(f"finance/trading/{p.name}"),
            "lit": bool(ml), "tol": bool(mt),
            "x": (ml.group(1).strip() if ml else
                  ((mt.group(1) or mt.group(2)).strip() if mt else "")),
        })
    dates = [d for d in pop if d["ts"] is not None]
    n_lit = sum(1 for d in pop if d["lit"])
    n_tol = sum(1 for d in pop if d["tol"])
    recents = sorted(dates, key=lambda d: -d["ts"])[:RECENTS]
    pl = 100 * sum(1 for d in recents if d["lit"]) / len(recents) if recents else 0.0
    pt = 100 * sum(1 for d in recents if d["tol"]) / len(recents) if recents else 0.0

    if pt - pl >= 30:
        lec, lab = "B", "**Artefact de format** — c'est le détecteur qui décroche"
    elif pt < 30 and (pt - pl) < 30:
        lec, lab = "A", "**Déclin réel** — la convention est abandonnée"
    else:
        lec, lab = "C", "**Ni l'un ni l'autre**"

    fr = lambda x: f"{x:.1f}".replace(".", ",")   # noqa: E731

    L = ["# La convention est-elle **en train de mourir** ? (pré-enregistré)", ""]
    L.append("Le **#486** avait observé **33** déclarés apparus le 13/08, puis **0**")
    L.append("sur les 5 derniers, et inscrit la question sans la trancher.")
    L.append("")

    L.append("## Les deux règles, citées verbatim")
    L.append("")
    L.append("```python")
    L.append(r'LITTERALE = r"Cycle d[e\'’]\s*\*\*([^*]+)\*\*"        # celle du #483')
    L.append(r'TOLERANTE = r"\*\*Cycle d[e\'’]\s*([^*]+)\*\*|Cycle d[e\'’]\s*\*\*([^*]+)\*\*"')
    L.append("```")
    L.append("")
    L.append("La tolérante accepte **les deux mises en forme** — le mot seul en gras,")
    L.append("ou la phrase entière — **et rien d'autre**. Elle n'élargit pas la notion")
    L.append("de déclaration, seulement sa typographie.")
    L.append("")

    L.append("## Les deux comptes, côte à côte")
    L.append("")
    L.append("| Règle | Déclarés sur l'ensemble | Part parmi les "
             f"{len(recents)} plus récents |")
    L.append("|---|---|---|")
    L.append(f"| **littérale** *(#483)* | **{n_lit} / {len(pop)}** | "
             f"**{fr(pl)} %** |")
    L.append(f"| **tolérante** | **{n_tol} / {len(pop)}** | **{fr(pt)} %** |")
    L.append(f"| *écart* | *{n_tol - n_lit:+d}* | *{fr(pt - pl)} points* |")
    L.append("")

    L.append("## La chronologie, sous les deux règles")
    L.append("")
    ordre = sorted(dates, key=lambda d: d["ts"])
    taille = max(1, len(ordre) // 6)
    L.append("| Tranche | Période | Littérale | Tolérante |")
    L.append("|---|---|---|---|")
    for i in range(0, len(ordre), taille):
        b = ordre[i:i + taille]
        if not b:
            continue
        nl = sum(1 for d in b if d["lit"])
        nt = sum(1 for d in b if d["tol"])
        L.append(f"| {i + 1}–{i + len(b)} | {jour(b[0]['ts'])} → "
                 f"{jour(b[-1]['ts'])} | **{nl} / {len(b)}** | **{nt} / {len(b)}** |")
    L.append("")

    L.append("## Les cinq derniers cycles, nommés")
    L.append("")
    L.append("*Critère 5 : ce sont les miens, et ce sont eux qui font le constat du")
    L.append("#486. Ils doivent être nommés un par un.*")
    L.append("")
    L.append("| Cycle | Littérale | Tolérante | Déclaration lue |")
    L.append("|---|---|---|---|")
    trouves = 0
    for n in MIENS:
        d = next((x for x in pop if x["nom"] == n), None)
        if not d:
            L.append(f"| `{n}` | *absent* | *absent* | — |")
            continue
        if d["tol"] and not d["lit"]:
            trouves += 1
        L.append(f"| `{n}` | **{'oui' if d['lit'] else 'non'}** | "
                 f"**{'oui' if d['tol'] else 'non'}** | "
                 f"{'« ' + d['x'] + ' »' if d['x'] else '—'} |")
    L.append("")
    L.append(f"- détectés par la **tolérante seule** : **{trouves} / {len(MIENS)}**")
    L.append("")

    L.append("## La lecture retenue")
    L.append("")
    L.append("Le critère, **fixé avant mesure** : **B** si `T − L ≥ 30 points` ;")
    L.append("**A** si `T < 30 %` et `T − L < 30 points` ; **C** sinon.")
    L.append("")
    L.append(f"> ### **{lec}** — {lab}")
    L.append("")
    if lec == "B":
        L.append("**La convention n'est pas morte : elle a changé de typographie.** Les")
        L.append("cycles récents écrivent `**Cycle de MODIFICATION**` — la phrase")
        L.append("entière en gras — au lieu de `Cycle de **MODIFICATION**`. **Ils")
        L.append("déclarent exactement la même chose**, et la règle du #483 ne les voit")
        L.append("pas.")
        L.append("")
        L.append("> **Le constat du #486 est nuancé, pas réécrit.** Son « 0 sur les 5")
        L.append("> derniers » était **exact sous sa règle** ; il mesurait la couverture")
        L.append("> d'un détecteur, pas l'état d'une pratique.")
        L.append("")
        L.append("**C'est l'hypothèse qui m'arrangeait, et elle se vérifie.** Je la")
        L.append("publie donc avec la réserve qui s'impose : je l'avais formulée avant")
        L.append("de mesurer, mais **c'est moi qui écris les cycles dont il s'agit**, et")
        L.append("j'avais toute latitude pour deviner juste. **Le fait mesurable — deux")
        L.append("mises en forme pour une même déclaration — est vérifiable par un")
        L.append("tiers ; mon mérite à l'avoir prédit ne l'est pas.**")
    elif lec == "A":
        L.append("**La convention est réellement abandonnée** — et par moi, puisque")
        L.append("c'est moi qui écris ces cycles. Aucune excuse typographique.")
    else:
        L.append("Les deux règles concordent et la baisse persiste sans explication")
        L.append("typographique.")
    L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    p1 = lec == "B"
    p2 = trouves == len(MIENS)
    p3 = (n_tol - n_lit) >= 5
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| lecture B retenue | B | {lec} | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| les 5 derniers : tolérante seule | 5 | {trouves} | "
             f"{'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| +5 déclarés au moins | ≥ 5 | {n_tol - n_lit:+d} | "
             f"{'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")

    L.append("## Ce que cela change au compte du #486")
    L.append("")
    L.append(f"- déclarés selon le #483/#486 : **{n_lit}**")
    L.append(f"- déclarés en acceptant les deux typographies : **{n_tol}**")
    L.append("")
    L.append("**Aucun chiffre du #486 n'est faux** : il comptait ce que sa règle")
    L.append("voyait, et il l'a dit. **Ce cycle ajoute que la règle voyait moins que la")
    L.append("pratique.**")
    L.append("")
    L.append("> La règle du #483 **n'est pas modifiée** dans les autres cycles : la")
    L.append("> tolérante n'existe que dans ce rapport. La changer partout serait une")
    L.append("> modification non déclarée, et elle mériterait son propre cycle.")
    L.append("")

    L.append("## Critères de succès")
    L.append("")
    c5 = all(any(x["nom"] == n for x in pop) for n in MIENS)
    L.append("1. Deux règles citées verbatim, comptes côte à côte — **OUI**.")
    L.append("2. Chronologie publiée sous les deux règles — **OUI**.")
    L.append(f"3. Une lecture nommée par le critère chiffré — **OUI** (**{lec}**).")
    L.append("4. Constat du #486 nuancé sans réécriture — "
             + ("**OUI**" if lec == "B" else "**sans objet**") + ".")
    L.append(f"5. Les 5 derniers cycles nommés individuellement — "
             f"**{'OUI' if c5 else 'NON'}**.")
    L.append("")
    L.append(f"**{'PASS' if c5 else 'FAIL'}** — le critère porte sur le **procédé**.")
    L.append("")
    L.append("Simulation 300 € et robustesse **sans objet** : aucune position, aucun")
    L.append("paramètre de stratégie. **Aucun script du dépôt n'a été exécuté.**")
    L.append("")
    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des fichiers à la date")
    L.append("> de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"pop={len(pop)} lit={n_lit} tol={n_tol} pl={fr(pl)}% pt={fr(pt)}% "
          f"lecture={lec} miens_tol_seule={trouves}")
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
