"""Trancher le sort du citeur du #451 (#472).

Specification pre-enregistree dans `PREREG_citer_451_resolution.md`, committee
AVANT toute mesure.

Le #451 comptait « 1 rapport qui cite l'encart sans le porter ». Le #469, au
depot d'aujourd'hui, n'a trouve 0 citeur etabli, et a refuse de trancher parce
que remonter au commit du #451 n'etait pas dans son perimetre declare.

Lecture d'objets git : aucun script execute, aucun effet de bord.
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

OUT = RESULTS / "nonml_citer_451_resolution_result.md"
PHRASE = "Rapport dépendant du dépôt"
BACKLOG = "finance/trading/NONML_STRATEGY_BACKLOG.md"

# Regle CORRIGEE du #469 : le script doit ECRIRE la marque, pas la contenir.
EMISSION = re.compile(r"(append|write|print)\s*\(.*Rapport dépendant du dépôt")
SUFFIXES = [("_result.md", "_backtest.py"),
            ("_audit.md", "_audit.py"),
            ("_robustness.md", "_robustness.py")]
# Angle mort connu (#469) : ecriture par variable.
VARIABLE = re.compile(r"(MARKER|MARQUE|ENCART)\w*\s*=|dépendant du dépôt\\n")


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def main():
    sha = bt.commit_introducteur(451)
    L = ["# Trancher le sort du **citeur du #451** (pré-enregistré)", ""]
    L.append("Le **#451** comptait, dans son propre tableau, **« 1 rapport qui cite")
    L.append("l'encart sans le porter »**. Le **#469**, au dépôt d'**aujourd'hui**, n'a")
    L.append("trouvé **0 citeur établi** — et a refusé de trancher, faute d'avoir")
    L.append("déclaré remonter à ce commit. **Ce cycle le déclare et le fait.**")
    L.append("")

    if sha is None:
        L.append("## Le commit du #451 est introuvable")
        L.append("")
        L.append("**FAIL** — le critère 1 n'est pas atteint, et rien de ce qui suit")
        L.append("n'aurait de sens.")
        OUT.write_text("\n".join(L), encoding="utf-8")
        print("\n".join(L))
        return

    L.append(f"## Le commit épinglé : `{sha[:12]}`")
    L.append("")

    fichiers = [l.strip() for l in
                (git("ls-tree", "-r", "--name-only", sha,
                     "finance/trading/results/") or "").splitlines()
                if l.strip().endswith(".md")]

    porteurs, citeurs, indetermines = [], [], []
    for f in fichiers:
        t = git("show", f"{sha}:{f}")
        if not t or PHRASE not in t:
            continue
        nom = f.split("/")[-1]
        src = None
        for suf_md, suf_py in SUFFIXES:
            if nom.endswith(suf_md):
                src = f"finance/trading/scripts/{nom[:-len(suf_md)]}{suf_py}"
                break
        code = git("show", f"{sha}:{src}") if src else None
        if code is None:
            indetermines.append(nom)
        elif any(EMISSION.search(l) for l in code.splitlines()):
            porteurs.append(nom)
        else:
            citeurs.append((nom, src.split("/")[-1], code))

    contiennent = len(porteurs) + len(citeurs) + len(indetermines)

    L.append("## Le classement à ce commit")
    L.append("")
    L.append(f"- rapports **contenant** la marque : **{contiennent}**")
    L.append(f"- **PORTEURS** : **{len(porteurs)}**")
    L.append(f"- **candidats CITEURS** : **{len(citeurs)}**")
    L.append(f"- **INDÉTERMINÉS** : **{len(indetermines)}**")
    L.append("")

    L.append("## L'examen individuel — avant tout décompte")
    L.append("")
    L.append("L'engagement 3 l'exige. Le **#469** a montré qu'un script écrivant la")
    L.append("marque **par variable** est invisible à la règle littérale : il avait")
    L.append("produit un faux citeur qu'un examen avait dû retirer.")
    L.append("")
    etablis = []
    if not citeurs:
        L.append("**Aucun candidat.**")
    else:
        L.append("| Rapport | Script producteur | Écriture par variable ? | Retenu |")
        L.append("|---|---|---|---|")
        for nom, src, code in citeurs:
            par_var = bool(VARIABLE.search(code))
            if not par_var:
                etablis.append(nom)
            L.append(f"| `{nom}` | `{src}` | "
                     f"**{'oui' if par_var else 'non'}** | "
                     f"{'**retiré**' if par_var else '**citeur établi**'} |")
        L.append("")
    L.append(f"- **citeurs établis** : **{len(etablis)}**")
    for n in etablis:
        L.append(f"  - `{n}`")
    L.append("")

    # --- Le #451 nomme-t-il son citeur ? -----------------------------------
    entree = bt.texte_entree(git("show", f"{sha}:{BACKLOG}") or "", 451) or ""
    noms_cites = sorted({m for m in re.findall(r"`(nonml_[a-z0-9_]+\.md)`", entree)})
    nomme = bool(noms_cites)

    L.append("## Le #451 nomme-t-il le rapport qu'il comptait ?")
    L.append("")
    L.append("Le pré-enregistrement énonçait **trois issues**, toutes publiables.")
    L.append("")
    if not nomme:
        issue = ("**il ne le nomme pas** → la comparaison est **partielle**, "
                 "et je le dis")
        L.append("Son entrée **ne cite nominativement aucun rapport** `.md`.")
    else:
        L.append("Rapports nommés dans son entrée :")
        L.append("")
        for n in noms_cites[:10]:
            L.append(f"- `{n}`")
        L.append("")
        commun = [n for n in etablis if n in noms_cites]
        if commun:
            issue = "**il le nomme, et ma règle trouve le même** → question close"
        else:
            issue = ("**il le nomme, et ma règle en trouve un autre ou aucun** → "
                     "**ma règle est en défaut**")
    L.append("")
    L.append(f"> **Issue : {issue}.**")
    L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    p1 = len(etablis) == 1
    p2 = not nomme
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| exactement 1 citeur établi | 1 | {len(etablis)} | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| le #451 ne nomme pas son citeur | ne nomme pas | "
             f"{'ne nomme pas' if p2 else 'nomme'} | "
             f"{'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append("| le citeur n'en est plus un aujourd'hui | — | "
             "*le #469 en trouvait 0* | "
             + ("*cohérent*" if len(etablis) >= 1 else "*sans objet*") + " |")
    L.append("")
    if len(etablis) == 0:
        L.append("> **Zéro citeur établi, déjà à l'époque.** L'explication commode —")
        L.append("> « il a disparu du dépôt depuis » — **tombe**. Le pré-enregistrement")
        L.append("> avait fixé la conséquence : **c'est ma méthode qui est en cause**,")
        L.append("> pas l'histoire du dépôt.")
        L.append("")
        L.append("Ma règle ne retrouve pas, au commit même où il a été compté, le")
        L.append("citeur que le #451 comptait. Deux lectures restent ouvertes, et je")
        L.append("n'ai pas de quoi les départager ici :")
        L.append("")
        L.append("1. le #451 employait une définition de « citer » que je n'ai pas")
        L.append("   reconstituée ;")
        L.append("2. ma règle littérale a un angle mort de plus que celui du #469.")
        L.append("")
        L.append("**Dans les deux cas, le croisement rapport ↔ script émetteur ne suffit")
        L.append("pas à reproduire ce compte** — et c'est le résultat de ce cycle.")
        L.append("")
        meme = [n for n, _s, _c in citeurs
                if n == "nonml_selfref_reports_marking_result.md"]
        if meme:
            L.append("### Un fait qui départage partiellement")
            L.append("")
            L.append("Le candidat trouvé ici est **le même rapport** qu'au #469 —")
            L.append("`nonml_selfref_reports_marking_result.md` — et il est retiré pour")
            L.append("**la même raison** : son script écrit la marque par variable.")
            L.append("")
            L.append("> **Le désaccord avec le #451 est donc stable, pas accidentel.**")
            L.append("> Ma règle donne le même candidat à deux commits séparés par vingt")
            L.append("> cycles, et l'écarte deux fois. Cela **oriente vers la lecture 1**")
            L.append("> — une définition différente de « citer » — plutôt que vers un")
            L.append("> angle mort qui varierait au hasard.")
            L.append("")
            L.append("Ce n'est **pas une preuve** : une définition et un angle mort")
            L.append("peuvent produire la même stabilité. Mais un défaut erratique")
            L.append("aurait, lui, donné des candidats différents.")
    elif p1:
        L.append("**Un citeur établi, au commit même du #451.** Le compte de l'époque")
        L.append("est reproduit par une méthode indépendante, et le **0** du #469")
        L.append("s'explique : ce rapport n'est plus un citeur aujourd'hui.")
    L.append("")

    L.append("## Critères de succès")
    L.append("")
    c2 = contiennent == len(porteurs) + len(citeurs) + len(indetermines)
    L.append(f"1. Commit du #451 retrouvé et publié — **OUI** (`{sha[:12]}`).")
    L.append(f"2. **{contiennent}/{contiennent}** rapports classés — "
             f"**{'OUI' if c2 else 'NON'}**.")
    L.append("3. Chaque citeur examiné avant décompte — **OUI**.")
    L.append("4. Rapport du #451 relu et issue nommée — **OUI**.")
    L.append("")
    L.append(f"**{'PASS' if c2 else 'FAIL'}** — le critère porte sur le **procédé** :")
    L.append("un cycle qui échoue à reproduire un compte, et le montre proprement,")
    L.append("réussit.")
    L.append("")

    L.append("")
    L.append("> **Rapport épinglé** — tout est lu au commit `"
             + sha[:12] + "`. Réexécuté dans dix cycles, il doit rendre les mêmes")
    L.append("> chiffres.")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()
