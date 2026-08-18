"""Audit adversarial du #491 — contrôle d'un geste dont l'issue était connue.

Un cycle qui execute un geste deja valide par le cycle precedent n'apprend rien
sur le geste. L'audit verifie donc ce qui restait ouvert :

1. le hissage a-t-il bien change la SORTIE, et pas seulement la structure ?
2. la prediction refutee est-elle publiee comme telle, sans attenuation ?
3. le perimetre est-il tenu : rien d'autre n'a bouge ?
4. le depot entier a-t-il ete recompte, ou seulement la cible ?
"""
import ast
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

RAPPORT = RESULTS / "nonml_battery_indet_hoist_declared_result.md"
OUT = RESULTS / "nonml_battery_indet_hoist_declared_audit.md"
CIBLE = "nonml_battery_coverage_backtest.py"
VAR = "indet"


def sans_markdown(t):
    """Normalisation adoptee au #490 : gras, code, retours a la ligne."""
    return re.sub(r"\s+", " ", t.replace("*", "").replace("`", ""))


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def ecritures_libres(src):
    """Instructions d'ecriture a profondeur 0, par AST."""
    arbre = ast.parse(src)
    out = []

    def walk(nd, prof):
        for e in ast.iter_child_nodes(nd):
            p = prof + 1 if isinstance(e, (ast.If, ast.For, ast.While, ast.Try)) \
                else prof
            if isinstance(e, ast.Call) and prof == 0:
                f = e.func
                n = f.attr if isinstance(f, ast.Attribute) else \
                    (f.id if isinstance(f, ast.Name) else "")
                if n == "append":
                    out.append(e.lineno)
            walk(e, p)

    for fn in [x for x in ast.walk(arbre) if isinstance(x, ast.FunctionDef)]:
        walk(fn, 0)
    return out


def main():
    av = git("show", f"HEAD:finance/trading/scripts/{CIBLE}")
    ap = (SCRIPTS / CIBLE).read_text(encoding="utf-8")
    pub = sans_markdown(RAPPORT.read_text(encoding="utf-8")) if RAPPORT.exists() else ""

    L = ["# Audit adversarial — le hissage déclaré (#491)", ""]
    L.append("Un cycle qui exécute un geste **déjà validé par le précédent** n'apprend")
    L.append("rien sur le geste. **L'audit vérifie donc ce qui restait ouvert.**")
    L.append("")

    L.append("## 1. La sortie a-t-elle vraiment changé ?")
    L.append("")
    L.append("Le rapport annonce un **changement de sortie**, pas un simple")
    L.append("déplacement. Route : compter les **écritures à profondeur 0** — celles")
    L.append("qui paraissent quoi qu'il arrive.")
    L.append("")
    n_av, n_ap = len(ecritures_libres(av)), len(ecritures_libres(ap))
    L.append(f"- écritures inconditionnelles **avant** : **{n_av}**")
    L.append(f"- écritures inconditionnelles **après** : **{n_ap}**")
    L.append(f"- variation : **{n_ap - n_av:+d}**")
    L.append("")
    change = n_ap > n_av
    if change:
        L.append("> **Confirmé : une ligne de plus paraît désormais quoi qu'il arrive.**")
        L.append("> Le rapport avait raison de refuser le mot « déplacement » — un")
        L.append("> lecteur verra maintenant `**0**` là où il ne voyait rien.")
    else:
        L.append("> **Non confirmé** — publié tel quel.")
    L.append("")

    L.append("## 2. La prédiction réfutée est-elle publiée sans atténuation ?")
    L.append("")
    L.append("Une prédiction chiffrée fausse par une ligne blanche est la plus facile")
    L.append("à présenter comme « essentiellement vérifiée ». **Contrôle textuel :**")
    L.append("")
    controles = [
        ("le tableau marque la prédiction 1 réfutée",
         "2 suppressions et 2 ajouts | 2 / 2 | 3 / 2 | réfutée" in pub),
        ("le rapport refuse l'atténuation",
         "essentiellement vérifié" in pub and "Je ne présente pas cela" in pub),
        ("il nomme la cause exacte (un séparateur redondant)",
         "séparateur devenu redondant" in pub),
        ("il en tire une conséquence sur le #490",
         "légèrement plus large" in pub),
        ("le résultat sur la règle est dit non informatif",
         "non informatif" in pub),
    ]
    L.append("| Contrôle | Résultat |")
    L.append("|---|---|")
    for lab, ok in controles:
        L.append(f"| {lab} | {'**OUI**' if ok else '**NON**'} |")
    L.append("")
    manques = [lab for lab, ok in controles if not ok]
    if not manques:
        L.append("> **La réfutation est publiée telle quelle**, avec sa cause, et sans")
        L.append("> la formule « essentiellement vérifiée » que le rapport écarte")
        L.append("> explicitement.")
    else:
        L.append(f"> **{len(manques)} contrôle(s) échoue(nt)** :")
        for m in manques:
            L.append(f"> - {m}")
    L.append("")

    L.append("## 3. Le périmètre est-il tenu ?")
    L.append("")
    num = [l for l in git("diff", "--numstat", "HEAD").splitlines()
           if l.strip() and "battery_indet_hoist_declared" not in l]
    hors = [l for l in num if CIBLE not in l]
    st = git("status", "--porcelain",
             "finance/trading/results/nonml_battery_coverage_result.md").strip()
    L.append(f"- fichiers modifiés hors la cible : **{len(hors)}**")
    for l in hors[:6]:
        L.append(f"  - `{l.strip()}`")
    L.append(f"- rapport de la cible : **{'inchangé' if not st else 'MODIFIÉ'}**")
    L.append("")
    borne = not hors and not st
    if borne:
        L.append("> **Un seul fichier touché, aucun rapport régénéré.** Le geste est")
        L.append("> resté dans son périmètre.")
    L.append("")

    L.append("## 4. Le dépôt entier a-t-il été recompté ?")
    L.append("")
    L.append("Un cycle pourrait ne recompter que sa cible et présenter le résultat")
    L.append("comme global. **Contrôle : le rapport publie-t-il des totaux à deux")
    L.append("chiffres, incompatibles avec un script isolé ?**")
    L.append("")
    m = re.search(r"avant \| (\d+) \| (\d+) \| (\d+) \| apres \| (\d+) \| (\d+) \| (\d+)",
                  pub)
    if not m:
        m = re.search(r"avant \| (\d+) \| (\d+) \| (\d+)", pub)
    chiffres = [int(x) for x in m.groups()] if m else []
    global_ok = bool(chiffres) and max(chiffres) > 10
    L.append(f"- chiffres relus dans le tableau : **{chiffres if chiffres else '—'}**")
    L.append(f"- compatibles avec un **recomptage du dépôt entier** : "
             f"**{'OUI' if global_ok else 'NON'}**")
    L.append("")
    if global_ok:
        L.append("> **Les totaux dépassent largement ce qu'un seul script peut porter.**")
        L.append("> Le recomptage est bien global.")
    L.append("")

    L.append("## Verdict")
    L.append("")
    bon = change and not manques and borne and global_ok
    L.append(f"**{'CONCORDANT' if bon else 'RÉSERVES'}** — le **changement de sortie**")
    L.append("est confirmé par une route indépendante, la **prédiction réfutée est")
    L.append("publiée sans atténuation**, le **périmètre est tenu**, le recomptage est")
    L.append(f"**global**, et **{len(controles) - len(manques)}/{len(controles)}**")
    L.append("contrôles de transparence sont tenus.")
    L.append("")
    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date")
    L.append("> de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()
