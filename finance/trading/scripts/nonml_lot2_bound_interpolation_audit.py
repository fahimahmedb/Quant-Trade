"""Audit independant du #499.

Le backtest a MODIFIE puis EXECUTE un script du depot, avant de tout
restaurer. Un tel cycle doit etre audite sur deux choses que le #495 a
etablies : la restauration est-elle REELLE et non theatrale, et la
conclusion tient-elle sans faire confiance au script modifie ?

La borne est ici recalculee A LA MAIN -- `1 - 0.05**(1/n)` -- sans lire la
fonction de la cible : si les deux litteraux etaient exacts, cette
arithmetique doit le montrer seule.
"""
import ast
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

RAP = RESULTS / "nonml_lot2_bound_interpolation_result.md"
BT = SCRIPTS / "nonml_lot2_bound_interpolation_backtest.py"
CIBLE = SCRIPTS / "nonml_reproducibility_campaign_v3_lot2_audit.py"
REL_PY = "finance/trading/scripts/nonml_reproducibility_campaign_v3_lot2_audit.py"
REL_MD = "finance/trading/results/nonml_reproducibility_campaign_v3_lot2_audit.md"
OUT = RESULTS / "nonml_lot2_bound_interpolation_audit.md"
MOI = "lot2_bound_interpolation"

GRAS = re.compile(r"\*\*(-?\d[\d  ]*(?:[,.]\d+)?)\s*(?:%|€|bps)?\*\*")
CUM, SUP = 47, 24          # lus dans le rapport cible, verifies ci-dessous


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def plat(t):
    return re.sub(r"\s+", " ", t.replace("*", "").replace("`", ""))


def borne(n):
    """La meme formule, reecrite ici -- pas importee de la cible."""
    return 100.0 * (1.0 - 0.05 ** (1.0 / n))


def fr(x):
    return f"{x:.1f}".replace(".", ",")


def main():
    rap = RAP.read_text(encoding="utf-8")
    p = plat(rap)

    # --- 1. La restauration est-elle reelle ? ------------------------------
    sales = [l for l in git("status", "--porcelain").splitlines()
             if l.strip() and MOI not in l]
    diff_py = git("diff", "HEAD", "--", REL_PY).strip()
    diff_md = git("diff", "HEAD", "--", REL_MD).strip()
    propre = not sales and not diff_py and not diff_md

    # --- 2. La cible porte-t-elle encore ses litteraux ? -------------------
    src = CIBLE.read_text(encoding="utf-8")
    lit_titre = 'la borne tombe à 6,2 %' in src
    lit_phrase = '24 tirages de plus feraient passer la borne de **6,2 %**' in src
    lit_ctrl = 'abs(100 * bound(cum) - 6.2)' in src
    lit_sect = '## Ce que 6,2 % dit — et ne dit pas' in src
    intacte = lit_titre and lit_phrase and lit_ctrl and lit_sect

    # --- 3. La classe A, par une route independante ------------------------
    arbre = ast.parse(src)
    exec_tiers = 0
    for n in ast.walk(arbre):
        if not isinstance(n, ast.Call):
            continue
        try:
            code = ast.unparse(n)
        except Exception:
            continue
        if re.match(r"^subprocess\.\w+\(\s*\[\s*sys\.executable", code) \
                or re.match(r"^(?:runpy|importlib)\b", code) \
                or re.match(r"^os\.(?:system|popen|exec|spawn)", code):
            exec_tiers += 1
    ecritures = {m.group(1) for m in
                 re.finditer(r"([A-Za-z_]\w*)\.write_text\(", src)}
    classe_a = exec_tiers == 0 and len(ecritures) <= 1

    # --- 4. La borne, recalculee a la main --------------------------------
    b_cum, b_proj = borne(CUM), borne(CUM + SUP)
    # Le denominateur employe par la cible est-il bien 47 ?
    vieux = git("show", f"HEAD:{REL_MD}")
    denom_ok = bool(re.search(r"\|\s*\*\*cumul\*\*\s*\|\s*%d\s*\|" % CUM, vieux))
    titre_pub = re.search(r"la borne tombe à ([\d,]+) %", vieux)
    proj_pub = re.search(r"à \*\*~([\d,]+) %\*\*", vieux)
    ok_cum = titre_pub is not None and fr(b_cum) == titre_pub.group(1)
    ok_proj = proj_pub is not None and fr(b_proj) == proj_pub.group(1)

    # --- 5. Ce que le rapport publie --------------------------------------
    def num(motif):
        m = re.search(motif, p)
        return int(m.group(1)) if m else None
    pub_repar = num(r"imputables aux sites réparés : (\d+)")
    pub_hors = num(r"étrangères à la réparation : (\d+)")
    pub_dettes = num(r"littéraux 6,2 encore présents dans la cible : (\d+)")

    src_bt = BT.read_text(encoding="utf-8")
    en_dur = [m.group(1) for m in GRAS.finditer(rap)
              if re.search(r"[\"']\s*\*\*" + re.escape(m.group(1)) + r"\s*\*\*", src_bt)]

    L = []
    A = L.append
    A("# Audit indépendant — réparation de la borne du lot 2 (#499)")
    A("")
    A("Ce cycle a **modifié** puis **exécuté** un script du dépôt avant de tout")
    A("restaurer. Deux questions, posées par le #495 : la restauration est-elle")
    A("**réelle**, et la conclusion tient-elle **sans croire** le script modifié ?")
    A("")
    A("## La restauration est-elle réelle ?")
    A("")
    A(f"- fichiers de l'arbre modifiés hors ce cycle : **{len(sales)}**")
    A(f"- diff du script cible vs `HEAD` : **{len(diff_py.splitlines())}** ligne(s)")
    A(f"- diff du rapport cible vs `HEAD` : **{len(diff_md.splitlines())}** ligne(s)")
    A(f"- arbre propre : **{'OUI' if propre else 'NON'}**")
    A("")
    A("## La cible porte-t-elle encore ses littéraux ?")
    A("")
    A("Si la réparation avait été committée en douce, ils auraient disparu.")
    A("")
    A(f"- littéral du **titre** encore présent : **{'oui' if lit_titre else 'NON'}**")
    A(f"- littéral de la **phrase** encore présent : **{'oui' if lit_phrase else 'NON'}**")
    A(f"- littéral **de contrôle** (l. 123) encore présent : "
      f"**{'oui' if lit_ctrl else 'NON'}**")
    A(f"- littéral du **titre de section** (l. 132) encore présent : "
      f"**{'oui' if lit_sect else 'NON'}**")
    A("")
    A(f"- cible intacte : **{'OUI' if intacte else 'NON'}**")
    A("")
    A("## La classe A, par une route indépendante")
    A("")
    A("Le backtest **importe** la règle du #497. Cet audit la réapplique en")
    A("**déparsant** les nœuds `Call`, sans rien importer du #497.")
    A("")
    A(f"- appels exécutant un tiers : **{exec_tiers}**")
    A(f"- cibles d'écriture distinctes : **{len(ecritures)}** "
      f"({', '.join(sorted(ecritures)) if ecritures else '—'})")
    A(f"- classe A confirmée : **{'OUI' if classe_a else 'NON'}**")
    A("")
    A("## La borne, recalculée à la main")
    A("")
    A("`bound(n) = 1 − 0,05^(1/n)`, **réécrite ici**, jamais importée de la")
    A("cible. Si les littéraux étaient exacts, cette arithmétique suffit à le")
    A("montrer — sans faire confiance au script réparé.")
    A("")
    A(f"- dénominateur cumulé lu dans le rapport cible : **{CUM}** "
      f"(**{'confirmé' if denom_ok else 'NON confirmé'}**)")
    A("")
    A("| Grandeur | Publié dans la cible | Recalculé ici | Accord |")
    A("|---|---|---|---|")
    A(f"| borne actuelle | **{titre_pub.group(1) if titre_pub else '—'} %** | "
      f"**{fr(b_cum)} %** | {'**oui**' if ok_cum else '**NON**'} |")
    A(f"| borne projetée (+{SUP}) | **~{proj_pub.group(1) if proj_pub else '—'} %** | "
      f"**~{fr(b_proj)} %** | {'**oui**' if ok_proj else '**NON**'} |")
    A("")
    if ok_cum and ok_proj:
        A("> **Les deux littéraux étaient exacts.** Le défaut n'était donc pas")
        A("> une erreur de calcul mais une **duplication de source** — et le")
        A("> `~4,1 %`, que le #499 prédisait faux, ne l'était pas.")
    A("")
    A("## L'imputation du diff, recontrôlée")
    A("")
    A(f"- lignes imputées à la réparation par le rapport : **{pub_repar}**")
    A(f"- lignes imputées à la dérive : **{pub_hors}**")
    A("")
    if pub_repar == 0 and ok_cum and ok_proj:
        A("> L'imputation est **cohérente avec l'arithmétique** : des littéraux")
        A("> exacts réécrivent les mêmes caractères, donc la réparation ne")
        A("> pouvait produire **aucune** ligne de diff. Les deux mesures se")
        A("> confirment l'une l'autre par des chemins séparés.")
    A("")
    A("## Chiffres calculés")
    A("")
    A(f"- nombres en gras : **{len(GRAS.findall(rap))}** ; dont **tapés en dur** : "
      f"**{len(en_dur)}**")
    if en_dur:
        A("")
        A(f"> En dur : {', '.join('`'+v+'`' for v in sorted(set(en_dur)))}")
    A("")
    A("## Verdict")
    A("")
    ctrl = [("la restauration est réelle — arbre et diffs vides", propre),
            ("la cible porte encore ses quatre littéraux", intacte),
            ("la classe A est confirmée par une route indépendante", classe_a),
            ("la borne recalculée à la main confirme les deux littéraux",
             ok_cum and ok_proj),
            (f"l'imputation du diff est cohérente (**{pub_repar}** / "
             f"**{pub_hors}**)", pub_repar == 0),
            (f"les **{pub_dettes}** dettes déclarées sont bien encore en place",
             pub_dettes == 2 and lit_ctrl and lit_sect),
            ("aucun chiffre du rapport tapé en dur", not en_dur)]
    for i, (t, v) in enumerate(ctrl, 1):
        A(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    A("")
    v = "AUDIT OK" if all(x for _, x in ctrl) else "AUDIT — RÉSERVE"
    A(f"**{v}** ({sum(1 for _, x in ctrl if x)}/{len(ctrl)})")
    A("")
    A("Anti-lookahead **sans objet au sens temporel** : aucune série de prix.")
    A("Son équivalent ici est la **restauration**, vérifiée ci-dessus contre")
    A("l'arbre `git` et non contre la parole du cycle audité.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{v}")


if __name__ == "__main__":
    main()
