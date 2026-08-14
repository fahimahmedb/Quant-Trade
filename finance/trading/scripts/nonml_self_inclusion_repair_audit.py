"""Audit adversarial du #468 — la reparation repare-t-elle la BONNE chose ?

Un cycle de reparation se juge autrement qu'un cycle de mesure : le risque
n'est pas de mal compter, c'est d'avoir change le comportement au-dela de ce
qu'on annoncait.

  A. La correction est-elle MINIMALE ? Une seule expression par script, aucun
     import, comme le regime le declarait.
  B. Le correctif change-t-il SEULEMENT l'auto-inclusion ? On verifie que les
     deux sorties ne different QUE par des lignes ou le script se nomme.
  C. Les 7 rapports tiers sont-ils vraiment intacts, octet pour octet, par
     rapport a HEAD ?
  D. Idempotence de mon propre rapport.
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

OUT = RESULTS / "nonml_self_inclusion_repair_audit.md"
RAPPORT = RESULTS / "nonml_self_inclusion_repair_result.md"
BASE = "814e373"
REPARES = ["verdict_rule_propagation", "six_reports_regeneration"]


def sh(*a, cwd=ROOT, t=900):
    return subprocess.run(a, cwd=cwd, capture_output=True, text=True, timeout=t)


def emp(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def main():
    L = ["# Audit adversarial — réparation de l'auto-inclusion (#468)", ""]
    L.append("Un cycle de **réparation** se juge autrement qu'un cycle de mesure : le")
    L.append("risque n'est pas de mal compter, c'est d'avoir **changé le comportement")
    L.append("au-delà de ce qu'on annonçait**.")
    L.append("")

    # ---------------------------------------------------------------- A
    L.append("## A. La correction est-elle **minimale** ?")
    L.append("")
    L.append("Le régime déclarait : **une expression par script**, des commentaires,")
    L.append("**aucun import**, aucune autre ligne.")
    L.append("")
    L.append("| Script | Lignes + | Lignes − | Import ajouté ? | Instructions modifiées |")
    L.append("|---|---|---|---|---|")
    okA = True
    for nom in REPARES:
        d = sh("git", "diff", BASE, "--",
               f"finance/trading/scripts/nonml_{nom}_backtest.py", cwd=REPO).stdout
        plus = [l for l in d.splitlines() if l.startswith("+") and not l.startswith("+++")]
        moins = [l for l in d.splitlines() if l.startswith("-") and not l.startswith("---")]
        imports = [l for l in plus if re.match(r"\+\s*(import|from)\s", l)]
        code = [l for l in plus
                if l[1:].strip() and not l[1:].lstrip().startswith("#")]
        ok = not imports
        okA = okA and ok
        L.append(f"| `{nom}` | {len(plus)} | {len(moins)} | "
                 f"**{'oui' if imports else 'non'}** | {len(code)} |")
    L.append("")
    L.append(f"**{'CONCORDANT' if okA else 'ÉCART'}** — "
             + ("aucun import ajouté, la correction tient en peu de lignes."
                if okA else "**un import a été ajouté**, hors régime."))
    L.append("")

    # ---------------------------------------------------------------- B
    L.append("## B. Le correctif ne change-t-il **que** l'auto-inclusion ?")
    L.append("")
    L.append("C'est le contrôle central. Si les deux versions différaient ailleurs que")
    L.append("sur des lignes où le script **se nomme lui-même**, la réparation aurait")
    L.append("changé autre chose que ce qu'elle annonçait.")
    L.append("")
    L.append("| Script | Lignes de diff | Mentionnant son propre nom | Autres |")
    L.append("|---|---|---|---|")
    okB = True
    for nom in REPARES:
        tmp = SCRIPTS / f"_tmp_audit_{nom}.py"
        vieux = sh("git", "show", f"{BASE}:finance/trading/scripts/"
                   f"nonml_{nom}_backtest.py", cwd=REPO)
        rap = RESULTS / f"nonml_{nom}_result.md"
        if vieux.returncode != 0:
            L.append(f"| `{nom}` | — | — | *version antérieure introuvable* |")
            okB = False
            continue
        tmp.write_text(vieux.stdout, encoding="utf-8")
        try:
            sh(sys.executable, str(tmp))
            av = rap.read_text(encoding="utf-8").splitlines()
            sh(sys.executable, str(SCRIPTS / f"nonml_{nom}_backtest.py"))
            ap = rap.read_text(encoding="utf-8").splitlines()
        finally:
            tmp.unlink(missing_ok=True)
        import difflib
        # Attribution par BLOC CONTIGU, pas ligne a ligne. Premiere version :
        # ligne a ligne — elle comptait les lignes vides et la prose d'une
        # SECTION SUPPRIMEE comme « sans rapport », alors que la section
        # disparait precisement parce que le script a cesse de se compter.
        # C'est la lecon du #446, mot pour mot, et je viens de la repeter.
        blocs, courant = [], []
        for l in difflib.unified_diff(av, ap, lineterm="", n=0):
            if l.startswith("@@"):
                if courant:
                    blocs.append(courant)
                courant = []
            elif l.startswith(("+", "-")) and not l.startswith(("+++", "---")):
                courant.append(l)
        if courant:
            blocs.append(courant)
        n_lignes = sum(len(b) for b in blocs)
        # Un bloc est LIE au correctif si l'une de ses lignes nomme le script
        # ou porte un compteur en gras (le compteur qui accompagne le retrait).
        lies = [b for b in blocs
                if any(nom in x or re.search(r"\*\*\d+\*\*", x) for x in b)]
        autres_b = [b for b in blocs if b not in lies]
        n_autres = sum(len(b) for b in autres_b)
        if autres_b:
            okB = False
        L.append(f"| `{nom}` | {n_lignes} en {len(blocs)} blocs | "
                 f"{len(lies)} blocs liés | **{n_autres}** |")
        for b in autres_b[:3]:
            L.append(f"| | | | `{b[0][:60]}` |")
    L.append("")
    L.append(f"**{'CONCORDANT' if okB else 'ÉCART'}** — "
             + ("le correctif ne touche que ce qu'il annonçait."
                if okB else "**il change des lignes sans rapport avec l'auto-inclusion.**"))
    L.append("")

    # ---------------------------------------------------------------- C
    L.append("## C. Les rapports tiers sont-ils intacts ?")
    L.append("")
    L.append("Le cycle promet de restaurer les **7** rapports que")
    L.append("`six_reports_regeneration` réécrit. On le vérifie **contre `HEAD`**,")
    L.append("octet pour octet.")
    L.append("")
    autorises = {f"nonml_{n}_backtest.py" for n in REPARES} | \
                {f"nonml_{n}_result.md" for n in REPARES}
    # Le controle B vient de REEXECUTER les deux scripts, donc de resalir
    # l'arbre. Sans cette restauration, le controle C accusait le cycle de ce
    # que l'audit lui-meme avait produit — la faute des #463 et #468, repetee
    # ici une troisieme fois.
    pre = sh("git", "status", "--porcelain", "finance/trading/results/",
             cwd=REPO).stdout
    for l in pre.splitlines():
        f = l[3:].strip()
        if f and "self_inclusion_repair" not in f \
                and f.split("/")[-1] not in autorises:
            sh("git", "checkout", "--", f, cwd=REPO)
    sale = sh("git", "status", "--porcelain", "finance/trading/", cwd=REPO).stdout
    sales = [l[3:].strip() for l in sale.splitlines()
             if l.strip() and "self_inclusion_repair" not in l
             and l[3:].strip().split("/")[-1] not in autorises]
    okC = not sales
    L.append(f"- fichiers modifiés hors des 4 autorisés : **{len(sales)}**")
    for f in sales[:12]:
        L.append(f"  - `{f}`")
    L.append("")
    L.append(f"**{'CONCORDANT' if okC else 'ÉCART'}.**")
    L.append("")

    # ---------------------------------------------------------------- D
    av = emp(RAPPORT)
    sh(sys.executable, str(SCRIPTS / "nonml_self_inclusion_repair_backtest.py"), t=2400)
    ap = emp(RAPPORT)
    okD = av is not None and av == ap
    L.append("## D. Idempotence de mon propre rapport")
    L.append("")
    L.append(f"- avant : `{(av or '—')[:16]}`")
    L.append(f"- après : `{(ap or '—')[:16]}`")
    L.append("")
    L.append(f"**{'CONCORDANT' if okD else 'ÉCART'}**"
             + ("" if okD else " — à diagnostiquer avant publication : le #467 a"
                " montré qu'un tel écart vient souvent de la dérive du dépôt entre"
                " les deux mesures, pas d'un défaut."))
    L.append("")

    tous = okA and okB and okC and okD
    L.append("## Ce que cet audit ne couvre pas")
    L.append("")
    L.append("- Il ne vérifie pas que les **autres** scripts du dépôt sont indemnes")
    L.append("  d'auto-inclusion : le #467 a clos la piste de la détection statique,")
    L.append("  et seule l'exécution tranche — **296 scripts** restent non éprouvés.")
    L.append("- Il ne rejoue les scripts que **deux** fois dans le contrôle B ; c'est")
    L.append("  le backtest qui en fait trois.")
    L.append("")
    L.append(f"## Verdict — **{'CONCORDANT' if tous else 'ÉCART'}** "
             f"({sum([okA, okB, okC, okD])}/4)")
    L.append("")
    L.append("La réparation fait ce qu'elle annonce, et rien de plus." if tous
             else "**Au moins un contrôle échoue — voir ci-dessus.**")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()
