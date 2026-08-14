"""Audit adversarial du #463 — la non-idempotence est-elle ce que je crois ?

Le backtest compare deux passages. Cet audit pose les questions qu'un tel
resultat appelle et que le backtest ne pose pas :

  A. La derive est-elle PERPETUELLE ou converge-t-elle apres un passage ?
     Si passage 2 == passage 3, ce n'est pas une derive sans fin mais une
     CONVERGENCE en un pas — et la lecture du resultat change.
  B. Le mecanisme est-il bien l'auto-inclusion ? Le rapport se nomme-t-il
     lui-meme dans son propre corpus ?
  C. Qui ecrit les 8 rapports hors perimetre ? Attribue nominativement.
  D. Mon propre rapport est-il idempotent ?
"""
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

OUT = RESULTS / "nonml_report_idempotence_audit.md"
MOI = "report_idempotence"
SUSPECTS = ["verdict_rule_propagation", "six_reports_regeneration"]


def sh(*a, **k):
    return subprocess.run(a, cwd=k.get("cwd", ROOT), capture_output=True,
                          text=True, timeout=k.get("timeout", 300))


def emp(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def restaure():
    sh("git", "checkout", "--", "finance/trading/results/", cwd=REPO)


def passages(nom, n):
    """n executions successives ; empreinte du rapport apres chacune."""
    script, rap = SCRIPTS / f"nonml_{nom}_backtest.py", RESULTS / f"nonml_{nom}_result.md"
    out = []
    for _ in range(n):
        r = sh(sys.executable, str(script))
        out.append(emp(rap) if r.returncode == 0 else None)
    return out


def touche_par(nom):
    """Les fichiers de results/ que CE script modifie, lui seul."""
    restaure()
    sh(sys.executable, str(SCRIPTS / f"nonml_{nom}_backtest.py"))
    st = sh("git", "status", "--porcelain", "finance/trading/results/", cwd=REPO).stdout
    f = sorted({l[3:].strip().split("/")[-1] for l in st.splitlines() if l.strip()})
    restaure()
    return f


def main():
    L = ["# Audit adversarial — idempotence des rapports (#463)", ""]
    L.append("Le backtest compare **deux** passages. Cet audit pose les questions qu'un")
    L.append("tel résultat appelle et que deux passages ne peuvent pas trancher.")
    L.append("")

    # ------------------------------------------------------------------ A
    L.append("## A. Dérive perpétuelle, ou convergence en un pas ?")
    L.append("")
    L.append("Si le passage 2 égale le passage 3, la non-idempotence n'est pas une")
    L.append("dérive sans fin : c'est une **convergence**, le rapport s'étant intégré")
    L.append("lui-même une bonne fois. **La lecture du résultat en dépend.**")
    L.append("")
    L.append("| Script | P1 | P2 | P3 | Lecture |")
    L.append("|---|---|---|---|---|")
    convergents, perpetuels = [], []
    for nom in SUSPECTS:
        restaure()
        e = passages(nom, 3)
        court = [x[:10] if x else "—" for x in e]
        if e[0] != e[1] and e[1] == e[2]:
            lect, cible = "**convergence en un pas**", convergents
        elif e[0] != e[1] and e[1] != e[2]:
            lect, cible = "**dérive perpétuelle**", perpetuels
        else:
            lect, cible = "*stable dès P1 — non reproduit*", []
        if cible != []:
            cible.append(nom)
        L.append(f"| `{nom}` | `{court[0]}` | `{court[1]}` | `{court[2]}` | {lect} |")
    restaure()
    L.append("")
    if convergents and not perpetuels:
        L.append(f"**Les {len(convergents)} cas convergent en un pas.** La")
        L.append("non-idempotence est réelle — deux lecteurs obtiennent deux textes —")
        L.append("mais elle ne s'aggrave pas : le rapport s'inclut lui-même une fois,")
        L.append("puis se stabilise.")
        L.append("")
        L.append("> **C'est moins grave que « dérive perpétuelle », et plus sournois** :")
        L.append("> un cycle qui régénère deux fois ne verra plus rien, et conclura à")
        L.append("> tort que le rapport est stable.")
    elif perpetuels:
        L.append(f"**{len(perpetuels)} cas dérivent sans se stabiliser.** Le rapport")
        L.append("change à chaque exécution : toute comparaison à une régénération est")
        L.append("sans valeur.")
    L.append("")

    # ------------------------------------------------------------------ B
    L.append("## B. Le mécanisme est-il bien l'auto-inclusion ?")
    L.append("")
    L.append("Un rapport qui se compte lui-même doit **se nommer** dans son propre")
    L.append("texte au passage où il apparaît.")
    L.append("")
    L.append("| Script | Se nomme dans son rapport | Verdict |")
    L.append("|---|---|---|")
    okB = True
    for nom in SUSPECTS:
        restaure()
        sh(sys.executable, str(SCRIPTS / f"nonml_{nom}_backtest.py"))
        sh(sys.executable, str(SCRIPTS / f"nonml_{nom}_backtest.py"))
        t = (RESULTS / f"nonml_{nom}_result.md").read_text(encoding="utf-8")
        vu = f"nonml_{nom}_result.md" in t or f"`{nom}`" in t
        okB = okB and vu
        L.append(f"| `{nom}` | {'**oui**' if vu else 'non'} | "
                 f"{'auto-inclusion **confirmée**' if vu else 'mécanisme *autre*'} |")
    restaure()
    L.append("")
    L.append(f"**{'CONCORDANT' if okB else 'ÉCART'}** — le mécanisme annoncé par le")
    L.append("rapport est celui qu'on observe.")
    L.append("")

    # ------------------------------------------------------------------ C
    L.append("## C. Qui écrit les rapports hors périmètre ?")
    L.append("")
    L.append("Le backtest constate **8** rapports réécrits sans dire par qui. On")
    L.append("attribue, en rejouant chaque suspect **seul**.")
    L.append("")
    attributions = {}
    for nom in SUSPECTS:
        f = touche_par(nom)
        hors = [x for x in f if x != f"nonml_{nom}_result.md"]
        attributions[nom] = hors
        L.append(f"### `{nom}`")
        L.append("")
        if hors:
            L.append(f"Écrit **{len(hors)}** fichier(s) qui ne sont pas son rapport :")
            L.append("")
            for x in hors:
                L.append(f"- `{x}`")
        else:
            L.append("N'écrit **que** son propre rapport.")
        L.append("")
    total_attribue = sum(len(v) for v in attributions.values())
    L.append(f"**{total_attribue}** écriture(s) hors rapport propre attribuée(s) aux")
    L.append("deux suspects. Le reste vient d'autres scripts du lot, non attribué ici :")
    L.append("l'attribution complète demanderait 18 exécutions isolées, et **ce cycle")
    L.append("ne la promet pas**.")
    L.append("")

    # ------------------------------------------------------------------ D
    L.append("## D. Mon propre rapport est-il idempotent ?")
    L.append("")
    mien = RESULTS / f"nonml_{MOI}_result.md"
    a = emp(mien)
    sh(sys.executable, str(SCRIPTS / f"nonml_{MOI}_backtest.py"), timeout=1800)
    b = emp(mien)
    okD = a is not None and a == b
    L.append(f"- avant : `{(a or '—')[:16]}`")
    L.append(f"- après : `{(b or '—')[:16]}`")
    L.append("")
    L.append(f"**{'CONCORDANT' if okD else 'ÉCART'}** — un cycle qui dénonce la")
    L.append("non-idempotence des autres doit commencer par la sienne.")
    L.append("")

    tous = okB and okD and not perpetuels
    L.append("## Ce que cet audit ne couvre pas")
    L.append("")
    L.append("- Il n'attribue pas les **8** écritures hors périmètre à tous leurs")
    L.append("  auteurs — seulement à ceux qu'il a rejoués.")
    L.append("- Il ne teste que **3** passages : une dérive à période plus longue lui")
    L.append("  échapperait.")
    L.append("- Il ne dit rien des **296** scripts hors de l'univers.")
    L.append("")
    L.append(f"## Verdict — **{'CONCORDANT' if tous else 'ÉCART'}**")
    L.append("")
    L.append("Le mécanisme annoncé est confirmé, et ce cycle est idempotent." if tous
             else "**Au moins un contrôle échoue — voir ci-dessus.**")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()
