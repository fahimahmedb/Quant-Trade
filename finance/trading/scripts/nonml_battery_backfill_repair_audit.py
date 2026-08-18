"""Audit independant du #511.

Ce cycle a MODIFIE un script du depot et l'a COMMITTE. Un audit doit donc
verifier trois choses que le backtest, juge et partie, ne peut pas etablir
seul :

  1. la reparation est REELLEMENT dans l'arbre committe -- pas seulement
     annoncee ;
  2. le rapport de la cible est INCHANGE par rapport a son etat d'avant le
     cycle : une reparation qui se voit dans le rapport n'etait pas une
     interpolation exacte ;
  3. la valeur derivee est correcte -- recalculee ICI depuis `SET_ASIDE`, sans
     executer la cible ni lire son rapport.

Il verifie enfin que le << 0,00 % >> est toujours en dur, comme annonce.
"""
import ast
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

CIBLE = SCRIPTS / "nonml_battery_backfill_lot_audit.py"
REL_PY = "finance/trading/scripts/nonml_battery_backfill_lot_audit.py"
REL_MD = "finance/trading/results/nonml_battery_backfill_lot_audit.md"
RAP = RESULTS / "nonml_battery_backfill_repair_result.md"
BT = SCRIPTS / "nonml_battery_backfill_repair_backtest.py"
OUT = RESULTS / "nonml_battery_backfill_repair_audit.md"
MOI = "battery_backfill_repair"

GRAS = re.compile(r"\*\*(-?\d[\d  ]*(?:[,.]\d+)?)\s*(?:%|€|bps)?\*\*")


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def plat(t):
    return re.sub(r"\s+", " ", t.replace("*", "").replace("`", ""))


def main():
    rap = RAP.read_text(encoding="utf-8")
    p = plat(rap)
    src = CIBLE.read_text(encoding="utf-8")
    arbre = ast.parse(src)

    # --- 1. La reparation est-elle dans l'arbre committe ? ----------------
    commit_rep = git("log", "-1", "--format=%H", "-S", "_hors", "--", REL_PY).strip()
    dans_head = "_hors" in git("show", f"HEAD:{REL_PY}")
    plus_litteral = "reste **1** candidat hors de portée" not in git(
        "show", f"HEAD:{REL_PY}")
    propre = not [l for l in git("status", "--porcelain").splitlines()
                  if l.strip() and MOI not in l]

    # --- 2. Le rapport de la cible a-t-il bouge ? ------------------------
    n_commits_md = len([l for l in git("log", "--format=%H", "--", REL_MD)
                        .splitlines() if l.strip()])
    diff_md_head = git("diff", "HEAD~1", "HEAD", "--", REL_MD).strip()

    # --- 3. La valeur derivee, recalculee ICI ----------------------------
    set_aside = None
    for n in ast.walk(arbre):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name) and t.id == "SET_ASIDE":
                    try:
                        set_aside = ast.literal_eval(n.value)
                    except (ValueError, SyntaxError):
                        set_aside = None
    attendu = (sum(1 for r in set_aside.values() if "panier" in r)
               if isinstance(set_aside, dict) else None)
    publie = None
    m = re.search(r"reste \*\*(\d+)\*\* candidat hors de portée",
                  Path(REPO / REL_MD).read_text(encoding="utf-8"))
    if m:
        publie = int(m.group(1))

    # --- 4. Le 0,00 % est-il toujours en dur ? ---------------------------
    zero_dur = "0,00 %" in src
    npz = bool(re.search(r"np\.load\s*\(|\.npz", src))

    src_bt = BT.read_text(encoding="utf-8")
    en_dur = [g.group(1) for g in GRAS.finditer(rap)
              if re.search(r"[\"']\s*\*\*" + re.escape(g.group(1)) + r"\s*\*\*", src_bt)]

    L = []
    A = L.append
    A("# Audit indépendant — réparation du candidat actionnable (#511)")
    A("")
    A("Ce cycle a **modifié et committé** un script du dépôt. L'audit vérifie")
    A("ce que le backtest, **juge et partie**, ne peut pas établir seul.")
    A("")
    A("## 1. La réparation est-elle réellement dans l'arbre ?")
    A("")
    A(f"- `_hors` présent dans la version **committée** (`HEAD`) : "
      f"**{'OUI' if dans_head else 'NON'}**")
    A(f"- l'ancien littéral a **disparu** de `HEAD` : "
      f"**{'OUI' if plus_litteral else 'NON'}**")
    A(f"- commit qui introduit `_hors` : "
      f"**{commit_rep[:8] if commit_rep else '—'}**")
    A(f"- arbre propre hors ce cycle : **{'OUI' if propre else 'NON'}**")
    A("")
    A("> Une réparation **annoncée** et une réparation **déposée** sont deux")
    A("> choses différentes. Le #499 avait tout restauré ; ici l'arbre doit")
    A("> porter la trace, et `git show HEAD:` la porte.")
    A("")
    A("## 2. Le rapport de la cible a-t-il bougé ?")
    A("")
    A(f"- commits touchant `{REL_MD.split('/')[-1]}` : **{n_commits_md}**")
    A(f"- diff du rapport entre `HEAD~1` et `HEAD` : "
      f"**{len(diff_md_head.splitlines())}** ligne(s)")
    A("")
    if not diff_md_head:
        A("> **Le rapport n'a pas bougé d'un octet.** C'est la preuve la plus")
        A("> forte que l'interpolation était **exacte** : le code calcule")
        A("> désormais ce qui était tapé, et produit **les mêmes caractères**.")
        A("> Une réparation visible dans le rapport aurait signifié que le")
        A("> littéral était faux.")
    else:
        A("> **Le rapport a changé.** La réparation n'était donc pas une")
        A("> interpolation exacte, et le diff ci-dessus doit être examiné.")
    A("")
    A("## 3. La valeur dérivée, recalculée ici")
    A("")
    A("Recalcul depuis `SET_ASIDE`, **lu par AST** dans la cible — sans")
    A("l'exécuter, sans lire le rapport du #511.")
    A("")
    A(f"- entrées dans `SET_ASIDE` : "
      f"**{len(set_aside) if isinstance(set_aside, dict) else '—'}**")
    A(f"- dont motif « panier » : **{attendu if attendu is not None else '—'}**")
    A(f"- valeur publiée par le rapport de la cible : **{publie or '—'}**")
    A(f"- accord : **{'OUI' if attendu == publie else 'NON'}**")
    A("")
    A("## 4. Le « 0,00 % » est-il toujours en dur, comme annoncé ?")
    A("")
    A(f"- littéral `0,00 %` encore présent : **{'OUI' if zero_dur else 'NON'}**")
    A(f"- la cible ouvre-t-elle un `.npz` : **{'OUI' if npz else 'NON'}**")
    A("")
    if zero_dur and not npz:
        A("> **Confirmé sur les deux points.** Le chiffre reste en dur, et la")
        A("> cible n'ouvre toujours aucune donnée d'activation : la")
        A("> justification du #485 le concernant est bien **fausse**, et le")
        A("> #511 n'a pas prétendu le réparer.")
    A("")
    A("## Ce que cet audit ne prouve pas")
    A("")
    A("Il ne dit **pas** que la valeur **1** soit la bonne réponse à la")
    A("question posée dans la phrase — seulement qu'elle est désormais")
    A("**dérivée** de `SET_ASIDE` au lieu d'être tapée. Si `SET_ASIDE` est")
    A("lui-même incomplet, le nombre reste faux, **calculé mais faux**.")
    A("")
    A("## Chiffres calculés")
    A("")
    A(f"- nombres en gras dans le rapport : **{len(GRAS.findall(rap))}** ; "
      f"dont **tapés en dur** : **{len(en_dur)}**")
    if en_dur:
        A("")
        A(f"> En dur : {', '.join('`'+v+'`' for v in sorted(set(en_dur)))}")
    A("")
    A("## Verdict")
    A("")
    ctrl = [("la réparation est présente dans `HEAD`", dans_head and plus_litteral),
            ("le rapport de la cible n'a pas bougé", not diff_md_head),
            ("la valeur dérivée concorde avec un recalcul indépendant",
             attendu is not None and attendu == publie),
            ("le « 0,00 % » reste en dur et la cible n'ouvre pas de `.npz`",
             zero_dur and not npz),
            ("arbre propre, aucun chiffre du rapport tapé en dur",
             propre and not en_dur)]
    for i, (t, v) in enumerate(ctrl, 1):
        A(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    A("")
    v = "AUDIT OK" if all(x for _, x in ctrl) else "AUDIT — RÉSERVE"
    A(f"**{v}** ({sum(1 for _, x in ctrl if x)}/{len(ctrl)})")
    A("")
    A("Anti-lookahead **sans objet au sens temporel** : aucune série de prix.")
    A("Son équivalent ici est la **vérification contre l'arbre `git`**, et non")
    A("contre la parole du cycle audité.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{v} — HEAD {dans_head}, rapport inchangé {not diff_md_head}, "
          f"valeur {attendu}=={publie}")


if __name__ == "__main__":
    main()
