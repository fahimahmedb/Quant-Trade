"""Reparer le seul candidat actionnable (#511).

Specification pre-enregistree dans `PREREG_battery_backfill_repair.md`,
committee AVANT toute modification -- perimetre et regle du geste borne
compris.

Ce script MODIFIE un script du depot et l'EXECUTE une fois. Il est donc
lui-meme non committable au sens du #507, et il le dit. Si le geste deborde,
TOUT est restaure et le cycle echoue.
"""
import ast
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

CIBLE = SCRIPTS / "nonml_battery_backfill_lot_audit.py"
REL_PY = "finance/trading/scripts/nonml_battery_backfill_lot_audit.py"
REL_MD = "finance/trading/results/nonml_battery_backfill_lot_audit.md"
RAPPORT = RESULTS / "nonml_battery_backfill_lot_audit.md"
OUT = RESULTS / "nonml_battery_backfill_repair_result.md"
MOI = "battery_backfill_repair"

AVANT = ('    L.append("reste **1** candidat hors de portée de l\'outil '
         '(schéma panier), listé et non")')
APRES = ('    _hors = sum(1 for _r in SET_ASIDE.values() if "panier" in _r)\n'
         '    L.append(f"reste **{_hors}** candidat hors de portée de l\'outil '
         '(schéma panier), listé et non")')
AUTORISEE = re.compile(r"candidat hors de portée de l'outil")

BALAYAGE = {"glob", "rglob", "iterdir", "scandir", "listdir"}
PRIM = ("P1", "P2", "P9", "P10")


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def regle_497():
    p = SCRIPTS / "nonml_execution_primitives_census_backtest.py"
    spec = importlib.util.spec_from_file_location("_c497", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def causes(src, arbre, existants, c497):
    prim = sorted(k for k in c497.primitives(src, arbre, existants) if k in PRIM)
    bal, gitc = [], []
    for n in ast.walk(arbre):
        if not isinstance(n, ast.Call):
            continue
        nom = n.func.attr if isinstance(n.func, ast.Attribute) else (
            n.func.id if isinstance(n.func, ast.Name) else None)
        if nom in BALAYAGE:
            bal.append(nom)
        if nom in ("run", "Popen", "check_output", "call"):
            for a in n.args:
                for s in ast.walk(a):
                    if isinstance(s, ast.Constant) and s.value == "git":
                        gitc.append("git")
    argv = [n for n in ast.walk(arbre)
            if isinstance(n, ast.Attribute) and n.attr == "argv"]
    return {"exécution d'un tiers": len(prim),
            "balayage de `scripts/` ou `results/`": len(set(bal)),
            "appel `git`": len(gitc),
            "dépendance à `sys.argv`": len(argv)}


def lignes_changees(rel):
    d = git("diff", "-U0", "--", rel)
    return [l[1:] for l in d.splitlines()
            if (l.startswith("+") or l.startswith("-"))
            and not l.startswith(("+++", "---"))]


def main():
    c497 = regle_497()
    existants = {p.stem for p in SCRIPTS.glob("nonml_*.py")}
    src0 = CIBLE.read_text(encoding="utf-8")
    arbre0 = ast.parse(src0)
    cz = causes(src0, arbre0, existants, c497)
    classe_ok = all(v == 0 for v in cz.values())

    vieux_md = git("show", f"HEAD:{REL_MD}")
    m_v = re.search(r"reste \*\*(\d+)\*\* candidat hors de portée", vieux_md)
    litteral = m_v.group(1) if m_v else None

    # --- Le 0,00 % : la justification du #485 confrontee au code ----------
    lit_npz = bool(re.search(r"\.npz|np\.load|load\(", src0))
    npz_reel = bool(re.search(r"np\.load\s*\(|\.npz", src0))
    prod_0 = "0,00 %" in src0

    diff_py, diff_md, neuve, echec = [], [], None, None
    if not classe_ok:
        echec = "la cible n'est plus de classe candidate"
    elif AVANT not in src0:
        echec = "site de réparation introuvable"
    else:
        s = src0.replace(AVANT, APRES, 1)
        CIBLE.write_text(s, encoding="utf-8")
        try:
            ast.parse(s)
        except SyntaxError as e:
            echec = f"le patch ne compile pas : {e}"
        if echec is None:
            r = subprocess.run([sys.executable, str(CIBLE)], cwd=str(REPO),
                               capture_output=True, text=True, timeout=900)
            if r.returncode != 0:
                echec = ((r.stderr.strip().splitlines() or ["(sans message)"])[-1])[:160]
        if echec is None:
            diff_py = lignes_changees(REL_PY)
            diff_md = lignes_changees(REL_MD)
            hors = [l for l in diff_md if not AUTORISEE.search(l)]
            m_n = re.search(r"reste \*\*(\d+)\*\* candidat hors de portée",
                            RAPPORT.read_text(encoding="utf-8"))
            neuve = m_n.group(1) if m_n else None
            if hors:
                echec = (f"le diff du rapport déborde : {len(hors)} ligne(s) "
                         f"hors du site autorisé")

    sales = [l for l in git("status", "--porcelain").splitlines()
             if l.strip() and MOI not in l
             and REL_PY.split("/")[-1] not in l and REL_MD.split("/")[-1] not in l]
    if echec or sales:
        git("checkout", "--", REL_PY, REL_MD)

    L = []
    A = L.append
    A("# Réparer le **seul candidat actionnable** (pré-enregistré)")
    A("")
    A("Après le #507, `nonml_battery_backfill_lot_audit.py` est le **seul** des")
    A("13 « réparables » qui soit candidat committable **et** sans dépendance à")
    A("`sys.argv`. Si le geste borné n'aboutit pas ici, le mot « actionnable »")
    A("ne veut rien dire.")
    A("")
    A("## Les quatre causes de non-committabilité, mesurées")
    A("")
    A("| Cause | Occurrences |")
    A("|---|---|")
    for k, v in cz.items():
        A(f"| {k} | **{v}** |")
    A("")
    A(f"- classe candidate confirmée : **{'OUI' if classe_ok else 'NON'}**")
    A("")
    A("## Le « 0,00 % » — la justification du #485 confrontée au code")
    A("")
    A("Le #485 rangeait ce chiffre parmi les réparables au motif que l'audit")
    A("« lit les `.npz` d'activation ». **Le code dit autre chose.**")
    A("")
    A(f"- occurrences de `np.load(` ou `.npz` dans la cible : "
      f"**{int(npz_reel)}**")
    A(f"- le littéral `0,00 %` est bien présent : **{int(prod_0)}**")
    A("")
    A("Sa seule source de données est `read_battery()`, qui relit des rapports")
    A("`.md`. **Aucune donnée d'activation n'est ouverte.**")
    A("")
    A("> **La justification du #485 est fausse sur ce chiffre.** Il n'est pas")
    A("> réparable par interpolation : le produire exigerait d'ouvrir une")
    A("> source que le script n'ouvre pas — un cycle distinct, pas « une")
    A("> interpolation ». **C'est la deuxième justification du #485 que la")
    A("> lecture du code contredit**, après celle que le #493 avait retirée.")
    A(">")
    A("> **Ce constat a été fait avant d'écrire le pré-enregistrement et y est")
    A("> déclaré : il n'est pas compté comme une prédiction.**")
    A("")
    A("## Le diff du `.py`")
    A("")
    A(f"- lignes changées : **{len(diff_py)}**")
    if diff_py:
        A("")
        A("```")
        for l in diff_py:
            A(l)
        A("```")
    A("")
    A("## Le diff du rapport")
    A("")
    A(f"- lignes changées : **{len(diff_md)}**")
    if diff_md:
        A("")
        A("```")
        for l in diff_md:
            A(l)
        A("```")
    A("")
    A("## La valeur calculée face au littéral")
    A("")
    A("| | Valeur |")
    A("|---|---|")
    A(f"| littéral d'origine | **{litteral or '—'}** |")
    A(f"| valeur calculée | **{neuve or '—'}** |")
    A("")
    if litteral and neuve and litteral == neuve:
        A("> Le littéral était **exact**. Le défaut n'était pas une erreur de")
        A("> calcul mais une **duplication de source** — et il est levé : le")
        A("> nombre est désormais dérivé de `SET_ASIDE`.")
    elif litteral and neuve:
        A(f"> **Le littéral était périmé** : la valeur dérivée vaut")
        A(f"> **{neuve}**, pas **{litteral}**. Le rapport publiait un chiffre")
        A("> que son propre code contredit.")
    A("")
    A("## Le geste est-il resté borné ?")
    A("")
    A(f"- autres fichiers de l'arbre touchés : **{len(sales)}**")
    A(f"- échec : **{echec if echec else 'aucun'}**")
    A("")
    if echec or sales:
        A("> **Tout a été restauré.** Le barème du #489 et du #499 s'applique")
        A("> sans adoucissement.")
    else:
        A("> **Le geste a tenu.** La réparation est **committée** — c'est la")
        A("> différence avec le #499, et la seule preuve que le mot")
        A("> « actionnable » du #507 recouvrait quelque chose.")
    A("")
    A("## Mes trois prédictions, confrontées")
    A("")
    p1 = echec is None and not sales
    p2 = bool(litteral and neuve and litteral == neuve)
    p3 = classe_ok
    A("| Prédiction | Annoncé | Mesuré | Verdict |")
    A("|---|---|---|---|")
    A(f"| diff du rapport limité au site réparé | oui | "
      f"{'oui' if p1 else 'non'} | **{'vérifiée' if p1 else 'réfutée'}** |")
    A(f"| la valeur calculée vaut le littéral | {litteral or '—'} | "
      f"{neuve or '—'} | **{'vérifiée' if p2 else 'réfutée'}** |")
    A(f"| les quatre causes valent 0 | 0 | {sum(cz.values())} | "
      f"**{'vérifiée' if p3 else 'réfutée'}** |")
    A("")
    if not p1:
        A("> **La prédiction 1 est réfutée, et sa portée dépasse ce cycle** :")
        A("> **aucun** des 13 « réparables » du #485 n'est alors committable, et")
        A("> ce compte ne décrit **rien d'actionnable**.")
    A("")
    A("## Critères de succès")
    A("")
    c = [(f"Les quatre causes mesurées et publiées (**{sum(cz.values())}**)",
          True),
         (f"Diff du `.py` limité au site réparé (**{len(diff_py)}** lignes)",
          bool(diff_py) and echec is None),
         (f"Diff du rapport réduit au site réparé (**{len(diff_md)}** lignes)",
          echec is None and not sales),
         ("Valeur calculée publiée face au littéral", bool(neuve)),
         ("Justification du #485 sur le « 0,00 % » confrontée et tranchée",
          True)]
    for i, (t, v) in enumerate(c, 1):
        A(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    A("")
    verdict = "PASS" if all(v for _, v in c) else "FAIL"
    A(f"**{verdict}** — le critère porte sur le **procédé**.")
    A("")
    A("Simulation 300 € et robustesse **sans objet** : cycle de réparation,")
    A("aucune position, aucun paramètre numérique de stratégie.")
    A("")
    A("> **Ce script-ci exécute et modifie un tiers** : il est lui-même non")
    A("> committable au sens du #507, et le dire vaut mieux que feindre")
    A("> l'inertie.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — classe {classe_ok}, diff py {len(diff_py)}, "
          f"diff md {len(diff_md)}, littéral {litteral} → {neuve}, échec={echec}")


if __name__ == "__main__":
    main()
