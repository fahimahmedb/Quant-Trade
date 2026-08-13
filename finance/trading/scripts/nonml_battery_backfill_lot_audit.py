"""Audit du lot de rattrapage de batterie (#432).

Spécification pré-enregistrée dans `PREREG_battery_backfill_lot.md`, committée
avant toute exécution.

Cet audit **relit** les rapports de batterie produits et vérifie qu'ils
répondent au critère pré-enregistré. Il ne rejoue aucun contrôle : la batterie
est l'outil de référence, le rôle de l'audit est de constater et de qualifier.
"""
import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT = RESULTS / "nonml_battery_backfill_lot_audit.md"

EXECUTED = [
    "gjr_vol_managed_russell2000",
    "gjr_vol_managed_sp500",
    "deep_drawdown_breadth_vol_targeting_overlay_pit_universe",
    "weakness_breadth_vol_targeting_overlay_pit_universe",
]
SET_ASIDE = {
    "january_effect_lowprice_overlay_pit_universe":
        "schéma **panier** — la batterie exige le schéma indiciel "
        "(`pos`, `r_asset`, `dates`, `cost_bps`). Lui fabriquer une position "
        "scalaire serait inventer une donnée.",
    "capitulation_gate_floor_sweep":
        "**diagnostic, pas une stratégie** — faux positif de détection écarté "
        "d'office par le pré-enregistrement (établi au #427).",
}
CONTROLS = ["Stress coûts", "Stress crise", "Stabilité temporelle",
            "SPA 1-candidat", "DSR (n_trials=backlog)"]


def read_battery(name: str):
    p = RESULTS / f"nonml_{name}_pass_validation_battery.md"
    if not p.exists():
        return None
    t = p.read_text(encoding="utf-8")
    res = {}
    for c in CONTROLS:
        m = re.search(rf"{re.escape(c)}\s*:\s*(OK|ÉCHEC)", t)
        res[c] = m.group(1) if m else "?"
    dsr = re.search(r"DSR\s*=\s*([0-9.]+)", t)
    nt = re.search(r"n_trials\s*=\s*(\d+)", t)
    return res, (float(dsr.group(1)) if dsr else None), (int(nt.group(1)) if nt else None)


def main():
    L = ["# Audit — rattrapage de batterie sur les PASS postérieurs à la Règle 9 (pré-enregistré)", ""]
    L.append("Cycle d'**infrastructure de protocole**. Aucune stratégie nouvelle, aucun")
    L.append("paramètre touché, **aucun verdict de niveau 1 modifié**.")
    L.append("")
    L.append("Cet audit relit les rapports produits par la batterie ; il ne rejoue aucun")
    L.append("contrôle. La batterie est l'outil de référence, l'audit constate et qualifie.")
    L.append("")

    # --- Périmètre --------------------------------------------------------
    L.append("## Périmètre — 4 exécutés, 2 écartés avec leur raison")
    L.append("")
    for n, why in SET_ASIDE.items():
        L.append(f"- `{n}` — {why}")
    L.append("")

    # --- Résultats --------------------------------------------------------
    L.append("## Résultats — les cinq contrôles, candidat par candidat")
    L.append("")
    L.append("| Candidat | a. Coûts | b. Crise | c. Stabilité | d. SPA | e. DSR | Verdict |")
    L.append("|---|---|---|---|---|---|---|")
    rows, n_pass = [], 0
    for n in EXECUTED:
        got = read_battery(n)
        if got is None:
            L.append(f"| `{n}` | — | — | — | — | — | **rapport absent** |")
            continue
        res, dsr, nt = got
        ok_all = all(v == "OK" for v in res.values())
        n_pass += int(ok_all)
        rows.append((n, res, dsr, nt))
        cells = " | ".join(res[c] for c in CONTROLS)
        L.append(f"| `{n}` | {cells} | {'**RENFORCÉ**' if ok_all else 'non validé'} |")
    L.append("")
    L.append(f"**{n_pass}/{len(rows)} candidat(s) obtiennent le PASS RENFORCÉ.**")
    L.append("")

    # --- La prédiction ----------------------------------------------------
    L.append("## La prédiction pré-enregistrée")
    L.append("")
    L.append("> « Attente : **0 des 4** candidats ne passe les 5 contrôles, l'échec venant au")
    L.append("> minimum du **DSR**. »")
    L.append("")
    dsr_fail = [n for n, res, _, _ in rows if res["DSR (n_trials=backlog)"] == "ÉCHEC"]
    nt = rows[0][3] if rows else None
    if n_pass == 0 and len(dsr_fail) == len(rows):
        L.append(f"**Vérifiée sur les deux points** : {n_pass}/{len(rows)} PASS RENFORCÉ, et le DSR")
        L.append(f"échoue pour **{len(dsr_fail)}/{len(rows)}**.")
    else:
        L.append(f"**Partiellement démentie** : {n_pass} PASS RENFORCÉ, DSR en échec pour")
        L.append(f"{len(dsr_fail)}/{len(rows)}. À instruire avant toute autre conclusion.")
    L.append("")
    L.append("| Candidat | DSR obtenu | Seuil |")
    L.append("|---|---|---|")
    for n, res, dsr, _ in rows:
        L.append(f"| `{n}` | {dsr if dsr is not None else '—'} | 0,95 |")
    L.append("")
    L.append(f"`n_trials = {nt}` pour les quatre. Les #111 et #112 avaient déjà mesuré qu'à")
    L.append("`n_trials = 110`, **aucune hypothèse individuelle du backlog n'avait de chance")
    L.append("réaliste** de franchir le seuil. À 370, le constat ne pouvait que se répéter.")
    L.append("")
    L.append("**Cette prédiction n'a donc aucun mérite** : elle découle d'un résultat déjà")
    L.append("mesuré il y a plus de trois cents cycles, pas d'une intuition. Je l'écris ainsi")
    L.append("plutôt que de la compter comme un succès de plus.")
    L.append("")

    # --- Le cas du PASS vide ----------------------------------------------
    L.append("## Le candidat inactif — pourquoi ses trois « OK » ne valent rien")
    L.append("")
    w = next((r for r in rows if r[0].startswith("weakness_breadth")), None)
    if w:
        n, res, _, _ = w
        oks = [c for c in CONTROLS if res[c] == "OK"]
        L.append(f"`{n}` passe **{len(oks)}** contrôles sur 5 :")
        L.append("")
        for c in oks:
            L.append(f"- {c} : OK")
        L.append("")
        L.append("**Ce n'est pas une force, c'est un artefact d'inactivité.** Ce candidat active")
        L.append("son overlay **0,00 %** du temps : son P&L est *identique* à celui de Buy & Hold")
        L.append("(#415, #417, étiquette « PASS NON INFORMATIF » déjà portée par son rapport).")
        L.append("")
        L.append("Une série identique au benchmark ne peut évidemment pas être dégradée par un")
        L.append("stress de coûts, ni faire pire que lui en crise, ni être instable *par rapport")
        L.append("à lui-même*. Les trois « OK » mesurent une **absence de position**, pas une")
        L.append("robustesse.")
        L.append("")
        L.append("Le pré-enregistrement l'annonçait avant l'exécution : « son résultat ne dira")
        L.append("rien d'un edge ». Il est publié ici tel quel, avec sa lecture, plutôt que")
        L.append("présenté comme 3/5 encourageants.")
    L.append("")

    # --- Ce que le cycle ne fait pas --------------------------------------
    L.append("## Ce que ce cycle ne fait pas")
    L.append("")
    L.append("**Aucun verdict de niveau 1 n'est modifié.** La batterie **ajoute** un jugement,")
    L.append("elle n'annule pas un PASS pré-enregistré : chacun de ces candidats a bien atteint")
    L.append("le critère qu'il s'était fixé, sur les données annoncées. Ce que le lot établit,")
    L.append("c'est qu'aucun ne survit au filtre joint que le backlog s'impose depuis le #111.")
    L.append("")
    L.append("Ce constat était **déjà celui du backlog** : « 0 PASS RENFORCÉ » y figure depuis")
    L.append("les #111-#112. Ce cycle ne le découvre pas — il **étend sa couverture** aux")
    L.append("candidats qui avaient échappé au filtre.")
    L.append("")

    # --- Conclusion -------------------------------------------------------
    L.append("## Conclusion")
    L.append("")
    L.append("| Critère pré-enregistré | Attendu | Obtenu | |")
    L.append("|---|---|---|---|")
    L.append(f"| candidats soumis | 4/4 | {len(rows)}/4 | {'✔' if len(rows) == 4 else '✘'} |")
    L.append(f"| écartés avec raison publiée | 1 (+1 d'office) | {len(SET_ASIDE)} | ✔ |")
    L.append(f"| cinq contrôles reportés individuellement | oui | oui | ✔ |")
    L.append(f"| verdicts de niveau 1 modifiés | 0 | 0 | ✔ |")
    L.append("")
    L.append("La dette ouverte par le #431 est **soldée pour les 4 candidats exécutables**. Il")
    L.append("reste **1** candidat hors de portée de l'outil (schéma panier), listé et non")
    L.append("forcé — étendre la batterie au schéma panier serait un cycle distinct, à déclarer.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
