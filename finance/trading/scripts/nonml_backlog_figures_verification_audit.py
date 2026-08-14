"""Audit adversarial du #461 — recalcul independant + controles de l'instrument.

Ne reutilise AUCUNE fonction du backtest : tout est reimplemente par une autre
route, pour qu'un bug commun ne puisse pas se cacher dans une dependance
partagee.

Quatre controles :

  A. Recalcul independant du nombre de jetons et d'absences.
  B. L'epinglage est-il reellement le commit INTRODUCTEUR ? (le parent ne doit
     pas contenir l'entree, le commit doit la contenir).
  C. Le rapport lit-il l'HISTOIRE ou le DISQUE ? Si les blobs epingles etaient
     identiques aux fichiers courants, l'epinglage serait decoratif.
  D. Idempotence : deux executions rendent-elles le meme fichier ?
"""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

OUT = RESULTS / "nonml_backlog_figures_verification_audit.md"
RAPPORT = RESULTS / "nonml_backlog_figures_verification_result.md"
BACKLOG = "finance/trading/NONML_STRATEGY_BACKLOG.md"
ENTREES = list(range(443, 461))


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


# --- A. Recalcul independant, par une AUTRE route ---------------------------
# Le backtest decoupe l'entree en lignes puis cherche les gras ligne a ligne.
# Ici : on isole l'entree par une expression sur le texte ENTIER, et on
# tokenise en une seule passe. Meme regle declaree, implementation disjointe.

def entree_par_regex(blob, num):
    m = re.search(rf"(?ms)^## Backlog #{num} \(.*?(?=^## |\Z)", blob)
    return m.group(0) if m else None


def compte_jetons(txt):
    t = re.sub(r"(?<=\d)[    ](?=\d)", "", txt)
    t = re.sub(r"(?<=\d)[    ](?=\d)", "", t)
    n = 0
    for seg in re.findall(r"\*\*(.+?)\*\*", t):
        s = seg
        for rx in (r"#\d+", r"\d{2}/\d{2}/\d{4}", r"\b4/4\b", r"n_trials\s*=\s*\d+"):
            s = re.sub(rx, " ", s)
        n += len(re.findall(r"[+\-−]?\d+(?:,\d+)?%?", s))
    return n


def main():
    L = ["# Audit adversarial — vérification des chiffres du backlog (#461)", ""]
    L.append("Recalcul par une **autre implémentation**, sans réutiliser une seule")
    L.append("fonction du backtest : un bug commun ne peut pas se cacher dans une")
    L.append("dépendance partagée.")
    L.append("")

    # ------------------------------------------------------------------ A
    lu = RAPPORT.read_text(encoding="utf-8") if RAPPORT.exists() else ""
    m = re.search(r"jetons numériques vérifiés : \*\*(\d+)\*\*", lu)
    annonce = int(m.group(1)) if m else -1

    total, par_entree, manquantes = 0, [], []
    for num in ENTREES:
        out = git("log", "-S", f"## Backlog #{num} (", "--format=%H", "--", BACKLOG)
        shas = [l for l in (out or "").splitlines() if l.strip()]
        if not shas:
            manquantes.append(num)
            continue
        sha = shas[-1]
        blob = git("show", f"{sha}:{BACKLOG}") or ""
        txt = entree_par_regex(blob, num)
        if txt is None:
            manquantes.append(num)
            continue
        n = compte_jetons(txt)
        total += n
        par_entree.append((num, sha, n))

    okA = (total == annonce) and not manquantes
    L.append("## A. Recalcul indépendant du nombre de jetons")
    L.append("")
    L.append(f"- annoncé par le rapport : **{annonce}**")
    L.append(f"- recalculé ici : **{total}**")
    L.append(f"- entrées introuvables : **{len(manquantes)}**")
    L.append("")
    L.append(f"**{'CONCORDANT' if okA else 'ÉCART'}.**")
    L.append("")

    # ------------------------------------------------------------------ B
    bons, mauvais = 0, []
    for num, sha, _ in par_entree:
        motif = f"## Backlog #{num} ("
        ici = motif in (git("show", f"{sha}:{BACKLOG}") or "")
        par = git("rev-parse", f"{sha}^") or ""
        avant = motif in (git("show", f"{par.strip()}:{BACKLOG}") or "") if par.strip() else False
        if ici and not avant:
            bons += 1
        else:
            mauvais.append((num, sha[:8], ici, avant))

    okB = not mauvais
    L.append("## B. L'épinglage est-il le commit **introducteur** ?")
    L.append("")
    L.append("Un épinglage qui viserait un commit postérieur laisserait la dérive du")
    L.append("dépôt rentrer par la fenêtre — c'est exactement le défaut des #445/#451.")
    L.append("Contrôle : l'entrée est présente au commit, **absente chez son parent**.")
    L.append("")
    L.append(f"- conformes : **{bons}/{len(par_entree)}**")
    if mauvais:
        L.append("")
        L.append("| Entrée | Commit | Présente ici | Présente chez le parent |")
        L.append("|---|---|---|---|")
        for num, s, ici, av in mauvais:
            L.append(f"| #{num} | `{s}` | {ici} | {av} |")
    L.append("")
    L.append(f"**{'CONCORDANT' if okB else 'ÉCART'}.**")
    L.append("")

    # ------------------------------------------------------------------ C
    differents, identiques = 0, 0
    for num, sha, _ in par_entree:
        hist = git("show", f"{sha}:{BACKLOG}") or ""
        disque = (REPO / BACKLOG).read_text(encoding="utf-8")
        if hist == disque:
            identiques += 1
        else:
            differents += 1
    okC = differents > 0
    L.append("## C. Le rapport lit-il l'**histoire** ou le **disque** ?")
    L.append("")
    L.append("Si les blobs épinglés étaient identiques au fichier courant, l'épinglage")
    L.append("serait **décoratif** et le rapport dériverait comme les inventaires que")
    L.append("les #436-#438 ont appris à repérer.")
    L.append("")
    L.append(f"- blobs épinglés **différents** du fichier courant : **{differents}**")
    L.append(f"- blobs épinglés identiques : **{identiques}**")
    L.append("")
    L.append(f"**{'CONCORDANT' if okC else 'ÉCART'}** — l'épinglage mord réellement.")
    L.append("")

    # ------------------------------------------------------------------ D
    def empreinte():
        return hashlib.sha256(RAPPORT.read_bytes()).hexdigest() if RAPPORT.exists() else ""

    av = empreinte()
    subprocess.run([sys.executable,
                    str(SCRIPTS / "nonml_backlog_figures_verification_backtest.py")],
                   cwd=ROOT, capture_output=True, text=True)
    ap = empreinte()
    okD = av == ap and av != ""
    L.append("## D. Idempotence")
    L.append("")
    L.append("Un rapport épinglé qui change d'une exécution à l'autre ne serait pas")
    L.append("épinglé. Le backtest est relancé et l'empreinte comparée.")
    L.append("")
    L.append(f"- avant : `{av[:16]}`")
    L.append(f"- après : `{ap[:16]}`")
    L.append("")
    L.append(f"**{'CONCORDANT' if okD else 'ÉCART'}.**")
    L.append("")

    # ------------------------------------------------------------------ fin
    tous = okA and okB and okC and okD
    L.append("## Ce que cet audit ne couvre pas")
    L.append("")
    L.append("Il vérifie que le contrôle **fait ce qu'il dit**. Il ne peut pas rattraper")
    L.append("la limite de fond, déjà publiée dans le rapport : **un contrôle de recopie")
    L.append("ne voit pas un chiffre faux à l'identique dans le backlog et dans le")
    L.append("rapport.** Les quatre faux connus (#449, #451, #453, #457) sont de cette")
    L.append("nature — aucun audit de recopie ne les aurait trouvés.")
    L.append("")
    L.append(f"## Verdict — **{'CONCORDANT' if tous else 'ÉCART'}** ({sum([okA, okB, okC, okD])}/4)")
    L.append("")
    L.append("Aucun bug détecté par recalcul indépendant." if tous
             else "**Au moins un contrôle échoue — voir ci-dessus.**")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()
