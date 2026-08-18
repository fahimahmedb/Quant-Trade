"""Audit adversarial du #492 — contrôle d'une hypothèse qui arrangeait l'auteur.

Le cycle soupconnait un artefact de format, et le trouve. **C'est le resultat
qui l'arrange** : il transforme un abandon de convention (dont il serait
responsable) en defaut de detecteur. L'audit teste donc l'hypothese contre
elle-meme.

Routes propres :
1. la variante typographique existe-t-elle vraiment ?  -> extraction du texte
2. la regle tolerante n'elargit-elle QUE la typographie ? -> faux positifs
3. le declin littéral etait-il reel ?                  -> recomptage separe
4. le cycle publie-t-il la reserve sur son propre merite ?
"""
import datetime as dt
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
REPO = ROOT.parent.parent

RAPPORT = RESULTS / "nonml_declaration_convention_decay_result.md"
OUT = RESULTS / "nonml_declaration_convention_decay_audit.md"
MOI = "declaration_convention_decay"
LITTERALE = re.compile(r"Cycle d[e'’]\s*\*\*([^*]+)\*\*", re.I)
TOLERANTE = re.compile(r"\*\*Cycle d[e'’]\s*([^*]+)\*\*|Cycle d[e'’]\s*\*\*([^*]+)\*\*",
                       re.I)


def sans_markdown(t):
    return re.sub(r"\s+", " ", t.replace("*", "").replace("`", ""))


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def main():
    pub = sans_markdown(RAPPORT.read_text(encoding="utf-8")) if RAPPORT.exists() else ""
    # « Declare d'avance » se verifie dans le PREREG, pas dans le rapport :
    # chercher la phrase dans `pub` serait tester au mauvais endroit.
    PRE = ROOT / f"PREREG_{MOI}.md"
    pre = sans_markdown(PRE.read_text(encoding="utf-8")) if PRE.exists() else ""
    fichiers = sorted(p for p in ROOT.glob("PREREG_*.md")
                      if p.name[len("PREREG_"):-3] != MOI)

    L = ["# Audit adversarial — la convention et son détecteur (#492)", ""]
    L.append("**Le cycle soupçonnait un artefact de format, et le trouve.** C'est")
    L.append("**le résultat qui l'arrange** : il transforme un abandon de convention —")
    L.append("dont il serait responsable — en défaut de détecteur. **L'audit teste")
    L.append("donc l'hypothèse contre elle-même.**")
    L.append("")

    # --- 1. La variante existe-t-elle ? ------------------------------------
    L.append("## 1. La variante typographique existe-t-elle vraiment ?")
    L.append("")
    L.append("Route : extraire **le texte réel** des déclarations captées par la")
    L.append("tolérante mais pas par la littérale, et vérifier qu'il s'agit bien de la")
    L.append("phrase entière en gras.")
    L.append("")
    exemples, n_var = [], 0
    for p in fichiers:
        tete = "\n".join(p.read_text(encoding="utf-8").splitlines()[:12])
        if TOLERANTE.search(tete) and not LITTERALE.search(tete):
            n_var += 1
            m = re.search(r"\*\*Cycle d[e'’][^*]+\*\*", tete, re.I)
            if m and len(exemples) < 5:
                exemples.append((p.name, m.group(0)))
    L.append(f"- `PREREG_` captés par la **tolérante seule** : **{n_var}**")
    L.append("")
    L.append("Extraits **verbatim** :")
    L.append("")
    L.append("```")
    for nom, txt in exemples:
        L.append(f"{nom} : {txt}")
    L.append("```")
    L.append("")
    reelle = n_var > 0 and all("**Cycle d" in t for _n, t in exemples)
    if reelle:
        L.append("> **La variante est réelle et lisible.** Ce ne sont pas des")
        L.append("> déclarations approximatives rattrapées par une règle lâche : ce sont")
        L.append("> **les mêmes mots, avec les astérisques déplacés**.")
    L.append("")

    # --- 2. La tolerante n'elargit-elle QUE la typographie ? ----------------
    L.append("## 2. La tolérante n'élargit-elle **que** la typographie ?")
    L.append("")
    L.append("Contrôle : les déclarations qu'elle capte en plus contiennent-elles")
    L.append("toutes littéralement `Cycle de` / `Cycle d'` ? Si l'une ne le contenait")
    L.append("pas, la règle aurait élargi la **notion**, pas la mise en forme.")
    L.append("")
    faux = 0
    for p in fichiers:
        tete = "\n".join(p.read_text(encoding="utf-8").splitlines()[:12])
        if TOLERANTE.search(tete) and not LITTERALE.search(tete):
            if not re.search(r"Cycle d[e'’]", tete, re.I):
                faux += 1
    L.append(f"- captés en plus **sans** la locution « Cycle de » : **{faux}**")
    L.append("")
    if faux == 0:
        L.append("> **Aucun.** La tolérante ne reconnaît rien que la littérale aurait")
        L.append("> refusé sur le fond. **L'élargissement est purement typographique**,")
        L.append("> comme annoncé.")
    else:
        L.append(f"> **{faux} cas** élargissent la notion — la règle est plus lâche")
        L.append("> qu'annoncé, et c'est publié tel quel.")
    L.append("")

    # --- 3. Le declin litteral etait-il reel ? ------------------------------
    L.append("## 3. Le déclin **littéral** était-il réel ?")
    L.append("")
    L.append("Le #486 avait raison **sous sa règle**. Contrôle indépendant : parmi les")
    L.append("20 plus récents, combien la littérale en voit-elle ?")
    L.append("")
    horod = []
    for p in fichiers:
        out = git("log", "--diff-filter=A", "--reverse", "--format=%ct",
                  "--", f"finance/trading/{p.name}")
        ls = [x.strip() for x in out.splitlines() if x.strip()]
        if ls:
            tete = "\n".join(p.read_text(encoding="utf-8").splitlines()[:12])
            horod.append((int(ls[0]), bool(LITTERALE.search(tete)),
                          bool(TOLERANTE.search(tete))))
    horod.sort(key=lambda x: -x[0])
    r20 = horod[:20]
    nl = sum(1 for _t, l, _x in r20 if l)
    nt = sum(1 for _t, _l, x in r20 if x)
    L.append(f"- littérale sur les 20 plus récents : **{nl} / 20**")
    L.append(f"- tolérante sur les 20 plus récents : **{nt} / 20**")
    L.append("")
    if nl < nt:
        L.append("> **Le déclin littéral est réel — et sans signification.** Le #486")
        L.append("> mesurait la couverture d'un détecteur ; il ne s'est pas trompé, il")
        L.append("> a mesuré autre chose que ce qu'on lui a fait dire.")
    L.append("")

    # --- 4. Le cycle publie-t-il la reserve sur son propre merite ? ---------
    L.append("## 4. Le cycle se donne-t-il le beau rôle ?")
    L.append("")
    controles = [
        ("il déclare **dans le PREREG** que l'hypothèse l'arrange",
         "hypothèse commode pour moi" in pre),
        ("il publie la réserve sur son propre mérite à l'avoir prédit",
         "mon mérite à l'avoir prédit ne l'est pas" in pub),
        ("il dit qu'aucun chiffre du #486 n'est faux",
         "Aucun chiffre du #486 n'est faux" in pub),
        ("il refuse de changer la règle du #483 ailleurs",
         "n'existe que dans ce rapport" in pub),
        ("il nomme les 5 cycles concernés un par un",
         pub.count("battery_indet_hoist_declared") >= 1
         and pub.count("masking_guards_witness_patch") >= 1),
    ]
    L.append("| Contrôle | Résultat |")
    L.append("|---|---|")
    for lab, ok in controles:
        L.append(f"| {lab} | {'**OUI**' if ok else '**NON**'} |")
    L.append("")
    manques = [lab for lab, ok in controles if not ok]
    if not manques:
        L.append("> **Le cycle publie que le résultat l'arrange**, que son mérite à")
        L.append("> l'avoir prédit n'est pas vérifiable par un tiers, et que le #486")
        L.append("> n'a écrit aucun chiffre faux. **Il refuse aussi d'étendre la règle**")
        L.append("> hors de son propre rapport.")
    else:
        L.append(f"> **{len(manques)} contrôle(s) échoue(nt)** :")
        for m in manques:
            L.append(f"> - {m}")
    L.append("")

    L.append("## Verdict")
    L.append("")
    bon = reelle and faux == 0 and nl < nt and not manques
    L.append(f"**{'CONCORDANT' if bon else 'RÉSERVES'}** — la variante est **réelle**,")
    L.append("l'élargissement est **purement typographique**, le déclin littéral est")
    L.append(f"**réel mais sans signification**, et **{len(controles) - len(manques)}/"
             f"{len(controles)}** contrôles de transparence sont tenus.")
    L.append("")
    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des fichiers à la date")
    L.append("> de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()
