"""Temoin de vraisemblance (lift) pour D500, D501, D497-P10 (#515).

Specification pre-enregistree dans `PREREG_untested_detectors_lift.md`,
committee AVANT toute mesure -- definitions, decoy et seuil de 3 compris.

Le #514 n'a teste que la couche contextuelle du #502. Trois couches
sous-jacentes -- l'extraction du #500, la confirmation brute du #501, la
primitive P10 du #497 -- n'avaient jamais subi de temoin. SANS RIEN EXECUTER.
"""
import ast
import importlib.util
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

OUT = RESULTS / "nonml_untested_detectors_lift_result.md"
MOI = "untested_detectors_lift"

SEUIL = 3.0             # lift minimal pour "discrimine", FIGE


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def module(nom):
    p = SCRIPTS / nom
    spec = importlib.util.spec_from_file_location("_m_" + p.stem, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def lift(n, na, nb, nab):
    pa, pb, pab = na / n, nb / n, nab / n
    attendu = pa * pb
    return (pab / attendu) if attendu > 0 else None, pa, pb, pab


def decoy_9c(v):
    """Complement a 9 chiffre par chiffre sur la partie entiere. d -> 9-d."""
    if "," in v:
        ent, dec = v.split(",", 1)
        suffixe = "," + dec
    elif "." in v:
        ent, dec = v.split(".", 1)
        suffixe = "." + dec
    else:
        ent, suffixe = v, ""
    ent = ent.lstrip("-")
    if not ent.isdigit():
        return None
    comp = "".join(str(9 - int(c)) for c in ent)
    if comp[0] == "0":
        return None            # indetermine, declare au pre-enregistrement
    return comp + suffixe


def main():
    avant = set(git("status", "--porcelain").splitlines())

    c500 = module("nonml_borrowed_figures_census_backtest.py")
    c501 = module("nonml_borrowed_figures_confrontation_backtest.py")
    c497 = module("nonml_execution_primitives_census_backtest.py")

    # === D500 : co-occurrence #NNN / nombre en gras dans une chaine =======
    chaines = []
    for py in sorted(SCRIPTS.glob("nonml_*.py")):
        if MOI in py.name:
            continue
        try:
            arbre = ast.parse(py.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for txt, _ in c500.chaines_publiees(arbre):
            chaines.append(txt)
    n500 = len(chaines)
    a500 = sum(1 for c in chaines if c500.CYCLE.search(c))
    b500 = sum(1 for c in chaines if c500.NOMBRE_GRAS.search(c))
    ab500 = sum(1 for c in chaines
               if c500.CYCLE.search(c) and c500.NOMBRE_GRAS.search(c))
    lift500, pa500, pb500, pab500 = lift(n500, a500, b500, ab500)

    # === D497-P10 : import nonml_* / .main() sur N'IMPORTE QUEL objet =====
    existants = {p.stem for p in SCRIPTS.glob("nonml_*.py")}
    scripts = [p for p in sorted(SCRIPTS.glob("nonml_*.py")) if MOI not in p.name]
    a497, b497, ab497 = 0, 0, 0
    for py in scripts:
        try:
            src = py.read_text(encoding="utf-8")
            arbre = ast.parse(src)
        except (SyntaxError, UnicodeDecodeError):
            continue
        par_alias, _ = c497.alias_imports(arbre, existants)
        importe = bool(par_alias)
        main_qq_part = any(isinstance(n, ast.Attribute) and n.attr == "main"
                           for n in ast.walk(arbre))
        p10_reel = bool(c497.primitives(src, arbre, existants).get("P10"))
        a497 += int(importe)
        b497 += int(main_qq_part)
        ab497 += int(p10_reel)
    n497 = len(scripts)
    lift497, pa497, pb497, pab497 = lift(n497, a497, b497, ab497)

    # === D501 : valeur reelle vs decoy (complement a 9), "en gras" =========
    secs = c501.sections_backlog()
    rapports = {f.name: f.read_text(encoding="utf-8") for f in
                sorted(RESULTS.glob("*.md")) if MOI not in f.name
                and not _bad(f)}
    corpus = list(secs.values()) + list(rapports.values())

    emprunts = []
    for py in sorted(SCRIPTS.glob("nonml_*.py")):
        if any(k in py.name for k in (c500.MOI, c501.MOI, MOI)):
            continue
        try:
            arbre = ast.parse(py.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for txt, cy, nb in c500.emprunts_de(arbre):
            for g in nb:
                v = c501.chiffres_seuls(g)
                if v is not None:
                    emprunts.append(v)

    def trouve(v):
        return any(c501.en_gras_dans(v, t) for t in corpus)

    n501, indet, trouve_reel, trouve_decoy = 0, 0, 0, 0
    for v in emprunts:
        d = decoy_9c(v)
        if d is None:
            indet += 1
            continue
        n501 += 1
        trouve_reel += int(trouve(v))
        trouve_decoy += int(trouve(d))

    taux_reel = 100.0 * trouve_reel / n501 if n501 else 0.0
    taux_decoy = 100.0 * trouve_decoy / n501 if n501 else 0.0
    ratio501 = (taux_reel / taux_decoy) if taux_decoy > 0 else None

    passe500 = lift500 is not None and lift500 >= SEUIL
    passe497 = lift497 is not None and lift497 >= SEUIL
    passe501 = ratio501 is not None and ratio501 >= SEUIL

    L = []
    A = L.append
    A("# Un témoin de vraisemblance pour les détecteurs jamais testés")
    A("")
    A("Le **#514** n'a testé que la couche contextuelle du #502. Trois couches")
    A("sous-jacentes — utilisées par toute la série #500-#514 — n'avaient")
    A("**jamais** subi de témoin.")
    A("")
    A("## La méthode, citée verbatim")
    A("")
    A("> `lift = P(A ET B) / (P(A) × P(B))` — **≥ 3** : discrimine ; "
      "**< 3** : recoupe deux événements fréquents, sans plus.")
    A("")
    A("## D500 — l'extraction du #500")
    A("")
    A("`A` = la chaîne contient `#NNN` ; `B` = elle contient un nombre en gras.")
    A("")
    A(f"- chaînes publiées analysées : **{n500}**")
    A(f"- `P(A)` = **{a500}**/{n500} = " + f"{pa500*100:.1f} %".replace(".", ","))
    A(f"- `P(B)` = **{b500}**/{n500} = " + f"{pb500*100:.1f} %".replace(".", ","))
    A(f"- `P(A∩B)` observé = **{ab500}**/{n500} = "
      + f"{pab500*100:.1f} %".replace(".", ","))
    A(f"- attendu sous indépendance = " + f"{pa500*pb500*100:.2f} %".replace(".", ","))
    A((f"- **lift = {lift500:.1f}**".replace(".", ",")) if lift500 is not None else "- lift indéterminé")
    A(f"- verdict : **{'DISCRIMINE' if passe500 else 'NE DISCRIMINE PAS'}**")
    A("")
    A("## D497-P10 — la primitive « exécution en process »")
    A("")
    A("`A` = le script importe un module `nonml_*` ; `B` = il appelle `.main()`")
    A("sur **n'importe quel** objet, sans exiger que ce soit l'alias importé.")
    A("")
    A(f"- scripts analysés : **{n497}**")
    A(f"- `P(A)` = **{a497}**/{n497} = " + f"{pa497*100:.1f} %".replace(".", ","))
    A(f"- `P(B)` = **{b497}**/{n497} = " + f"{pb497*100:.1f} %".replace(".", ","))
    A(f"- `P(A∩B)` observé — **la vraie règle P10**, même alias — = "
      f"**{ab497}**/{n497} = " + f"{pab497*100:.1f} %".replace(".", ","))
    A(f"- attendu sous indépendance = " + f"{pa497*pb497*100:.2f} %".replace(".", ","))
    A((f"- **lift = {lift497:.1f}**".replace(".", ",")) if lift497 is not None else "- lift indéterminé")
    A(f"- verdict : **{'DISCRIMINE' if passe497 else 'NE DISCRIMINE PAS'}**")
    A("")
    A("## D501 — la confirmation brute « en gras quelque part »")
    A("")
    A("`decoy(v)` = complément à 9 chiffre par chiffre sur la partie entière")
    A("de `v` (`d → 9-d`) ; partie décimale inchangée ; **indéterminé et")
    A("exclu** si le chiffre de tête du complément vaut `0`.")
    A("")
    A(f"- valeurs empruntées : **{len(emprunts)}**")
    A(f"- indéterminées (exclues) : **{indet}**")
    A(f"- évaluées : **{n501}**")
    A("")
    A("| | Trouvée en gras quelque part | Taux |")
    A("|---|---|---|")
    A(f"| **valeur réelle** | **{trouve_reel}**/{n501} | "
      + f"**{taux_reel:.1f} %**".replace(".", ",") + " |")
    A(f"| **decoy** (complément à 9) | **{trouve_decoy}**/{n501} | "
      + f"**{taux_decoy:.1f} %**".replace(".", ",") + " |")
    A("")
    A(f"- rapport réel/decoy : "
      + (f"**{ratio501:.1f}**".replace(".", ",")
         if ratio501 is not None else "**indéterminé** (decoy jamais trouvé)"))
    A(f"- verdict : **{'DISCRIMINE' if passe501 else 'NE DISCRIMINE PAS'}**")
    A("")
    A("## Le résumé")
    A("")
    A("| Détecteur | Mesure | Seuil | Verdict |")
    A("|---|---|---|---|")
    A(f"| **D500** (#500) | lift " + f"{lift500:.1f}".replace(".", ",") + f" | ≥ {SEUIL:.0f} | "
      f"**{'PASSE' if passe500 else 'ÉCHOUE'}** |")
    A(f"| **D497-P10** (#497) | lift " + f"{lift497:.1f}".replace(".", ",") + f" | ≥ {SEUIL:.0f} | "
      f"**{'PASSE' if passe497 else 'ÉCHOUE'}** |")
    r501s = (f"{ratio501:.1f}".replace(".", ",")) if ratio501 is not None else "indéterminé"
    A(f"| **D501** (#501) | rapport {r501s} | ≥ {SEUIL:.0f} | "
      f"**{'PASSE' if passe501 else 'ÉCHOUE'}** |")
    A("")
    n_passe = sum([passe500, passe497, passe501])
    A(f"- détecteurs qui discriminent : **{n_passe}** sur **3**")
    A("")
    if passe500 and passe497 and not passe501:
        A("> **Le schéma annoncé au pré-enregistrement se confirme.** Les deux")
        A("> couches structurelles (extraction du #500, primitive P10 du #497)")
        A("> mesurent une conjonction réelle. **La confirmation brute du #501 —")
        A("> « en gras quelque part », sans contrainte de sujet — ne discrimine")
        A("> pas** : un decoy fabriqué par une transformation arbitraire des")
        A("> chiffres se retrouve « confirmé » presque aussi souvent que la")
        A("> vraie valeur. **C'est exactement pourquoi le #502 a dû ajouter les")
        A("> mots-clés** : sans eux, la couche #501 seule ne prouvait rien, et")
        A("> ce cycle en donne enfin la mesure.")
    elif n_passe == 3:
        A("> **Les trois détecteurs discriminent.** Contrairement à l'attente du")
        A("> pré-enregistrement, même la confirmation brute du #501 dépasse le")
        A("> hasard — la prédiction 3 est réfutée, et il faut l'écrire.")
    elif n_passe == 0:
        A("> **Aucun des trois ne discrimine.** Toute la chaîne #500-#511 aurait")
        A("> reposé sur des conjonctions de fréquence, pas de sens — un constat")
        A("> plus large que celui du #512/#513.")
    A("")
    A("## Mes trois prédictions, confrontées")
    A("")
    A("| Prédiction | Annoncé | Mesuré | Verdict |")
    A("|---|---|---|---|")
    A(f"| D500 discrimine (lift ≥ 3) | oui | " + f"{lift500:.1f}".replace(".", ",") + " | "
      f"**{'vérifiée' if passe500 else 'réfutée'}** |")
    A(f"| D497-P10 discrimine (lift ≥ 3) | oui | " + f"{lift497:.1f}".replace(".", ",") + " | "
      f"**{'vérifiée' if passe497 else 'réfutée'}** |")
    A(f"| D501 NE discrimine PAS (rapport < 3) | non | {r501s} | "
      f"**{'vérifiée' if not passe501 else 'réfutée'}** |")
    A("")
    A("## Aucune exécution")
    A("")
    apres = set(git("status", "--porcelain").splitlines())
    nouv = [l for l in sorted(apres - avant) if MOI not in l]
    A(f"- fichiers modifiés par ce cycle hors les siens : **{len(nouv)}**")
    for l in nouv:
        A(f"  - `{l.strip()}`")
    A("")
    A("Fonctions **importées** des backtests des #500, #501 et #497 — jamais")
    A("recopiées, jamais leur `main()`.")
    A("")
    A("## Critères de succès")
    A("")
    c = [("Les trois définitions (A, B, decoy) citées verbatim", True),
         ("Les trois lifts/rapports publiés avec leurs effectifs",
          n500 > 0 and n497 > 0 and n501 > 0),
         ("Verdict rendu pour chacun des trois au seuil de 3", True),
         (f"Indéterminés de D501 comptés (**{indet}**)", True),
         ("Aucun script exécuté, arbre propre", not nouv)]
    for i, (t, v) in enumerate(c, 1):
        A(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    A("")
    verdict = "PASS" if all(v for _, v in c) else "FAIL"
    A(f"**{verdict}** — le critère porte sur le **procédé**. **Il ne dépend pas")
    A("du succès des détecteurs testés**, seulement de la publication honnête")
    A("de leur verdict (leçon du #513).")
    A("")
    A("## Portée — ce que ce cycle ne retranche pas")
    A("")
    A("Un détecteur qui échoue ici **n'invalide pas rétroactivement** un cycle")
    A("qui l'utilisait en combinaison avec la couche contextuelle du #502,")
    A("déjà testée et validée au #514. La portée est **la couche testée**, pas")
    A("la chaîne complète.")
    A("")
    A("Simulation 300 € et robustesse **sans objet** : cycle de vérification,")
    A("aucune position, aucun paramètre numérique de stratégie.")
    A("")
    A("> **Rapport dépendant du dépôt** — il décrit l'état des scripts, du")
    A("> registre et des rapports à la date de son exécution.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — D500 lift={lift500:.1f} ({passe500}), "
          f"D497 lift={lift497:.1f} ({passe497}), "
          f"D501 rapport={r501s} ({passe501})")


def _bad(f):
    try:
        f.read_text(encoding="utf-8")
        return False
    except UnicodeDecodeError:
        return True


if __name__ == "__main__":
    main()
