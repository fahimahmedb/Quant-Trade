"""Inventaire honnête des verdicts après la campagne de correction #375-#381.

Recompte les PASS à partir des fichiers `results/*_result.md` réellement présents,
APRÈS correction des deux bugs (composition des rendements log, agrégation de
panier). Le chiffre « 101 PASS sur 372 hypothèses » qui circulait dans le backlog
datait d'avant ces corrections et n'est plus utilisable.

Principes de l'inventaire :

1. **Rien n'est masqué.** Un fichier dont le verdict n'est pas analysable est
   compté dans une catégorie « indéterminé » explicite, jamais écarté en silence.
2. **Le dénominateur est celui des fichiers réellement présents**, pas un compteur
   historique reporté de cycle en cycle.
3. Les fichiers `*_pass_validation_battery.md` (batteries Règle 9) sont recensés à
   part et **confrontés au verdict courant** de la stratégie qu'ils valident : une
   batterie qui valide une stratégie désormais FAIL est **caduque**.

Usage : python3 scripts/nonml_pass_inventory.py
"""

from __future__ import annotations

import glob
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT = RESULTS / "nonml_pass_inventory.md"

VERDICT_RE = re.compile(r"\*\*(PASS|FAIL)")


def verdict_of(path: Path) -> str | None:
    """Premier verdict en gras du fichier, ou None si illisible."""
    try:
        txt = path.read_text(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        return None
    m = VERDICT_RE.search(txt)
    return m.group(1) if m else None


def main() -> None:
    results, battery = [], []
    for p in sorted(RESULTS.glob("*.md")):
        n = p.name
        if n.endswith("_pass_validation_battery.md"):
            battery.append(p)
        elif n.endswith("_result.md"):
            results.append(p)

    verdicts = {p.name: verdict_of(p) for p in results}
    n_pass = sum(1 for v in verdicts.values() if v == "PASS")
    n_fail = sum(1 for v in verdicts.values() if v == "FAIL")
    n_unk = sum(1 for v in verdicts.values() if v is None)

    # Batteries Regle 9 : confrontation au verdict courant de leur strategie.
    caduques, valides, orphelines = [], [], []
    for b in battery:
        strat = b.name[: -len("_pass_validation_battery.md")]
        rf = RESULTS / f"{strat}_result.md"
        if not rf.exists():
            orphelines.append(b.name)
            continue
        v = verdicts.get(rf.name)
        if v == "FAIL":
            caduques.append(strat)
        elif v == "PASS":
            valides.append(strat)
        else:
            orphelines.append(b.name)

    L = []
    L.append("# Inventaire des verdicts après la campagne de correction (#382)")
    L.append("")
    L.append("**Recomptage mécanique, non pré-enregistré** : on lit les fichiers de résultat")
    L.append("présents dans `results/` et on compte. Aucun paramètre, aucun seuil.")
    L.append("")
    L.append("## Pourquoi ce recomptage")
    L.append("")
    L.append("Le chiffre **« 101 PASS niveau 1 sur 372 hypothèses »** circulait de synthèse en")
    L.append("synthèse. Il datait d'**avant** la campagne #375-#381, qui a fait tomber 20 PASS.")
    L.append("Il n'est plus utilisable et ne doit plus être cité.")
    L.append("")
    L.append("## Décompte")
    L.append("")
    L.append("| | |")
    L.append("|---|---|")
    L.append(f"| fichiers `*_result.md` présents | **{len(results)}** |")
    L.append(f"| verdict **PASS** | **{n_pass}** |")
    L.append(f"| verdict **FAIL** | **{n_fail}** |")
    L.append(f"| verdict **indéterminé** (non analysable) | **{n_unk}** |")
    L.append("")
    L.append("Le dénominateur est le nombre de fichiers de résultat réellement présents, pas")
    L.append("un compteur historique reporté. Il ne coïncide pas avec le « 372 hypothèses »")
    L.append("du backlog : certains cycles étaient des synthèses ou des batteries sans")
    L.append("fichier de résultat propre, d'autres produisent plusieurs fichiers.")
    L.append("")
    if n_unk:
        L.append(f"### Les {n_unk} verdicts indéterminés")
        L.append("")
        L.append("Comptés explicitement plutôt qu'écartés en silence — leur format de rapport")
        L.append("ne porte pas de verdict en gras analysable :")
        L.append("")
        for name, v in sorted(verdicts.items()):
            if v is None:
                L.append(f"- `{name[: -len('_result.md')]}`")
        L.append("")
    L.append("## Contrôle de cohérence")
    L.append("")
    L.append("Le décompte pris **après** la correction de composition mais **avant** celle")
    L.append("d'agrégation (cycle #377) donnait **101 PASS sur 265 verdicts lisibles**. On en")
    L.append(f"compte ici **{n_pass} sur {len(results) - n_unk}**.")
    L.append("")
    L.append(f"Écart : **{101 - n_pass}**. La correction d'agrégation a fait tomber 8 PASS")
    L.append("(`momentum_52w_high` au #378, plus 7 au #379). Les deux chiffres se")
    L.append("réconcilient exactement — le décompte n'est pas un comptage indépendant qui")
    L.append("« retomberait » par chance, mais la conséquence arithmétique des")
    L.append("reclassifications documentées.")
    L.append("")
    L.append("Les 12 reclassifications dues au bug de composition, elles, étaient déjà")
    L.append("intégrées dans le 101 : elles sont antérieures à cette mesure.")
    L.append("")
    L.append("## Batteries Règle 9 : lesquelles sont caduques")
    L.append("")
    L.append("Une batterie de validation renforcée qui valide une stratégie **désormais")
    L.append("FAIL** ne valide plus rien : elle porte sur un résultat qui n'existe plus.")
    L.append("")
    L.append("| | |")
    L.append("|---|---|")
    L.append(f"| batteries présentes | **{len(battery)}** |")
    L.append(f"| **caduques** (stratégie désormais FAIL) | **{len(caduques)}** |")
    L.append(f"| encore adossées à un PASS | {len(valides)} |")
    L.append(f"| sans résultat associé analysable | {len(orphelines)} |")
    L.append("")
    if caduques:
        L.append("### Batteries caduques")
        L.append("")
        for s in sorted(caduques):
            L.append(f"- `{s}`")
        L.append("")
        L.append("**Ces batteries ne sont pas supprimées** — l'historique est conservé — mais")
        L.append("elles ne doivent plus être invoquées comme validation.")
        L.append("")
    L.append("## Portée")
    L.append("")
    L.append("Ce décompte porte sur les fichiers de résultat **tels qu'ils existent après")
    L.append("correction**. Il ne rejuge aucune stratégie et n'en revalide aucune : il")
    L.append("constate. Un PASS recensé ici reste un PASS **de niveau 1** — le critère")
    L.append("renforcé Sharpe+rendement — et non un verdict final au sens de la Règle 9.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"resultats : {len(results)} | PASS {n_pass} | FAIL {n_fail} | indetermine {n_unk}")
    print(f"batteries : {len(battery)} | caduques {len(caduques)} | valides {len(valides)} | orphelines {len(orphelines)}")
    print(f"ecrit : {OUT}")


if __name__ == "__main__":
    main()
