"""Résolution par horodatage des candidats « du jour même » (#433).

Spécification pré-enregistrée dans `PREREG_sameday_timestamp_resolution.md`,
committée avant toute mesure.

Le #431 classait par **date** et laissait 17 candidats ambigus. Git conserve
l'horodatage à la **seconde** : la comparaison exacte tranche.

Règle FIXÉE AVANT EXÉCUTION :
- horodatage strictement antérieur à l'ajout de la batterie ⇒ antériorité ;
- strictement postérieur ⇒ dette réelle ;
- exactement égal ⇒ compté à part, jamais rangé arbitrairement.
"""
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
REPO = ROOT.parent.parent
OUT = RESULTS / "nonml_sameday_timestamp_resolution_result.md"

BATTERY = "finance/trading/scripts/nonml_pass_validation_battery.py"


def added_at(path_rel: str):
    """Horodatage (epoch) du commit d'AJOUT du fichier, ou None."""
    r = subprocess.run(
        ["git", "log", "--reverse", "--format=%ct", "--diff-filter=A", "--", path_rel],
        cwd=str(REPO), capture_output=True, text=True, timeout=120)
    out = r.stdout.strip().split("\n")
    return int(out[0]) if out and out[0].isdigit() else None


def verdict_of(p: Path) -> str:
    t = p.read_text(encoding="utf-8")
    if "**PASS" in t or "PASS (niveau 1)" in t:
        return "PASS"
    if "**FAIL" in t:
        return "FAIL"
    return "indéterminé"


def schema_of(name: str):
    p = RESULTS / f"nonml_{name}_pnl.npz"
    if not p.exists():
        return "aucun .npz"
    d = np.load(p, allow_pickle=True)
    f = set(d.files)
    if {"pos", "r_asset", "dates", "cost_bps"} <= f:
        return "indiciel"
    if {"pnl_gross_ov", "pnl_gross_bh"} <= f:
        return "panier"
    return "autre"


def sameday_candidates(rule_ts: int):
    """Recalcule la liste des PASS sans batterie tombant le JOUR de la règle."""
    import datetime as dt
    rule_day = dt.datetime.utcfromtimestamp(rule_ts).strftime("%Y-%m-%d")
    out = []
    for p in sorted(RESULTS.glob("nonml_*_result.md")):
        name = p.name.replace("nonml_", "").replace("_result.md", "")
        if verdict_of(p) != "PASS":
            continue
        if (RESULTS / f"nonml_{name}_pass_validation_battery.md").exists():
            continue
        txt = p.read_text(encoding="utf-8").lower()
        if "batterie" in txt or "validation" in txt:
            continue
        ts = added_at(f"finance/trading/results/nonml_{name}_result.md")
        if ts is None:
            continue
        day = dt.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")
        if day == rule_day:
            out.append((name, ts))
    return out, rule_day


def main():
    rule_ts = added_at(BATTERY)
    if rule_ts is None:
        raise SystemExit("Horodatage d'ajout de la batterie introuvable — arrêt.")

    cands, rule_day = sameday_candidates(rule_ts)
    import datetime as dt
    rule_str = dt.datetime.utcfromtimestamp(rule_ts).strftime("%Y-%m-%d %H:%M:%S UTC")

    before, after, equal = [], [], []
    for name, ts in cands:
        if ts < rule_ts:
            before.append((name, ts))
        elif ts > rule_ts:
            after.append((name, ts))
        else:
            equal.append((name, ts))

    def hh(ts):
        return dt.datetime.utcfromtimestamp(ts).strftime("%H:%M:%S")

    L = ["# Résolution par horodatage des candidats « du jour même » (pré-enregistré)", ""]
    L.append("Cycle d'**infrastructure de protocole**. Aucune stratégie nouvelle, aucun")
    L.append("paramètre touché, **aucun verdict de niveau 1 modifié**.")
    L.append("")
    L.append(f"La batterie `nonml_pass_validation_battery.py` a été ajoutée au dépôt le")
    L.append(f"**{rule_str}**. Le #431 comparait des **dates** ; ce cycle compare des")
    L.append("**horodatages à la seconde**, ce qui tranche exactement.")
    L.append("")

    L.append("## Classification des candidats du jour même")
    L.append("")
    L.append(f"- candidats tombant le **{rule_day}** : **{len(cands)}**")
    L.append("")
    L.append("| Catégorie | Nombre |")
    L.append("|---|---|")
    L.append(f"| horodatage **antérieur** ⇒ antériorité, blanchi | **{len(before)}** |")
    L.append(f"| horodatage **postérieur** ⇒ dette réelle | **{len(after)}** |")
    L.append(f"| horodatage **exactement égal** ⇒ indécidable | **{len(equal)}** |")
    L.append("")

    if before:
        L.append("### Blanchis — publiés avant l'existence de la règle")
        L.append("")
        L.append("| Candidat | Rapport ajouté à | Écart avant la règle |")
        L.append("|---|---|---|")
        for n, ts in sorted(before, key=lambda t: t[1]):
            d = rule_ts - ts
            L.append(f"| `{n}` | {hh(ts)} | −{d // 3600} h {(d % 3600) // 60} min |")
        L.append("")

    if after:
        L.append("### Dette réelle — publiés après l'existence de la règle")
        L.append("")
        L.append("| Candidat | Rapport ajouté à | Écart après la règle | Schéma |")
        L.append("|---|---|---|---|")
        for n, ts in sorted(after, key=lambda t: t[1]):
            d = ts - rule_ts
            L.append(f"| `{n}` | {hh(ts)} | +{d // 3600} h {(d % 3600) // 60} min | "
                     f"{schema_of(n)} |")
        L.append("")

    if equal:
        L.append("### Indécidables — horodatage identique à la seconde")
        L.append("")
        for n, _ in equal:
            L.append(f"- `{n}`")
        L.append("")

    L.append("## Lecture")
    L.append("")
    L.append("Le #431 avait compté ces candidats à part plutôt que de les ranger « du côté qui")
    L.append("m'arrange » — c'était le bon réflexe. Mais le #432 concluait « non tranchable par")
    L.append("la date seule » et **s'arrêtait là**, alors que l'horodatage était disponible.")
    L.append("La formule était vraie au mot près et la conclusion prématurée.")
    L.append("")
    if not after:
        L.append("**Aucun des candidats du jour même n'est en dette.** Tous ont été publiés")
        L.append("avant l'ajout de la batterie : ils relèvent de l'antériorité, comme les 10")
        L.append("déjà classés ainsi au #431. La dette de la Règle 9 reste celle du #432,")
        L.append("désormais soldée.")
    else:
        L.append(f"**{len(after)} candidat(s) rejoignent la dette réelle.** Ils sont soumis à la")
        L.append("batterie dans ce même cycle, comme le pré-enregistrement l'annonçait avant")
        L.append("que leurs noms soient connus.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")
    return before, after, equal


if __name__ == "__main__":
    main()
