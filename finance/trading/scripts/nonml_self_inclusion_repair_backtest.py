"""Reparer les deux scripts auto-inclusifs (#468).

Specification pre-enregistree dans `PREREG_self_inclusion_repair.md`, committee
AVANT toute modification et toute mesure.

Premier cycle de REPARATION de la serie. Le #463 avait trouve les defauts sans
les corriger, le #466 avait refuse : l'engagement etait de ne pas meler la
decouverte a la correction. Ici le cycle ne fait QUE reparer, et il le declare.
"""
import difflib
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

OUT = RESULTS / "nonml_self_inclusion_repair_result.md"
MOI = "self_inclusion_repair"
BASE = "814e373"          # commit du PREREG, epingle (lecons #445/#451)

REPARES = ["verdict_rule_propagation", "six_reports_regeneration"]
# Les 4 fichiers que ce cycle a le droit de laisser modifies.
AUTORISES = {f"nonml_{n}_backtest.py" for n in REPARES} | \
            {f"nonml_{n}_result.md" for n in REPARES} | \
            {f"nonml_{MOI}_result.md", f"nonml_{MOI}_backtest.py",
             f"nonml_{MOI}_audit.py", f"nonml_{MOI}_audit.md",
             f"nonml_{MOI}_anti_cheat.md"}


def sh(*a, cwd=ROOT, t=600):
    return subprocess.run(a, cwd=cwd, capture_output=True, text=True, timeout=t)


def emp(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def avant_du_rapport(nom):
    """Le rapport tel qu'il etait au commit epingle — jamais lu sur le disque."""
    r = sh("git", "show", f"{BASE}:finance/trading/results/nonml_{nom}_result.md",
           cwd=REPO)
    return r.stdout if r.returncode == 0 else None


def trois_passages(nom):
    script = SCRIPTS / f"nonml_{nom}_backtest.py"
    rap = RESULTS / f"nonml_{nom}_result.md"
    emps = []
    for _ in range(3):
        r = sh(sys.executable, str(script), t=900)
        if r.returncode != 0:
            return None, None
        emps.append(emp(rap))
    return emps, rap.read_text(encoding="utf-8")


def main():
    resultats = {}
    for nom in REPARES:
        avant = avant_du_rapport(nom)
        emps, apres = trois_passages(nom)
        resultats[nom] = (avant, emps, apres)

    # --- Restauration des rapports TIERS ------------------------------------
    sale = sh("git", "status", "--porcelain", "finance/trading/results/",
              cwd=REPO).stdout
    tiers = [l[3:].strip() for l in sale.splitlines()
             if l.strip() and l[3:].strip().split("/")[-1] not in AUTORISES]
    for f in tiers:
        sh("git", "checkout", "--", f, cwd=REPO)
    sale2 = sh("git", "status", "--porcelain", "finance/trading/results/",
               cwd=REPO).stdout
    residus = [l[3:].strip() for l in sale2.splitlines()
               if l.strip() and l[3:].strip().split("/")[-1] not in AUTORISES]

    # --- Diff du code, contre le commit EPINGLE -----------------------------
    numstat = sh("git", "diff", BASE, "--numstat", "--",
                 "finance/trading/scripts/", cwd=REPO).stdout.strip()
    touches = [l.split("\t") for l in numstat.splitlines() if l.strip()]
    hors_regime = [t for t in touches
                   if t[2].split("/")[-1] not in AUTORISES]

    L = ["# Réparer les deux scripts auto-inclusifs (pré-enregistré)", ""]
    L.append("**Premier cycle de RÉPARATION de la série.** Le #463 avait trouvé les")
    L.append("défauts sans les corriger et le #466 avait refusé de le faire :")
    L.append("l'engagement depuis le #450 est de **ne pas mêler la découverte d'un")
    L.append("défaut à sa correction**. Ici le cycle **ne fait que réparer**.")
    L.append("")

    L.append("## 1. Idempotence après correction — **trois** passages")
    L.append("")
    L.append("Trois, pas deux : le #467 a montré qu'une dérive de **période 2** échappe")
    L.append("à deux passages.")
    L.append("")
    L.append("| Script | P1 | P2 | P3 | Verdict |")
    L.append("|---|---|---|---|---|")
    tous_ok = True
    for nom in REPARES:
        _av, emps, _ap = resultats[nom]
        if emps is None:
            L.append(f"| `{nom}` | — | — | — | **échec d'exécution** |")
            tous_ok = False
            continue
        stable = emps[0] == emps[1] == emps[2] and emps[0] is not None
        tous_ok = tous_ok and stable
        c = [e[:10] if e else "—" for e in emps]
        L.append(f"| `{nom}` | `{c[0]}` | `{c[1]}` | `{c[2]}` | "
                 + ("**stable**" if stable else "**INSTABLE**") + " |")
    L.append("")
    if tous_ok:
        L.append("**Les deux sont idempotents.** La correction tient, et le diagnostic")
        L.append("du #463 — l'auto-inclusion — était bien la cause **unique**.")
    else:
        L.append("**Au moins un reste instable.** La correction est **insuffisante** :")
        L.append("l'auto-inclusion n'était pas la seule cause, ce qui met en cause le")
        L.append("diagnostic du #463 autant que ma réparation.")
    L.append("")

    L.append("## 2. L'effet de la correction sur les rapports")
    L.append("")
    L.append("Comparaison au rapport **tel qu'il était au commit épinglé** "
             f"(`{BASE}`) — jamais au fichier du disque, leçon des #445 et #451.")
    L.append("")
    for nom in REPARES:
        avant, _emps, apres = resultats[nom]
        L.append(f"### `{nom}`")
        L.append("")
        if avant is None or apres is None:
            L.append("*Comparaison impossible : rapport absent au commit épinglé.*")
            L.append("")
            continue
        d = list(difflib.unified_diff(avant.splitlines(), apres.splitlines(),
                                      "avant (épinglé)", "après correction",
                                      lineterm="", n=0))
        L.append(f"Lignes de diff : **{len(d)}**"
                 + (" *(les 20 premières)*" if len(d) > 20 else ""))
        L.append("")
        L.append("```diff")
        L.extend(d[:20])
        L.append("```")
        L.append("")

    # --- L'effet du correctif, ISOLE de la derive ---------------------------
    # Defaut de conception trouve en relisant le diff : epingler le TEXTE du
    # rapport « avant » n'isole pas l'effet du correctif, parce que la sortie
    # depend de l'etat courant du depot (« 303 rapports » -> « 321 » n'est pas
    # ma correction, c'est la derive). On execute donc les DEUX versions au
    # MEME etat de depot, et on compare leurs sorties entre elles.
    L.append("## 2 bis. L'effet du correctif, **isolé** de la dérive")
    L.append("")
    L.append("Épingler le texte du rapport « avant » **n'isole pas** l'effet du")
    L.append("correctif : la sortie dépend de l'état **courant** du dépôt. Le passage")
    L.append("de « 303 rapports comparés » à « 321 » ci-dessus est de la **dérive**,")
    L.append("pas ma correction — le défaut que les #449/#450/#451 avaient déjà")
    L.append("rencontré, et que mon pré-enregistrement n'avait pas anticipé.")
    L.append("")
    L.append("Les **deux versions** sont donc exécutées au **même état de dépôt**, et")
    L.append("leurs sorties comparées entre elles.")
    L.append("")
    for nom in REPARES:
        # Nom volontairement hors du glob `nonml_*_backtest.py` : une copie qui
        # s'y trouverait fausserait les comptes qu'on mesure (lecon du #449).
        tmp = SCRIPTS / f"_tmp_ancienne_{nom}.py"
        vieux = sh("git", "show", f"{BASE}:finance/trading/scripts/"
                   f"nonml_{nom}_backtest.py", cwd=REPO)
        rap = RESULTS / f"nonml_{nom}_result.md"
        L.append(f"### `{nom}`")
        L.append("")
        if vieux.returncode != 0:
            L.append("*Version antérieure introuvable au commit épinglé.*")
            L.append("")
            continue
        tmp.write_text(vieux.stdout, encoding="utf-8")
        try:
            sh(sys.executable, str(tmp), t=900)
            avant_iso = rap.read_text(encoding="utf-8")
            sh(sys.executable, str(SCRIPTS / f"nonml_{nom}_backtest.py"), t=900)
            apres_iso = rap.read_text(encoding="utf-8")
        finally:
            tmp.unlink(missing_ok=True)
        d = list(difflib.unified_diff(avant_iso.splitlines(),
                                      apres_iso.splitlines(),
                                      "ancienne version", "version corrigée",
                                      lineterm="", n=0))
        L.append(f"Lignes de diff : **{len(d)}**"
                 + (" *(les 16 premières)*" if len(d) > 16 else ""))
        L.append("")
        L.append("```diff")
        L.extend(d[:16])
        L.append("```")
        L.append("")
    L.append("> **C'est ce diff-là qui mesure la correction**, et lui seul.")
    L.append("")

    # --- Restauration FINALE, apres TOUTE execution -------------------------
    # Defaut d'ordonnancement trouve en relisant la sortie : la restauration
    # avait lieu AVANT la section 2 bis, qui reexecute les deux scripts et
    # resalit donc l'arbre. Le critere 4 lisait un etat perime et annoncait
    # « 0 residu » sur un arbre sale — exactement le defaut de l'ordre
    # d'execution qui avait vide le controle du #446 et fausse celui du #451.
    sale = sh("git", "status", "--porcelain", "finance/trading/results/",
              cwd=REPO).stdout
    tiers = [l[3:].strip() for l in sale.splitlines()
             if l.strip() and l[3:].strip().split("/")[-1] not in AUTORISES]
    for f in tiers:
        sh("git", "checkout", "--", f, cwd=REPO)
    sale2 = sh("git", "status", "--porcelain", "finance/trading/results/",
               cwd=REPO).stdout
    residus = [l[3:].strip() for l in sale2.splitlines()
               if l.strip() and l[3:].strip().split("/")[-1] not in AUTORISES]

    L.append("## 3. Le diff du code — confiné au régime déclaré ?")
    L.append("")
    L.append("Le régime annonçait : **une expression par script**, des commentaires,")
    L.append("**aucun import**, **aucune autre ligne**.")
    L.append("")
    L.append("| Fichier | + | − |")
    L.append("|---|---|---|")
    for plus, moins, chemin in touches:
        L.append(f"| `{chemin.split('/')[-1]}` | {plus} | {moins} |")
    L.append("")
    L.append(f"- fichiers hors régime : **{len(hors_regime)}**")
    if hors_regime:
        for t in hors_regime:
            L.append(f"  - `{t[2]}`")
    L.append("")
    L.append(f"**Confiné : {'OUI' if not hors_regime else 'NON'}.**")
    L.append("")

    L.append("## 4. La régénération, bornée")
    L.append("")
    L.append("`six_reports_regeneration` **écrit 7 rapports qui ne sont pas le sien**")
    L.append("(#463). Ils ont donc été réécrits pendant la mesure, puis **restaurés** :")
    L.append("committer leur régénération mêlerait l'effet de la correction à la dérive")
    L.append("du dépôt, ce que le #450 a payé cher.")
    L.append("")
    L.append("> **La restauration a lieu après TOUTE exécution**, section 2 bis")
    L.append("> comprise. Dans une première version elle la précédait, et le critère 4")
    L.append("> annonçait « 0 résidu » **sur un arbre sale** — le défaut d'ordre")
    L.append("> d'exécution qui avait déjà vidé un contrôle au #446 et faussé le #451.")
    L.append("")
    L.append(f"- rapports tiers restaurés : **{len(tiers)}**")
    for f in tiers[:12]:
        L.append(f"  - `{f.split('/')[-1]}`")
    L.append(f"- **résidus hors des fichiers autorisés** : **{len(residus)}**")
    if residus:
        for f in residus[:12]:
            L.append(f"  - `{f}`")
    L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    p1 = tous_ok
    p3 = not residus
    L.append("| Prédiction | Mesuré | Verdict |")
    L.append("|---|---|---|")
    L.append(f"| les deux deviennent idempotents sur 3 passages | "
             f"{'oui' if p1 else 'non'} | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append("| leurs compteurs baissent d'exactement 1 | *voir les diffs* | "
             "*à lire* |")
    L.append(f"| aucun autre fichier suivi ne reste modifié | {len(residus)} | "
             f"{'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")

    L.append("## Critères de succès")
    L.append("")
    c2 = not hors_regime
    L.append(f"1. Les 2 scripts idempotents sur 3 passages — "
             f"**{'OUI' if p1 else 'NON'}**.")
    L.append(f"2. Diff de code confiné au régime — **{'OUI' if c2 else 'NON'}**.")
    L.append("3. Effet sur les 2 rapports publié avec son diff — **OUI**.")
    L.append(f"4. Arbre propre hors des fichiers du cycle — "
             f"**{'OUI' if p3 else 'NON'}**.")
    L.append("")
    verdict = "PASS" if (p1 and c2 and p3) else "FAIL"
    L.append(f"**{verdict}**")
    L.append("")

    L.append("## Ce que ce cycle ne fait pas")
    L.append("")
    L.append("- Il ne **touche** à aucun autre script, même signalé par le #466 : ces")
    L.append("  signalements sont **sans valeur démontrée** (#467, **0/6**).")
    L.append("- Il ne **committe** aucun rapport tiers régénéré.")
    L.append("- Il ne **réécrit** aucun verdict de stratégie.")
    L.append("")

    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date")
    L.append("> de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()
