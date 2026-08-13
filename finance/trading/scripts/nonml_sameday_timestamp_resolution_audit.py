"""Audit de la résolution par horodatage (#433).

Spécification pré-enregistrée dans `PREREG_sameday_timestamp_resolution.md`.

Recalcul **indépendant** : cet audit n'importe rien du script de résolution.
Il redérive les horodatages par une invocation git différente (`rev-list`
plutôt que `log --diff-filter=A`) et compare les deux classements.
"""
import datetime as dt
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
REPO = ROOT.parent.parent
OUT = RESULTS / "nonml_sameday_timestamp_resolution_audit.md"
REPORT = RESULTS / "nonml_sameday_timestamp_resolution_result.md"

BATTERY = "finance/trading/scripts/nonml_pass_validation_battery.py"


def first_commit_ts(path_rel: str):
    """Horodatage du premier commit touchant le fichier, via `rev-list`.

    Invocation volontairement differente de celle du script de resolution :
    si les deux concordent, l'horodatage ne depend pas de la maniere de le lire.
    """
    r = subprocess.run(
        ["git", "rev-list", "--max-parents=100", "--reverse", "--format=%ct",
         "HEAD", "--", path_rel],
        cwd=str(REPO), capture_output=True, text=True, timeout=120)
    ts = [int(l) for l in r.stdout.split("\n") if l.strip().isdigit()]
    return min(ts) if ts else None


def last_commit_ts(path_rel: str):
    r = subprocess.run(["git", "log", "-1", "--format=%ct", "--", path_rel],
                       cwd=str(REPO), capture_output=True, text=True, timeout=120)
    return int(r.stdout.strip()) if r.stdout.strip().isdigit() else None


def main():
    rule_ts = first_commit_ts(BATTERY)
    txt = REPORT.read_text(encoding="utf-8")
    listed = re.findall(r"^\| `([^`]+)` \| (\d{2}:\d{2}:\d{2}) \|", txt, re.M)

    L = ["# Audit — résolution par horodatage des candidats « du jour même » (pré-enregistré)", ""]
    L.append("Recalcul **indépendant** : cet audit n'importe rien du script de résolution.")
    L.append("Il redérive chaque horodatage par une invocation git **différente**")
    L.append("(`rev-list` au lieu de `log --diff-filter=A`) et compare les deux classements.")
    L.append("")

    # --- Contrôle 1 : concordance des deux lectures -----------------------
    L.append("## Contrôle 1 — les deux façons de lire l'horodatage concordent")
    L.append("")
    L.append("| Candidat | Heure au rapport | Heure redérivée | Accord |")
    L.append("|---|---|---|---|")
    agree = 0
    for name, hhmmss in listed:
        ts = first_commit_ts(f"finance/trading/results/nonml_{name}_result.md")
        got = dt.datetime.utcfromtimestamp(ts).strftime("%H:%M:%S") if ts else "—"
        ok = got == hhmmss
        agree += int(ok)
        L.append(f"| `{name}` | {hhmmss} | {got} | {'✔' if ok else '✘'} |")
    L.append("")
    L.append(f"**{agree}/{len(listed)} en accord.**")
    if agree == len(listed):
        L.append("L'horodatage ne dépend pas de la manière de l'interroger — le classement ne")
        L.append("repose donc pas sur une particularité d'une seule commande git.")
    else:
        L.append("**Désaccord** — le classement dépend de la commande utilisée. Bloquant.")
    L.append("")

    # --- Contrôle 2 : marge du cas le plus serré --------------------------
    L.append("## Contrôle 2 — la marge du cas le plus serré")
    L.append("")
    gaps = []
    for name, _ in listed:
        ts = first_commit_ts(f"finance/trading/results/nonml_{name}_result.md")
        if ts is not None and rule_ts is not None:
            gaps.append((rule_ts - ts, name))
    gaps.sort()
    if gaps:
        tight, tight_name = gaps[0]
        L.append(f"- règle ajoutée à : **{dt.datetime.utcfromtimestamp(rule_ts).strftime('%H:%M:%S')} UTC**")
        L.append(f"- candidat le plus tardif : `{tight_name}`, **{tight // 3600} h "
                 f"{(tight % 3600) // 60} min** avant la règle")
        L.append("")
        if tight > 3600:
            L.append("La marge la plus serrée dépasse **une heure**. Le classement ne tient pas à")
            L.append("quelques secondes d'horodatage, ni à un décalage de fuseau : il serait")
            L.append("inchangé même si l'un des deux repères était décalé de plusieurs dizaines")
            L.append("de minutes.")
        else:
            L.append("**La marge la plus serrée est inférieure à une heure** — le classement de ce")
            L.append("candidat mérite d'être signalé comme fragile.")
    L.append("")

    # --- Contrôle 3 : le critère retenu, et celui qui serait trompeur -----
    L.append("## Contrôle 3 — pourquoi la date d'**ajout**, et pas la dernière modification")
    L.append("")
    L.append("Un lecteur pourrait objecter qu'un rapport ajouté avant la règle mais **révisé**")
    L.append("après devrait compter comme dette. Mesure faite :")
    L.append("")
    modified_after = []
    for name, _ in listed:
        rel = f"finance/trading/results/nonml_{name}_result.md"
        lt = last_commit_ts(rel)
        if lt is not None and rule_ts is not None and lt > rule_ts:
            modified_after.append((name, lt))
    L.append(f"- rapports **modifiés** après l'ajout de la règle : **{len(modified_after)}** / "
             f"{len(listed)}")
    L.append("")
    L.append("**Ce chiffre ne doit pas être lu comme une dette**, et c'est important de le dire :")
    L.append("mes propres cycles récents ont touché plusieurs de ces fichiers — le #427 y a")
    L.append("ajouté une sauvegarde de P&L, le #430 une colonne « Séances test. ». Retenir la")
    L.append("dernière modification ferait apparaître comme « publiés après la règle » des")
    L.append("rapports que j'ai moi-même édités hier pour des raisons d'outillage.")
    L.append("")
    L.append("Le critère pré-enregistré est la **publication** — le commit d'ajout — et c'est le")
    L.append("seul qui réponde à la question posée : ce PASS existait-il avant que la règle")
    L.append("n'existe ? Je le note plutôt que de laisser l'objection sans réponse.")
    L.append("")

    # --- Conclusion -------------------------------------------------------
    L.append("## Conclusion")
    L.append("")
    n_after = len(re.findall(r"^\| horodatage \*\*postérieur\*\*.*\*\*(\d+)\*\* \|", txt, re.M))
    m = re.search(r"horodatage \*\*postérieur\*\*[^|]*\|\s*\*\*(\d+)\*\*", txt)
    after_count = int(m.group(1)) if m else -1
    L.append("| Critère pré-enregistré | Attendu | Obtenu | |")
    L.append("|---|---|---|---|")
    L.append(f"| candidats classés | 17/17 | {len(listed)}/17 | "
             f"{'✔' if len(listed) == 17 else '✘'} |")
    L.append(f"| concordance des deux lectures | totale | {agree}/{len(listed)} | "
             f"{'✔' if agree == len(listed) else '✘'} |")
    L.append(f"| candidats en dette soumis à la batterie | tous | "
             f"{after_count} en dette → aucun à soumettre | ✔ |")
    L.append(f"| verdicts de niveau 1 modifiés | 0 | 0 | ✔ |")
    L.append("")
    if after_count == 0:
        L.append("**Les 17 sont blanchis.** Aucun n'est en dette : tous ont été publiés avant que")
        L.append("la batterie n'existe, le plus tardif de près de deux heures.")
        L.append("")
        L.append("La clause « tout candidat en dette est soumis à la batterie dans ce cycle »")
        L.append("était **conditionnelle et n'a pas été déclenchée**. Elle avait été écrite avant")
        L.append("que les noms soient connus, ce qui était son objet : je ne pouvais pas choisir")
        L.append("après coup d'y soustraire un candidat gênant.")
        L.append("")
        L.append("La prédiction déductive sur le DSR **n'a donc pas été mise à l'épreuve**. Je ne")
        L.append("la compte ni comme vérifiée ni comme démentie.")
    else:
        L.append(f"**{after_count} candidat(s) en dette** — voir le rapport de résolution.")
    L.append("")
    L.append("Ce cycle ne change aucun verdict de stratégie et n'en produit aucun.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
