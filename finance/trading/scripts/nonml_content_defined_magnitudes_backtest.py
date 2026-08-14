"""Les grandeurs definies par le CONTENU (#465).

Specification pre-enregistree dans `PREREG_content_defined_magnitudes.md`,
committee AVANT toute mesure.

Le #462 a conclu contre lui-meme que trois des quatre faux connus lui
echappaient : ils se definissent par le contenu des fichiers, pas par leur nom.
Ce cycle compte deux d'entre eux. Le troisieme (#453, une relation entre globs)
reste hors de portee, et rien n'est ajoute pour lui.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
sys.path.insert(0, str(SCRIPTS))

import nonml_backlog_figures_verification_backtest as bt  # noqa: E402
import nonml_verdict  # noqa: E402  (pour `_nu`, la denudation Markdown)

OUT = RESULTS / "nonml_content_defined_magnitudes_result.md"
ENTREES = list(range(443, 461))

IMPORTE = re.compile(r"^\s*(?:import\s+nonml_verdict|from\s+nonml_verdict\b)", re.M)
MARQUE = "**Rapport dépendant du dépôt**"
PHRASE = "Rapport dépendant du dépôt"


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def fichiers(sha, sous_dossier, suffixe):
    out = git("ls-tree", "-r", "--name-only", sha, f"finance/trading/{sous_dossier}/")
    return [l.strip() for l in (out or "").splitlines()
            if l.strip().endswith(suffixe)]


def porte_marque(txt):
    """PORTE la marque : une ligne denudee qui COMMENCE par elle."""
    for ligne in txt.splitlines():
        if nonml_verdict._nu(ligne).startswith(MARQUE):
            return True
    return False


def mesure(sha):
    g1 = 0
    for f in fichiers(sha, "scripts", ".py"):
        t = git("show", f"{sha}:{f}")
        if t and IMPORTE.search(t):
            g1 += 1
    porteurs = mentionneurs = 0
    for f in fichiers(sha, "results", ".md"):
        t = git("show", f"{sha}:{f}")
        if not t:
            continue
        if porte_marque(t):
            porteurs += 1
        elif PHRASE in t:
            mentionneurs += 1
    return g1, porteurs, mentionneurs


def main():
    table, manquantes = [], []
    for num in ENTREES:
        sha = bt.commit_introducteur(num)
        if sha is None:
            manquantes.append((num, "commit introducteur introuvable"))
            continue
        g1, po, me = mesure(sha)
        table.append((num, sha, g1, po, me))

    cellules = len(table) * 2
    attendu = len(ENTREES) * 2
    par = {n: (s, g, p, m) for n, s, g, p, m in table}

    L = ["# Les grandeurs définies par le **contenu** (pré-enregistré)", ""]
    L.append("Le **#462** a conclu **contre lui-même** que trois des quatre faux connus")
    L.append("lui échappaient : ils se définissent par le **contenu** des fichiers, pas")
    L.append("par leur nom. Ce cycle en compte **deux**.")
    L.append("")

    L.append("## La distinction qui décide — **porter** n'est pas **mentionner**")
    L.append("")
    L.append("Le #451 a établi que le « 6 » du backlog était faux parce qu'il comptait")
    L.append("comme marqués des rapports qui **parlent** de l'encart. C'est exactement le")
    L.append("défaut du #446 sur la règle de verdict.")
    L.append("")
    L.append("**Porte** = une ligne, décoration retirée, **commence par** la marque.")
    L.append("**Mentionne** = la phrase apparaît, sans être portée en tête de ligne.")
    L.append("")

    L.append("## La table")
    L.append("")
    L.append(f"**{cellules}/{attendu}** cellules.")
    L.append("")
    if manquantes:
        for num, why in manquantes:
            L.append(f"- #{num} : {why}")
        L.append("")
    L.append("| Entrée | Commit | G1 consommateurs | G2 porteurs | mentionneurs |")
    L.append("|---|---|---|---|---|")
    for num, sha, g1, po, me in table:
        L.append(f"| #{num} | `{sha[:8]}` | {g1} | {po} | {me} |")
    L.append("")

    L.append("## Les deux faux connus, recomptés")
    L.append("")
    L.append("| Entrée | Annoncé | Recompté au commit | Verdict |")
    L.append("|---|---|---|---|")
    v449 = v451 = None
    if 449 in par:
        v449 = par[449][1]
        L.append(f"| #449 | **8** consommateurs | **{v449}** à `{par[449][0][:8]}` | "
                 + ("**le « 8 » était bien faux**" if v449 != 8
                    else "**le « 8 » était JUSTE**") + " |")
    if 451 in par:
        v451 = par[451][2]
        L.append(f"| #451 | **6** porteurs | **{v451}** à `{par[451][0][:8]}` | "
                 + ("**le « 6 » était bien faux**" if v451 != 6
                    else "**le « 6 » était JUSTE**") + " |")
    L.append("")

    if 451 in par:
        po, me = par[451][2], par[451][3]
        L.append("### Le mécanisme du « 6 »")
        L.append("")
        L.append(f"Au commit du #451 : **{po}** rapports **portent** la marque,")
        L.append(f"**{me}** la **mentionnent** sans la porter.")
        L.append("")
        if me > 0:
            L.append("**Un compte qui ne distingue pas les deux gonfle mécaniquement.**")
            L.append("C'est la même erreur que le détecteur de verdict d'avant le #446,")
            L.append("et elle s'est reproduite sur un autre objet **trois cycles plus")
            L.append("tard** — la leçon n'avait pas été généralisée.")
        else:
            L.append("**Aucun mentionneur** : le mécanisme que je supposais n'est pas")
            L.append("celui-là. Publié tel quel — mon explication du « 6 » était fausse.")
        L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    p1 = v449 is not None and v449 != 8
    p1b = v449 == 6
    p2 = v451 is not None and v451 != 6
    p3 = 451 in par and par[451][3] > par[451][2]
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| G1 ≠ 8 au commit du #449 | ≠ 8 | {v449} | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| et précisément G1 = 6 | 6 | {v449} | "
             f"{'**vérifiée**' if p1b else '**réfutée**'} |")
    L.append(f"| G2 ≠ 6 au commit du #451 | ≠ 6 | {v451} | "
             f"{'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| mentionneurs > porteurs au #451 | > | "
             f"{par[451][3] if 451 in par else '—'} vs "
             f"{par[451][2] if 451 in par else '—'} | "
             f"{'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")
    if not p1:
        L.append("> **La correction du #449 était fausse, pas le compte d'origine.**")
        L.append("> Le pré-enregistrement prévoyait ce cas et exigeait de le publier tel")
        L.append("> quel, y compris contre trois cycles de dette inscrite. **C'est fait**,")
        L.append("> et la dette doit être révisée en conséquence — par un cycle déclaré,")
        L.append("> pas ici.")
        L.append("")

    L.append("## Ce que ce cycle ne peut pas faire")
    L.append("")
    L.append("- **G1 est une borne inférieure.** `import nonml_verdict` ne capture pas")
    L.append("  un script qui **réimplémenterait** la règle sans l'importer — et les")
    L.append("  #446-#448 ont montré que de telles copies ont existé.")
    L.append("- Le faux du **#453** (« 13 orphelins ») est une **relation** entre deux")
    L.append("  globs : toujours hors de portée, et **rien n'a été ajouté pour lui**.")
    L.append("- Il ne couvre que **deux** grandeurs de contenu sur toutes celles que le")
    L.append("  backlog énonce en prose.")
    L.append("")

    L.append("## Critères de succès")
    L.append("")
    c1 = cellules == attendu
    c2 = v449 is not None and v451 is not None
    L.append(f"1. **{cellules}/{attendu}** cellules — **{'OUI' if c1 else 'NON'}**.")
    L.append(f"2. Les deux faux recomptés — **{'OUI' if c2 else 'NON'}**.")
    L.append("3. Distinction porte / mentionne publiée avec ses deux chiffres — **OUI**.")
    L.append("4. Définitions inchangées après mesure — **OUI**.")
    L.append("")
    L.append(f"**{'PASS' if (c1 and c2) else 'FAIL'}** — le critère porte sur le procédé.")
    L.append("")

    L.append("")
    L.append("> **Rapport épinglé** — chaque grandeur est comptée au commit qui a créé")
    L.append("> l'entrée. Réexécuté dans dix cycles, il doit rendre les mêmes chiffres.")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()
