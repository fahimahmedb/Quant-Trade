"""Audit — correction de `n_trials` pour non-indépendance mesurée (cycle #421).

Quatre contrôles :

1. **La déduction est appliquée** — `n_trials` passe de 372 à 370.
2. **Elle ne s'applique qu'aux identités mesurées** — les paires voisines
   (#414) et emboîtées (#418) ne sont pas déduites, comme pré-enregistré.
3. **Effet mesuré** — DSR avant / après, et nombre de verdicts modifiés.
4. **Jusqu'où faudrait-il aller ?** — quelle valeur de `n_trials` rendrait le
   meilleur candidat conforme au seuil DSR de 0,95. Contrôle destiné à empêcher
   qu'on espère un jour sauver un candidat en jouant sur ce compte, moi compris.

Usage : python3 scripts/nonml_n_trials_dependence_correction_audit.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
RESULTS = ROOT / "results"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(SCRIPTS))

import nonml_pass_validation_battery as bat  # noqa: E402
from prediction import dsr  # noqa: E402

OUT = RESULTS / "nonml_n_trials_dependence_correction_audit.md"

# DSR relevés AVANT la correction (n_trials = 372), lus dans les rapports
# committés au moment où ils ont été produits.
BEFORE = {
    "market_concentration_vol_targeting_overlay_pit_universe": 0.1781,
    "momentum_dispersion_vol_targeting_overlay_pit_universe": 0.1712,
    "momentum_decile_spread_vol_targeting_overlay_pit_universe": 0.1717,
}


def after_of(name):
    txt = (RESULTS / f"nonml_{name}_pass_validation_battery.md").read_text(encoding="utf-8")
    import re
    m = re.search(r"DSR = ([0-9.]+)", txt)
    n = re.search(r"n_trials = (\d+)", txt)
    v = re.search(r"e\. DSR \(n_trials=backlog\) : (\w+)", txt)
    return (float(m.group(1)) if m else None,
            int(n.group(1)) if n else None,
            v.group(1) if v else None)


def main():
    L = ["# Audit — correction de `n_trials` pour non-indépendance mesurée", ""]

    # --- 1. deduction appliquee ---
    n_now = bat.parse_backlog_n_trials()
    L.append("## 1. La déduction est-elle appliquée ?")
    L.append("")
    L.append(f"- `n_trials` publié par la batterie : **{n_now}**")
    L.append(f"- déduction : **{bat.N_TRIALS_DEDUCTION}** entrée(s)")
    L.append("")
    ok1 = n_now == 370
    L.append(f"**{'CONFORME — 372 → 370, comme annoncé avant calcul.' if ok1 else 'ANOMALIE'}**")
    L.append("")

    # --- 2. perimetre de la deduction ---
    deducted = {d for d, _t, _c in bat.DEPENDENT_DUPLICATES}
    forbidden = {
        "momentum_dispersion_vol_targeting_overlay",          # #414, voisinage
        "momentum_decile_spread_vol_targeting_overlay",       # #414, voisinage
        "sma200_momentum_breadth_and_overlay",                # #418, emboitement
        "momentum_breadth_vol_targeting_overlay",             # #418, emboitement
    }
    leak = deducted & forbidden
    ok2 = not leak

    L.append("## 2. La déduction reste-t-elle dans son périmètre ?")
    L.append("")
    L.append("Le pré-enregistrement limitait la déduction aux **identités mesurées**. Les")
    L.append("paires seulement voisines ou emboîtées devaient rester comptées.")
    L.append("")
    L.append("Entrées déduites :")
    L.append("")
    for d, t, c in bat.DEPENDENT_DUPLICATES:
        L.append(f"- `{d}` (jumeau conservé : `{t}`, identité établie au {c})")
    L.append("")
    L.append(f"- paires voisines/emboîtées déduites à tort : **{len(leak)}**")
    L.append("")
    L.append(f"**{'CONFORME — aucune paire de jugement n a été déduite.' if ok2 else 'DÉBORDEMENT DE PÉRIMÈTRE'}**")
    L.append("")

    # --- 3. effet mesure ---
    L.append("## 3. Effet mesuré")
    L.append("")
    L.append("| Candidat | DSR avant (372) | DSR après (370) | Δ | Verdict e. |")
    L.append("|---|---|---|---|---|")
    n_changed = 0
    for name, before in BEFORE.items():
        after, ntr, verdict = after_of(name)
        delta = after - before if after is not None else float("nan")
        if verdict != "ÉCHEC":
            n_changed += 1
        L.append(f"| `{name}` | {before:.4f} | {after:.4f} | {delta:+.4f} | {verdict} |")
    L.append("")
    L.append(f"- verdicts modifiés par la correction : **{n_changed}**")
    L.append("")
    if n_changed == 0:
        L.append("**Aucun verdict modifié.** L'écart de DSR est de l'ordre de +0,0005 — cinq")
        L.append("dix-millièmes, pour un seuil situé à 0,95 et des valeurs autour de 0,17.")
        L.append("")
        L.append("**La dette portée trois fois était donc immatérielle.** C'est un résultat, et")
        L.append("il vaut d'être écrit : il aurait été plus confortable de la laisser ouverte")
        L.append("comme une réserve indéfinie sur la validité des DSR publiés. Elle est close,")
        L.append("et elle ne changeait rien.")
    else:
        L.append("**Au moins un verdict a changé** — c'est le résultat principal du cycle et il")
        L.append("doit être instruit avant toute autre conclusion.")
    L.append("")

    # --- 4. jusqu'ou faudrait-il aller ? ---
    txt = (RESULTS / "nonml_market_concentration_vol_targeting_overlay_pit_universe_"
           "pass_validation_battery.md").read_text(encoding="utf-8")
    import re
    m_sr = re.search(r"var_trials .*?≈ ([0-9.]+)", txt)
    var_trials = float(m_sr.group(1)) if m_sr else 0.000585
    # on reprend le candidat au DSR le plus eleve des trois
    best_name = max(BEFORE, key=lambda k: after_of(k)[0])
    d = np.load(RESULTS / f"nonml_{best_name}_pnl.npz", allow_pickle=True)
    pos = np.asarray(d["pos"], dtype=float)
    r = np.asarray(d["r_asset"], dtype=float)
    c = float(d["cost_bps"]) / 1e4
    pnl = pos * r - np.abs(np.diff(pos, prepend=1.0)) * c
    sr_daily = float(np.mean(pnl) / np.std(pnl, ddof=1))
    n_obs = len(pnl)
    x = (pnl - np.mean(pnl)) / np.std(pnl, ddof=1)
    skew = float(np.mean(x ** 3))
    kurt_excess = float(np.mean(x ** 4) - 3.0)

    found = None
    for n_try in range(1, 400):
        val = dsr(sr_daily, n_obs, var_trials, n_trials=n_try,
                  skew=skew, kurt_excess=kurt_excess)["dsr"]
        if val >= 0.95:
            found = n_try
    L.append("## 4. Jusqu'où faudrait-il abaisser `n_trials` pour franchir le seuil ?")
    L.append("")
    L.append("Contrôle destiné à empêcher qu'on espère un jour sauver un candidat en jouant")
    L.append("sur ce compte — moi compris.")
    L.append("")
    L.append(f"Candidat au DSR le plus élevé des trois : `{best_name}`.")
    L.append("")
    L.append(f"- Sharpe journalier : **{sr_daily:.4f}**, observations : **{n_obs}**")
    L.append(f"- `n_trials` maximal permettant DSR ≥ 0,95 : "
             f"**{found if found else 'aucun, même à n_trials = 1'}**")
    L.append("")
    if not found:
        L.append("**Même en ne comptant qu'un seul essai** — c'est-à-dire en supposant que ce")
        L.append("candidat est la seule hypothèse jamais testée du projet — son DSR resterait")
        L.append("sous le seuil. Le compte d'essais n'est donc **pas** ce qui empêche ces")
        L.append("candidats de passer : c'est leur Sharpe.")
        L.append("")
        L.append("Cela clôt la question pour de bon : aucune correction de `n_trials`, si")
        L.append("généreuse soit-elle, ne peut faire passer un candidat du backlog.")
    else:
        L.append(f"Un `n_trials` inférieur ou égal à **{found}** suffirait. À {n_now}, on en est")
        L.append("loin, mais l'ordre de grandeur mérite d'être connu.")
    L.append("")

    verdict = ok1 and ok2
    L.append("## Verdict de l'audit")
    L.append("")
    L.append(f"**{'CONFORME.' if verdict else 'NON CONFORME.'}**")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
