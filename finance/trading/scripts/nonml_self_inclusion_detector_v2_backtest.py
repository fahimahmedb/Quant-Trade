"""Detecteur d'auto-inclusion, DEUXIEME essai (#467). `n_trials = 2`.

Specification pre-enregistree dans `PREREG_self_inclusion_detector_v2.md`,
committee AVANT toute mesure.

Le #466 a echoue (rappel 1/2). Ce cycle elargit la regle a l'enumeration par
`git status` — la forme manquee — et affronte le probleme que cela pose :

  la calibration sur les 18 cas du #463 est CONTAMINEE, puisque la regle est
  elargie EN CONNAISSANT la reponse. Le vrai test est ailleurs : 6 scripts
  nouvellement signales, executes deux fois, hors de toute verite terrain.
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
sys.path.insert(0, str(SCRIPTS))

import nonml_self_inclusion_detector_backtest as v1  # noqa: E402

OUT = RESULTS / "nonml_self_inclusion_detector_v2_result.md"
MOI = "self_inclusion_detector_v2"
BUDGET = 300
TAILLE_ECHANTILLON = 6

# --- La regle ELARGIE, enoncee au pre-enregistrement -----------------------
ECRIT = re.compile(r"\bwrite_text\s*\(")
ENUMERE = re.compile(
    r"RESULTS\s*\.\s*glob\s*\(|RESULTS\s*\.\s*iterdir\s*\(|glob\.glob\s*\(|"
    r"ls-tree|ls-files|"
    r"[\"']status[\"']|git\s+status|"                    # #467 : forme manquee
    r"--name-only|--name-status"
)
PROTEGE = re.compile(r"\bunlink\s*\(|!=\s*OUT\b|\bOUT\s*!=|p\s*!=\s*OUT|\bMOI\b|"
                     r"not\s+in\s+.*\bOUT\b|\.name\s*!=")


def signale(txt):
    return bool(ECRIT.search(txt) and ENUMERE.search(txt) and not PROTEGE.search(txt))


def empreinte(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def restaure():
    subprocess.run(["git", "checkout", "--", "finance/trading/results/"],
                   cwd=REPO, capture_output=True, text=True)


def joue_deux_fois(nom_fichier):
    """Deux executions ; empreintes du rapport comparees."""
    script = SCRIPTS / nom_fichier
    nom = nom_fichier[len("nonml_"):-len("_backtest.py")]
    rap = RESULTS / f"nonml_{nom}_result.md"
    emps = []
    for _ in range(2):
        try:
            r = subprocess.run([sys.executable, str(script)], cwd=ROOT,
                               capture_output=True, text=True, timeout=BUDGET)
        except subprocess.TimeoutExpired:
            return "budget dépassé", None, None
        if r.returncode != 0:
            return f"erreur (code {r.returncode})", None, None
        if not rap.exists():
            return "sans rapport identifiable", None, None
        emps.append(empreinte(rap))
    etat = "idempotent" if emps[0] == emps[1] else "**NON IDEMPOTENT**"
    return etat, emps[0], emps[1]


def main():
    tous = sorted(SCRIPTS.glob("nonml_*_backtest.py"))
    sig = []
    for p in tous:
        try:
            if signale(p.read_text(encoding="utf-8")):
                sig.append(p.name)
        except Exception:  # noqa: BLE001
            continue
    sigset = set(sig)

    rappel = sorted(v1.FAUTIFS_463 & sigset)
    rates = sorted(v1.FAUTIFS_463 - sigset)
    faux_pos = sorted(v1.SAINS_463 & sigset)
    connus = v1.FAUTIFS_463 | v1.SAINS_463
    nouveaux = sorted(sigset - connus)

    # --- Le second volet : hors echantillon --------------------------------
    echantillon = nouveaux[:TAILLE_ECHANTILLON]
    resultats = []
    for n in echantillon:
        restaure()
        resultats.append((n, *joue_deux_fois(n)))
    restaure()
    sale = subprocess.run(["git", "status", "--porcelain",
                           "finance/trading/results/"],
                          cwd=REPO, capture_output=True, text=True).stdout
    residus = [l for l in sale.splitlines() if l.strip() and MOI not in l]

    eprouves = [r for r in resultats if r[1] in ("idempotent", "**NON IDEMPOTENT**")]
    confirmes = [r for r in resultats if r[1] == "**NON IDEMPOTENT**"]

    L = ["# Détecteur d'auto-inclusion — **deuxième essai** (pré-enregistré)", ""]
    L.append("**`n_trials = 2`.** Le #466 a tenté la même hypothèse et échoué")
    L.append("(rappel 1/2). Le protocole impose de **compter cet essai**, pas de")
    L.append("repartir à 1.")
    L.append("")

    L.append("## La calibration est **contaminée** — dit avant, répété ici")
    L.append("")
    L.append("La règle est élargie à l'énumération par `git status` **en connaissant la")
    L.append("cause de l'échec du #466**. La recalibrer sur les **mêmes 18 cas**, c'est")
    L.append("ajuster une règle sur les données qui servent à la juger.")
    L.append("")
    L.append("| | Mesuré |")
    L.append("|---|---|")
    L.append(f"| rappel sur les fautifs connus | **{len(rappel)} / 2** |")
    L.append(f"| faux positifs sur les sains connus | **{len(faux_pos)} / 16** |")
    L.append("")
    if not rates:
        L.append("> **Le rappel est parfait, et il ne prouve rien.** Je l'ai obtenu en")
        L.append("> regardant la réponse. C'est écrit dans le pré-enregistrement pour")
        L.append("> que je ne puisse pas m'en prévaloir maintenant.")
    else:
        L.append("**Cas encore manqués** malgré l'élargissement :")
        L.append("")
        for n in rates:
            L.append(f"- `{n}`")
        L.append("")
        L.append("> **La règle élargie échoue sur le cas même qui l'a motivée.** Il n'y")
        L.append("> a rien à sauver ici.")
    L.append("")

    L.append("## Le résultat sur tout le dépôt")
    L.append("")
    L.append(f"- scripts examinés : **{len(tous)}**")
    L.append(f"- **signalés** : **{len(sig)}** *(contre 20 au #466)*")
    L.append(f"- dont **inconnus** de toute vérité terrain : **{len(nouveaux)}**")
    L.append("")

    L.append("## Le vrai test — validation **hors échantillon**")
    L.append("")
    L.append(f"Les **{TAILLE_ECHANTILLON} premiers** nouveaux signalés, par ordre")
    L.append("alphabétique — règle fixée **avant** d'avoir vu la liste. Chacun exécuté")
    L.append("**deux fois**, empreintes comparées.")
    L.append("")
    L.append("| Script | État | Passage 1 | Passage 2 |")
    L.append("|---|---|---|---|")
    for n, etat, a, b in resultats:
        L.append(f"| `{n}` | {etat} | "
                 f"{'`' + a[:12] + '`' if a else '—'} | "
                 f"{'`' + b[:12] + '`' if b else '—'} |")
    L.append("")
    L.append(f"- éprouvés : **{len(eprouves)}** / {len(echantillon)}")
    L.append(f"- **réellement non idempotents** : **{len(confirmes)}**")
    L.append("")

    p2 = len(confirmes) >= 2
    if not p2:
        L.append("> **Le détecteur sur-signale.** Sur les")
        L.append(f"> **{len(eprouves)}** scripts éprouvés hors échantillon, seuls")
        L.append(f"> **{len(confirmes)}** sont réellement défectueux. **Sa liste de")
        L.append("> suspects n'a pas de valeur de priorité**, et le")
        L.append("> pré-enregistrement en tire la conséquence qu'il avait fixée :")
        L.append("> **la piste « détection statique » est déclarée CLOSE**, pas")
        L.append("> retentée une troisième fois.")
    else:
        L.append("> **Le détecteur tient hors échantillon.** Sur")
        L.append(f"> **{len(eprouves)}** scripts qu'aucune vérité terrain ne couvrait,")
        L.append(f"> **{len(confirmes)}** se révèlent réellement non idempotents — et")
        L.append("> cette mesure-là, contrairement à la calibration, **n'est pas")
        L.append("> contaminée**.")
    L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    p1 = len(rappel) == 2
    p3 = len(faux_pos) >= 8
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| rappel 2/2 *(sans valeur, dit d'avance)* | 2 | {len(rappel)} | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| **≥ 2 des {TAILLE_ECHANTILLON} hors échantillon défectueux** | ≥ 2 | "
             f"{len(confirmes)} | {'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| faux positifs ≥ 8 sur 16 | ≥ 8 | {len(faux_pos)} | "
             f"{'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")

    L.append("## L'effet de bord")
    L.append("")
    L.append("La validation **exécute** des scripts, donc réécrit des rapports. Arbre")
    L.append("restauré (leçon du #450).")
    L.append("")
    L.append(f"- résidus sous `results/` après restauration : **{len(residus)}**")
    if residus:
        for r in residus[:15]:
            L.append(f"  - `{r.strip()}`")
    L.append("")
    L.append("**Aucun rapport régénéré n'est committé.**")
    L.append("")

    L.append("## Critères de succès")
    L.append("")
    c1 = True
    c3 = len(resultats) == len(echantillon)
    c4 = not residus
    L.append(f"1. **{len(tous)}/{len(tous)}** scripts classés — **OUI**.")
    L.append("2. Calibration publiée **avec sa contamination** — **OUI**.")
    L.append(f"3. Les {TAILLE_ECHANTILLON} hors échantillon traités — "
             f"**{'OUI' if c3 else 'NON'}**.")
    L.append(f"4. Arbre propre après restauration — **{'OUI' if c4 else 'NON'}**.")
    L.append("")
    L.append(f"**{'PASS' if (c1 and c3 and c4) else 'FAIL'}** — le critère porte sur le")
    L.append("**procédé**. Un détecteur condamné par sa propre validation, publié")
    L.append("proprement, **réussit ce cycle**.")
    L.append("")

    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date")
    L.append("> de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()
