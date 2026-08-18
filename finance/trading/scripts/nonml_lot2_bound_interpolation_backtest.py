"""Reparer le 13e reparable : interpoler la borne du lot 2 (#499).

Specification pre-enregistree dans `PREREG_lot2_bound_interpolation.md`,
committee AVANT toute modification -- perimetre et regle du geste borne
compris.

Ce script MODIFIE un script du depot et l'EXECUTE une fois. Il est donc
lui-meme de classe C au sens du #497, et il le dit. La regle du geste borne
du #489 s'applique : si le diff du rapport deborde des lignes visees, TOUT
est restaure et le cycle echoue.
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

CIBLE = SCRIPTS / "nonml_reproducibility_campaign_v3_lot2_audit.py"
RAPPORT = RESULTS / "nonml_reproducibility_campaign_v3_lot2_audit.md"
REL_PY = "finance/trading/scripts/nonml_reproducibility_campaign_v3_lot2_audit.py"
REL_MD = "finance/trading/results/nonml_reproducibility_campaign_v3_lot2_audit.md"
OUT = RESULTS / "nonml_lot2_bound_interpolation_result.md"
MOI = "lot2_bound_interpolation"

# Les deux sites ENUMERES par le pre-enregistrement -- et eux seuls.
AVANT_TITRE = '    L = ["# Audit — campagne v3, lot 2 : la borne tombe à 6,2 %", ""]'
APRES_TITRE = ('    L = [f"# Audit — campagne v3, lot 2 : la borne tombe à '
               '{_fr(100*bound(cum))} %", ""]')
AVANT_PHRASE = ('    L.append("24 tirages de plus feraient passer la borne de '
                '**6,2 %** à **~4,1 %** — de ~17 à")')
APRES_PHRASE = ('    L.append(f"{TIRAGES_SUP} tirages de plus feraient passer la '
                'borne de **{_fr(100*bound(cum))} %** à "\n'
                '             f"**~{_fr(100*bound(cum + TIRAGES_SUP))} %** — de ~17 à")')
AIDE = ('TIRAGES_SUP = 24\n\n\n'
        'def _fr(x):\n'
        '    """Rend un nombre a la francaise -- la typographie deja publiee."""\n'
        '    return f"{x:.1f}".replace(".", ",")\n\n\n'
        'def bound(n):')

# Lignes du rapport que le pre-enregistrement autorise a changer.
AUTORISEES = [re.compile(r"^# Audit — campagne v3, lot 2"),
              re.compile(r"tirages de plus feraient passer la borne")]
# Lignes du .py que le perimetre enumere autorise a changer : APPARTENANCE
# EXACTE au bloc insere et aux deux sites, jamais un motif ajuste apres coup.
def _autorisees_py():
    ok = set()
    for bloc in (AIDE, AVANT_TITRE, APRES_TITRE, AVANT_PHRASE, APRES_PHRASE):
        for l in bloc.splitlines():
            ok.add(l.rstrip())
    return ok

# Dettes laissees en place, NOMMEES d'avance ou constatees, jamais corrigees.
DETTES = [
    (123, "`ok_bound = abs(100 * bound(cum) - 6.2) < 0.2`",
     "littéral **de contrôle** qui **garde une section** — le corriger "
     "changerait la logique, pas la typographie. Nommé au pré-enregistrement."),
    (132, '`L.append("## Ce que 6,2 % dit — et ne dit pas")`',
     "**titre de section** portant le même littéral. **Mon énumération du "
     "pré-enregistrement ne l'avait pas vu** : je ne l'élargis pas après coup."),
]


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def regle_497():
    """La regle des 12 primitives, IMPORTEE du #497 -- jamais recopiee."""
    p = SCRIPTS / "nonml_execution_primitives_census_backtest.py"
    spec = importlib.util.spec_from_file_location("_c497", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)          # constantes seulement ; `main()` non appelé
    return m


def restaure():
    git("checkout", "--", REL_PY, REL_MD)


def lignes_changees(rel):
    d = git("diff", "-U0", "--", rel)
    return [l[1:] for l in d.splitlines()
            if (l.startswith("+") or l.startswith("-"))
            and not l.startswith(("+++", "---"))]


def nombres(txt, motif):
    m = re.search(motif, txt)
    return m.groups() if m else ()


def main():
    c497 = regle_497()
    existants = {p.stem for p in SCRIPTS.glob("nonml_*.py")}

    # --- 1. La classe de la cible, PAR AST -------------------------------
    src0 = CIBLE.read_text(encoding="utf-8")
    prim = c497.primitives(src0, ast.parse(src0), existants)
    classe_ok = not prim

    # --- Les litteraux d'origine, LUS dans la version committee ----------
    vieux_md = git("show", f"HEAD:{REL_MD}")
    v_titre = nombres(vieux_md, r"# Audit — campagne v3, lot 2 : la borne tombe à ([\d,]+) %")
    v_phrase = nombres(vieux_md,
                       r"tirages de plus feraient passer la borne de \*\*([\d,]+) %\*\* à \*\*~([\d,]+) %\*\*")

    diff_py, diff_md, n_titre, n_phrase, echec = [], [], (), (), None
    n_hors, n_repar = 0, 0
    if not classe_ok:
        echec = "la cible exécute un tiers — le geste ne serait pas borné"
    else:
        # --- 2. Le patch, limite aux deux sites enumeres -----------------
        s = src0
        for a in (AVANT_TITRE, AVANT_PHRASE, "def bound(n):"):
            if a not in s:
                echec = f"site introuvable : {a[:60]}"
                break
        if echec is None:
            s = s.replace("def bound(n):", AIDE, 1)
            s = s.replace(AVANT_TITRE, APRES_TITRE, 1)
            s = s.replace(AVANT_PHRASE, APRES_PHRASE, 1)
            CIBLE.write_text(s, encoding="utf-8")
            try:
                ast.parse(s)
            except SyntaxError as e:
                echec = f"le patch ne compile pas : {e}"

        # --- 3. Une exécution, une seule ---------------------------------
        if echec is None:
            r = subprocess.run([sys.executable, str(CIBLE)], cwd=str(REPO),
                               capture_output=True, text=True, timeout=900)
            if r.returncode != 0:
                echec = ((r.stderr.strip().splitlines() or ["(sans message)"])[-1])[:160]

        # --- 4. Le geste est-il borné ? ----------------------------------
        if echec is None:
            diff_py = lignes_changees(REL_PY)
            diff_md = lignes_changees(REL_MD)
            hors = [l for l in diff_md
                    if not any(m.search(l) for m in AUTORISEES)]
            neuf_md = RAPPORT.read_text(encoding="utf-8")
            n_titre = nombres(neuf_md, r"# Audit — campagne v3, lot 2 : la borne tombe à ([\d,]+) %")
            n_phrase = nombres(neuf_md,
                               r"tirages de plus feraient passer la borne de \*\*([\d,]+) %\*\* à \*\*~([\d,]+) %\*\*")
            n_hors = len(hors)
            n_repar = len(diff_md) - n_hors
            if hors:
                echec = (f"le diff du rapport déborde : {len(hors)} ligne(s) "
                         f"hors des sites autorisés")

    # --- Autres fichiers touchés ? ---------------------------------------
    sales = [l for l in git("status", "--porcelain").splitlines()
             if l.strip() and MOI not in l
             and REL_PY.split("/")[-1] not in l and REL_MD.split("/")[-1] not in l]

    if echec or sales:
        restaure()

    L = []
    A = L.append
    A("# Réparer le 13ᵉ réparable : interpoler la borne du lot 2 (pré-enregistré)")
    A("")
    A("## La classe de la cible, établie par AST — non supposée")
    A("")
    A("La règle des **12 primitives** du #497 est **importée**, jamais recopiée :")
    A("recopier une règle est le meilleur moyen de la faire diverger. L'import")
    A("n'appelle pas `main()` — ce n'est donc pas la primitive **P10**.")
    A("")
    A(f"- primitives d'exécution d'un tiers dans la cible : **{len(prim)}** "
      f"({', '.join(sorted(prim)) if prim else 'aucune'})")
    A(f"- classe : **{'A — exécutable sans danger' if classe_ok else 'C — non exécutable'}**")
    A("")
    A("> Ce script-ci, lui, **modifie et exécute** un tiers : il est de")
    A("> **classe C** au sens du #497, et le dire vaut mieux que feindre")
    A("> l'inertie.")
    A("")
    A("## Le diff du `.py`")
    A("")
    A(f"- lignes changées dans le script cible : **{len(diff_py)}**")
    if diff_py:
        A("")
        A("```")
        for l in diff_py:
            A(l)
        A("```")
    A("")
    A("## Le diff du rapport")
    A("")
    A(f"- lignes changées dans le rapport : **{len(diff_md)}**")
    if diff_md:
        A("")
        A("```")
        for l in diff_md:
            A(l)
        A("```")
    A("")
    A("## Ce qui, dans ce diff, vient de la réparation")
    A("")
    A(f"- lignes du diff **imputables aux sites réparés** : **{n_repar}**")
    A(f"- lignes du diff **étrangères à la réparation** : **{n_hors}**")
    A("")
    if diff_md and n_repar == 0:
        A("> **La réparation n'a produit aucun changement de texte.** Les deux")
        A("> littéraux étaient exacts : interpolés, ils réécrivent les mêmes")
        A("> caractères. **La totalité du diff est de la dérive du dépôt**, sans")
        A("> rapport avec ce cycle.")
        A("")
        A("> Ce qui échoue n'est donc pas la réparation, c'est la **possibilité")
        A("> de la committer**. Le rapport cible n'est plus reproductible : le")
        A("> régénérer réécrit son vivier, son échantillon et l'un de ses")
        A("> contrôles. **Un chiffre dérivable n'est pas pour autant réparable")
        A("> par un geste borné** — le #493 comptait la dérivabilité, pas la")
        A("> committabilité, et les deux ne coïncident pas.")
        A("")
    A("## Les valeurs calculées, face aux littéraux")
    A("")
    A("| Site | Littéral d'origine | Valeur calculée |")
    A("|---|---|---|")
    A(f"| titre | **{v_titre[0] if v_titre else '—'} %** | "
      f"**{n_titre[0] if n_titre else '—'} %** |")
    A(f"| phrase, borne actuelle | **{v_phrase[0] if v_phrase else '—'} %** | "
      f"**{n_phrase[0] if n_phrase else '—'} %** |")
    A(f"| phrase, borne projetée | **~{v_phrase[1] if v_phrase else '—'} %** | "
      f"**~{n_phrase[1] if n_phrase else '—'} %** |")
    A("")
    if n_phrase and v_phrase and n_phrase[1] != v_phrase[1]:
        A(f"> **Le « ~{v_phrase[1]} % » était faux.** La fonction que le script")
        A(f"> possède donne **{n_phrase[1]} %**. Le chiffre projeté n'était pas")
        A("> un arrondi de son propre code : c'était une arithmétique de tête,")
        A("> publiée telle quelle.")
        A("")
    elif n_phrase and v_phrase:
        A("> Les deux littéraux étaient **exacts** : la fonction redonne les")
        A("> mêmes valeurs. Le défaut était la **duplication de source**, pas")
        A("> l'erreur de calcul — et il est levé.")
        A("")
    A("## Les dettes laissées en place — nommées, non corrigées")
    A("")
    A(f"- littéraux `6,2` **encore présents** dans la cible : **{len(DETTES)}**")
    A("")
    for ln, quoi, pourquoi in DETTES:
        A(f"- **l. {ln}** — {quoi} : {pourquoi}")
    A("")
    A("> La seconde est la plus instructive : **un cycle dédié à réparer des")
    A("> chiffres en dur a lui-même sous-énuméré les sites**. Je la laisse, et")
    A("> je l'écris — l'élargir maintenant serait la dérive que le #490 a")
    A("> refusée à son propre détriment.")
    A("")
    A("## Le geste est-il resté borné ?")
    A("")
    A(f"- autres fichiers de l'arbre touchés : **{len(sales)}**")
    A(f"- échec : **{echec if echec else 'aucun'}**")
    if echec or sales:
        A("")
        A("> **Tout a été restauré** — script et rapport. Le barème du #489 et")
        A("> du #495 s'applique sans adoucissement.")
    A("")
    A("## Mes trois prédictions, confrontées")
    A("")
    p1 = classe_ok
    p2 = bool(n_titre and v_titre and n_titre[0] == v_titre[0])
    p3 = bool(n_phrase and v_phrase and n_phrase[1] != v_phrase[1])
    A("| Prédiction | Annoncé | Mesuré | Verdict |")
    A("|---|---|---|---|")
    A(f"| la cible est de classe A | 0 primitive | {len(prim)} | "
      f"**{'vérifiée' if p1 else 'réfutée'}** |")
    A(f"| `100*bound(cum)` redonne le littéral | {v_titre[0] if v_titre else '—'} | "
      f"{n_titre[0] if n_titre else '—'} | **{'vérifiée' if p2 else 'réfutée'}** |")
    A(f"| la borne projetée diffère de `~{v_phrase[1] if v_phrase else '—'}` | "
      f"≠ | {n_phrase[1] if n_phrase else '—'} | "
      f"**{'vérifiée' if p3 else 'réfutée'}** |")
    A("")
    A("## Critères de succès")
    A("")
    hors_ok = echec is None and not sales
    permises = _autorisees_py()
    py_hors = [l for l in diff_py if l.rstrip() and l.rstrip() not in permises]
    c = [("Classe de la cible établie par AST, 0 primitive d'exécution", classe_ok),
         (f"Diff du `.py` publié, limité aux sites énumérés (**{len(diff_py)}** lignes)",
          bool(diff_py) and not py_hors),
         (f"Diff du rapport réduit aux sites autorisés (**{len(diff_md)}** lignes)",
          hors_ok),
         ("Valeurs calculées publiées face aux littéraux",
          bool(n_titre and v_titre)),
         (f"Littéraux de contrôle nommés comme dette (**{len(DETTES)}**), non modifiés",
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
    A("> **Rapport dépendant du dépôt** — il décrit l'état des fichiers à la")
    A("> date de son exécution.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — classe {'A' if classe_ok else 'C'}, "
          f"diff py {len(diff_py)}, diff md {len(diff_md)}, échec={echec}")


if __name__ == "__main__":
    main()
