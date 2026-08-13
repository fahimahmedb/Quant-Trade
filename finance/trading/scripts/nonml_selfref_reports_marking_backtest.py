"""Signaler les rapports dépendants du dépôt (#439).

Spécification pré-enregistrée dans `PREREG_selfref_reports_marking.md`,
committée avant toute modification.

Ce cycle **ne stabilise pas** ces rapports : un diagnostic qui décrit l'état du
dépôt doit changer quand le dépôt change. Il les **signale**, pour qu'un lecteur
ne prenne pas cette dérive pour une péremption de résultat.

Le déclencheur est le **test comportemental** du #438 — pas un motif de code,
dont le #437 a montré qu'il ratait des cas.

Régime : **insertions seulement**, repris tel quel du #428.
"""
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
OUT = RESULTS / "nonml_selfref_reports_marking_result.md"

# Texte FIXE au pre-enregistrement, non ajustable apres coup.
MARKER_KEY = "**Rapport dépendant du dépôt**"
MARKER = (
    "\n> **Rapport dépendant du dépôt** — ce document décrit l'état du dépôt à la date\n"
    "> de son exécution. Il change à chaque cycle qui ajoute un fichier : c'est voulu,\n"
    "> et ce n'est pas une péremption de résultat (cycles #436-#438).\n"
)

SENTINELS = [
    RESULTS / "nonml__sentinelle_tmp_result.md",
    SCRIPTS / "nonml__sentinelle_tmp_backtest.py",
    RESULTS / "nonml__sentinelle_tmp_pnl.npz",
]

SYNTACTIC = re.compile(
    r'(RESULTS|SCRIPTS)\.glob\(|ROOT\s*/\s*"(results|scripts)"[^\n]*\.glob\(')
TIMEOUT_S = 300


def place_sentinels():
    SENTINELS[0].write_text("# sentinelle temporaire (#439)\n", encoding="utf-8")
    SENTINELS[1].write_text('"""Sentinelle temporaire (#439)."""\n', encoding="utf-8")
    np.savez(SENTINELS[2], pos=np.ones(3), r_asset=np.zeros(3),
             dates=np.arange(3), cost_bps=5.0)


def remove_sentinels():
    for p in SENTINELS:
        try:
            p.unlink(missing_ok=True)
        except Exception:  # noqa: BLE001
            pass


def run(name):
    """Execute un candidat en groupe de processus isole.

    Au premier essai du #439, `subprocess.run(timeout=...)` ne tuait que
    l'enfant direct : les petits-enfants (les backtests relances par un script
    de campagne) survivaient et REECRIVAIENT des rapports apres la
    restauration. On isole donc le groupe et on le tue entier.
    """
    proc = subprocess.Popen(
        [sys.executable, str(SCRIPTS / f"nonml_{name}_backtest.py")],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        start_new_session=True)
    try:
        out, err = proc.communicate(timeout=TIMEOUT_S)
        return subprocess.CompletedProcess(proc.args, proc.returncode, out, err)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except Exception:  # noqa: BLE001
            proc.kill()
        proc.wait(timeout=30)
        raise


def candidates():
    out, interferes = [], []
    for s in sorted(SCRIPTS.glob("nonml_*_backtest.py")):
        n = s.name.replace("nonml_", "").replace("_backtest.py", "")
        if "_sentinelle_tmp" in n or n == "selfref_reports_marking":
            continue
        # EXCLUSION DE CORRECTION (#439) : un candidat qui manipule lui-meme des
        # fichiers portant les MEMES noms de sentinelles supprime les miennes
        # dans son propre `finally`, ce qui vide le test de son sens. La raison
        # est mecanique et connaissable sans voir aucun resultat -- elle se lit
        # dans le code du candidat, pas dans son verdict.
        if "nonml__sentinelle_tmp" in s.read_text(encoding="utf-8"):
            interferes.append(n)
            continue
        if not (RESULTS / f"nonml_{n}_result.md").exists():
            continue
        if SYNTACTIC.search(s.read_text(encoding="utf-8")):
            out.append(n)
    return out, interferes


def depends_on_repo(name, tmp):
    """Test comportemental : le rapport bouge-t-il si le dépôt gagne des fichiers ?"""
    rep = RESULTS / f"nonml_{name}_result.md"
    published = tmp / f"{name}_published.md"
    shutil.copy2(rep, published)
    verdict, why = "indéterminé", ""
    try:
        r = run(name)
        if r.returncode != 0:
            return "indéterminé", f"le script échoue (code {r.returncode})", published
        base = tmp / f"{name}_base.md"
        shutil.copy2(rep, base)
        place_sentinels()
        r2 = run(name)
        if r2.returncode != 0:
            verdict, why = "indéterminé", "le script échoue en présence des sentinelles"
        elif rep.read_bytes() != base.read_bytes():
            verdict, why = "CONFIRMÉ", "le rapport change quand le dépôt gagne des fichiers neutres"
        else:
            verdict, why = "INFIRMÉ", "le rapport ne dépend pas du contenu du dépôt"
    except subprocess.TimeoutExpired:
        verdict, why = "indéterminé", f"délai > {TIMEOUT_S} s"
    finally:
        remove_sentinels()
        shutil.copy2(published, rep)   # rapport PUBLIE restaure
    return verdict, why, published


def main():
    cands, interferes = candidates()
    tmp = Path(tempfile.mkdtemp(prefix="selfref_"))
    confirmed, refuted, undetermined = [], [], []

    try:
        for n in cands:
            v, why, _ = depends_on_repo(n, tmp)
            (confirmed if v == "CONFIRMÉ" else
             refuted if v == "INFIRMÉ" else undetermined).append((n, why))
    finally:
        remove_sentinels()

    # --- Marquage : insertions seulement ---------------------------------
    marked, already = [], []
    for n, _ in confirmed:
        rep = RESULTS / f"nonml_{n}_result.md"
        txt = rep.read_text(encoding="utf-8")
        if MARKER_KEY in txt:
            already.append(n)
            continue
        rep.write_text(txt.rstrip("\n") + "\n" + MARKER, encoding="utf-8")
        marked.append(n)

    L = ["# Rapports dépendants du dépôt — signalés, non appauvris (pré-enregistré)", ""]
    L.append("Cycle de **modification déclarée**, régime des #428-#430. Aucune stratégie")
    L.append("évaluée, aucun verdict recalculé, aucun paramètre de stratégie touché.")
    L.append("")
    L.append("## Pourquoi signaler plutôt que stabiliser")
    L.append("")
    L.append("Le #438 avait inscrit « rendre stables » ces rapports, en invoquant un")
    L.append("dénominateur de borne amputé. **Le calcul ne le justifie pas** :")
    L.append("")
    n_pool = len([s for s in SCRIPTS.glob("nonml_*_backtest.py")
                  if (RESULTS / f"nonml_{s.name.replace('nonml_', '').replace('_backtest.py', '')}_result.md").exists()])
    L.append(f"- candidats dépendants du dépôt : **{len(cands)}**")
    L.append(f"- vivier : **{n_pool}** → **{100*len(cands)/n_pool:.1f} %**")
    L.append(f"- perte moyenne sur un tirage de 24 : **{24*len(cands)/n_pool:.1f}** tirage")
    L.append("")
    L.append("« Rendre stable » signifierait **supprimer** de ces rapports les décomptes du")
    L.append("dépôt — exactement l'information que le #428 y avait ajoutée à dessein pour")
    L.append("empêcher un lecteur de surestimer la portée du balayage. J'appauvrirais un")
    L.append("diagnostic pour récupérer moins d'un tirage sur vingt-quatre.")
    L.append("")
    L.append("**Un diagnostic qui décrit l'état du dépôt doit changer quand le dépôt change.**")
    L.append("Sa divergence est son fonctionnement ; le défaut serait qu'un lecteur la prenne")
    L.append("pour une péremption. D'où un marqueur, et non une amputation.")
    L.append("")

    L.append("## Deux défauts de ce cycle, rencontrés en l'exécutant")
    L.append("")
    L.append("### 1. Interférence de sentinelles")
    L.append("")
    L.append("Une première exécution a dû être **interrompue**. Un candidat manipule lui-même")
    L.append("des fichiers portant **les mêmes noms de sentinelles** : lancé comme candidat, il")
    L.append("supprimait les miennes dans son propre `finally`, **vidant le test de son sens**.")
    L.append("")
    L.append(f"- candidats **écartés pour interférence** : **{len(interferes)}**")
    L.append("")
    for n in sorted(interferes):
        L.append(f"- `{n}`")
    L.append("")
    L.append("La raison est **mécanique et connaissable sans voir aucun résultat** — elle se lit")
    L.append("dans le code du candidat, pas dans son verdict.")
    L.append("")
    L.append("### 2. Processus orphelins survivant au délai")
    L.append("")
    L.append("Plus grave, et découvert en inspectant l'arbre après coup : `subprocess.run`")
    L.append("avec `timeout` ne tuait que l'**enfant direct**. Les candidats qui relancent")
    L.append("eux-mêmes des backtests laissaient des **petits-enfants orphelins** qui ont")
    L.append("continué de tourner et **réécrit un rapport après sa restauration** —")
    L.append("`nonml_reproducibility_sample_result.md` a été retrouvé modifié alors qu'il")
    L.append("n'était pas marqué.")
    L.append("")
    L.append("Les orphelins ont été tués et le rapport restauré. Le script exécute désormais")
    L.append("chaque candidat dans un **groupe de processus isolé**, tué entier au délai.")
    L.append("**La garantie « aucun rapport publié modifié » ne tenait pas à ce moment-là**, et")
    L.append("je l'écris plutôt que de la présenter comme acquise depuis le début.")
    L.append("")
    L.append("## Test comportemental — ce qui déclenche le marquage")
    L.append("")
    L.append("Le #437 a échoué en identifiant ces scripts par la **forme de leur code**. Ici")
    L.append("chaque candidat est **testé** : exécution, sauvegarde, ajout de fichiers")
    L.append("sentinelles neutres, ré-exécution, comparaison.")
    L.append("")
    L.append("| | Nombre |")
    L.append("|---|---|")
    L.append(f"| candidats repérés par la syntaxe | **{len(cands)}** |")
    L.append(f"| **confirmés** par le test | **{len(confirmed)}** |")
    L.append(f"| **infirmés** (faux positifs syntaxiques) | **{len(refuted)}** |")
    L.append(f"| indéterminés | **{len(undetermined)}** |")
    L.append("")
    if refuted:
        L.append("### Infirmés — repérés par la syntaxe, mais le test les disculpe")
        L.append("")
        L.append("| Script | Raison |")
        L.append("|---|---|")
        for n, why in sorted(refuted):
            L.append(f"| `{n}` | {why} |")
        L.append("")
        L.append("**Ils ne sont pas marqués.** Le test prime sur la syntaxe, comme le")
        L.append("pré-enregistrement l'exigeait.")
        L.append("")
    if undetermined:
        L.append("### Indéterminés")
        L.append("")
        L.append("| Script | Raison |")
        L.append("|---|---|")
        for n, why in sorted(undetermined):
            L.append(f"| `{n}` | {why} |")
        L.append("")
        L.append("Non marqués : le doute ne suffit pas à justifier une modification.")
        L.append("")

    L.append("## Marquage")
    L.append("")
    L.append(f"- rapports **marqués** par ce cycle : **{len(marked)}**")
    L.append(f"- déjà porteurs du marqueur : **{len(already)}**")
    L.append("")
    if marked:
        L.append("| Rapport marqué |")
        L.append("|---|")
        for n in sorted(marked):
            L.append(f"| `{n}` |")
        L.append("")
    L.append("Texte ajouté, **fixé au pré-enregistrement** :")
    L.append("")
    L.append("```")
    for line in MARKER.strip("\n").splitlines():
        L.append(line)
    L.append("```")
    L.append("")

    L.append("## Contrôle des sentinelles")
    L.append("")
    left = [p.name for p in SENTINELS if p.exists()]
    L.append(f"- sentinelles subsistantes : **{len(left)}** "
             f"{'✔' if not left else '✘ — CYCLE EN ÉCHEC'}")
    L.append("")

    shutil.rmtree(tmp, ignore_errors=True)
    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
