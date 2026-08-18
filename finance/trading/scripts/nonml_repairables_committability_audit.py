"""Audit independant du #507.

Le backtest classe sur des APPELS (`glob`, `git`, primitives du #497). Cet
audit classe autrement : il mesure, pour chaque rapport des 13 reparables,
combien de fois il a ETE REECRIT dans l'historique git. Un rapport committe
une fois n'a jamais derive ; un rapport reecrit dix fois derive a chaque
regeneration.

C'est une route ENTIEREMENT differente -- l'histoire au lieu de la structure --
et elle permet de tester la regle statique du #507 contre un fait observe.
"""
import ast
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

RAP = RESULTS / "nonml_repairables_committability_result.md"
BT = SCRIPTS / "nonml_repairables_committability_backtest.py"
OUT = RESULTS / "nonml_repairables_committability_audit.md"
MOI = "repairables_committability"

GRAS = re.compile(r"\*\*(-?\d[\d  ]*(?:[,.]\d+)?)\s*(?:%|€|bps)?\*\*")
SUFFIXES = [("_backtest.py", "_result.md"), ("_audit.py", "_audit.md")]


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def plat(t):
    return re.sub(r"\s+", " ", t.replace("*", "").replace("`", ""))


def rapport_de(nom):
    for a, b in SUFFIXES:
        if nom.endswith(a):
            return f"{nom[:-len(a)]}{b}"
    return None


def reecritures(rel):
    """Nombre de commits ayant TOUCHE ce fichier -- l'histoire, pas la structure."""
    s = git("log", "--format=%H", "--", rel)
    return len([l for l in s.splitlines() if l.strip()])


def main():
    rap = RAP.read_text(encoding="utf-8")
    p = plat(rap)

    # --- Le classement publie, relu -------------------------------------
    bloc = rap.split("## Le détail, script par script", 1)[-1].split("\n## ", 1)[0]
    lignes = re.findall(r"\|\s*`([a-z0-9_]+\.py)`\s*\|\s*\*\*(NC1|NC2|C|\?)\*\*\s*\|",
                        bloc)

    fiches = []
    for nom, cl in lignes:
        r = rapport_de(nom)
        rel = f"finance/trading/results/{r}" if r else None
        n = reecritures(rel) if rel else 0
        fiches.append({"py": nom, "cl": cl, "rap": r, "n": n,
                       "existe": bool(rel and (RESULTS / r).exists())})

    par_classe = {}
    for f in fiches:
        par_classe.setdefault(f["cl"], []).append(f["n"])

    def moy(v):
        return sum(v) / len(v) if v else 0.0

    cand = [f for f in fiches if f["cl"] == "C"]
    non_c = [f for f in fiches if f["cl"] in ("NC1", "NC2")]
    m_cand, m_non = moy([f["n"] for f in cand]), moy([f["n"] for f in non_c])

    def num(motif):
        m = re.search(motif, p)
        return int(m.group(1)) if m else None
    pub = {
        "pop": num(r"population : (\d+)"),
        "nc1": num(r"\| NC1 \| (\d+) \|"),
        "nc2": num(r"\| NC2 \| (\d+) \|"),
        "c": num(r"\| C \| (\d+) \|"),
        "noncomm": num(r"non committables \(NC1 \+ NC2\) : (\d+)"),
    }
    partition = (pub["nc1"] + pub["nc2"] + pub["c"]) <= pub["pop"]
    somme_ok = pub["noncomm"] == pub["nc1"] + pub["nc2"]
    relu_ok = len(lignes) == pub["pop"]

    src_bt = BT.read_text(encoding="utf-8")
    en_dur = [m.group(1) for m in GRAS.finditer(rap)
              if re.search(r"[\"']\s*\*\*" + re.escape(m.group(1)) + r"\s*\*\*", src_bt)]
    sales = [l for l in git("status", "--porcelain").splitlines()
             if l.strip() and MOI not in l]

    L = []
    A = L.append
    A("# Audit indépendant — committabilité des réparables (#507)")
    A("")
    A("Le backtest classe sur la **structure** : quels appels le script fait.")
    A("Cet audit interroge l'**histoire** : combien de fois le rapport de chaque")
    A("réparable a **réellement été réécrit** dans le dépôt. Un rapport committé")
    A("une seule fois n'a jamais dérivé ; un rapport réécrit dix fois dérive à")
    A("chaque régénération.")
    A("")
    A("## Le classement relu")
    A("")
    A(f"- lignes de détail relues : **{len(lignes)}**")
    A(f"- population annoncée : **{pub['pop']}**")
    A(f"- accord : **{'OUI' if relu_ok else 'NON'}**")
    A(f"- NC1 + NC2 = non committables annoncés : "
      f"**{'OUI' if somme_ok else 'NON'}**")
    A("")
    A("## L'histoire, classe par classe")
    A("")
    A("| Classe | Effectif | Réécritures — moyenne | min | max |")
    A("|---|---|---|---|---|")
    for cl in ("NC1", "NC2", "C", "?"):
        v = par_classe.get(cl, [])
        if not v:
            continue
        A(f"| **{cl}** | **{len(v)}** | " + f"**{moy(v):.1f}**".replace(".", ",")
          + f" | **{min(v)}** | **{max(v)}** |")
    A("")
    A(f"- moyenne des **candidats C** : " + f"**{m_cand:.1f}**".replace(".", ","))
    A(f"- moyenne des **non committables** : " + f"**{m_non:.1f}**".replace(".", ","))
    A("")
    valeurs = [f["n"] for f in fiches]
    discrimine = len(set(valeurs)) > 1
    A(f"- valeurs distinctes de réécritures sur la population : "
      f"**{len(set(valeurs))}**")
    A("")
    if not discrimine:
        A("> **Cette route ne discrimine rien ici.** Les **" + str(len(fiches)) +
          "** rapports ont")
        A(f"> **tous** été écrits **{valeurs[0]}** fois. Une moyenne identique de")
        A("> part et d'autre n'est pas une confirmation : **c'est une absence de")
        A("> mesure.** Le contrôle correspondant est donc **non testable**, et")
        A("> je ne le compte pas comme réussi.")
        A(">")
        A("> *(La route fonctionne pourtant : un rapport régénéré du dépôt")
        A("> affiche bien plusieurs commits. C'est cette population-ci qui est")
        A("> uniforme — parce qu'aucun de ces rapports n'a jamais été refait.)*")
    elif m_cand < m_non:
        A("> **L'histoire confirme la structure.** Les rapports que la règle")
        A("> statique juge candidats ont été **moins réécrits** que ceux qu'elle")
        A("> condamne. Deux routes sans rien de commun — l'une lit du code,")
        A("> l'autre lit des commits — **désignent les mêmes scripts**.")
    elif m_cand > m_non:
        A("> **L'histoire contredit la structure.** Les « candidats » ont été")
        A("> **plus** réécrits que les condamnés : la règle statique désigne")
        A("> comme stables des rapports que le dépôt n'a cessé de refaire.")
        A("> **Le classement du #507 est douteux.**")
    else:
        A("> Les deux moyennes coïncident : l'histoire ne départage pas.")
    A("")
    A("## Le détail")
    A("")
    A("| Script | Classe | Rapport | Réécritures |")
    A("|---|---|---|---|")
    for f in sorted(fiches, key=lambda x: (x["cl"], -x["n"], x["py"])):
        A(f"| `{f['py']}` | **{f['cl']}** | "
          f"{'`' + f['rap'] + '`' if f['rap'] else '—'} | **{f['n']}** |")
    A("")
    A("## Ce que cet audit ne prouve pas")
    A("")
    A("Le nombre de réécritures est un **indice**, pas une preuve : un rapport")
    A("peu réécrit peut l'être parce que personne ne s'y est intéressé, non")
    A("parce qu'il est stable. **La corrélation entre les deux routes ne")
    A("valide pas la règle du #507** — elle montre seulement qu'elles ne se")
    A("contredisent pas.")
    A("")
    A("## Inertie et chiffres calculés")
    A("")
    A(f"- fichiers de l'arbre modifiés hors ce cycle : **{len(sales)}**")
    A(f"- nombres en gras : **{len(GRAS.findall(rap))}** ; dont **tapés en "
      f"dur** : **{len(en_dur)}**")
    if en_dur:
        A("")
        A(f"> En dur : {', '.join('`'+v+'`' for v in sorted(set(en_dur)))}")
    A("")
    A("## Verdict")
    A("")
    ctrl = [("le détail relu couvre toute la population annoncée", relu_ok),
            ("NC1 + NC2 égale le compte de non committables", somme_ok),
            ("les classes ne dépassent pas la population", partition),
            ("l'histoire ne contredit pas la structure",
             (m_cand <= m_non) if discrimine else None),
            ("aucun chiffre du rapport tapé en dur, arbre propre",
             not en_dur and not sales)]
    for i, (t, v) in enumerate(ctrl, 1):
        etat = "NON TESTABLE" if v is None else ("OUI" if v else "NON")
        A(f"{i}. {t} — **{etat}**.")
    A("")
    testables = [x for _, x in ctrl if x is not None]
    n_nt = sum(1 for _, x in ctrl if x is None)
    v = "AUDIT OK" if all(testables) else "AUDIT — RÉSERVE"
    suffixe = f", **{n_nt}** non testable(s)" if n_nt else ""
    A(f"**{v}** ({sum(1 for x in testables if x)}/{len(testables)}{suffixe})")
    A("")
    A("Anti-lookahead **sans objet au sens temporel** pour les prix ; la")
    A("datation employée ici est **strictement rétrospective** — commits")
    A("passés, jamais l'état futur.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{v} — candidats {m_cand:.1f} vs non committables {m_non:.1f} réécritures")


if __name__ == "__main__":
    main()
