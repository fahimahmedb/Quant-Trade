"""Reproductibilité des rapports publiés — lot 3 (#436).

Spécification pré-enregistrée dans `PREREG_reproducibility_sample_lot3.md`,
committée avant tout tirage.

Deux volets :
- **A** : 24 tirages supplémentaires, disjoints des 36 des #434/#435, pour
  porter la borne cumulée de 8,0 % vers ~4,9 % ;
- **B** : contrôle de **représentativité en âge** du cumul des trois lots —
  la borne suppose des scripts représentatifs, ce que personne n'avait vérifié.

Régime FIXÉ AVANT EXÉCUTION : chaque rapport est sauvegardé, comparé, puis
**restauré à l'identique**.
"""
import random
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
OUT = RESULTS / "nonml_reproducibility_sample_lot3_result.md"

SEED, SAMPLE_SIZE, TIMEOUT_S = 20260815, 24, 300
LOTS = [(20260813, 12), (20260814, 24)]          # graines et tailles anterieures
SELF = {"reproducibility_sample", "reproducibility_sample_lot2",
        "reproducibility_sample_lot3"}
AGE_TOLERANCE_POINTS = 10.0                      # fixe au pre-enregistrement


def pool_all():
    out = []
    for s in sorted(SCRIPTS.glob("nonml_*_backtest.py")):
        name = s.name.replace("nonml_", "").replace("_backtest.py", "")
        if name in SELF:
            continue
        if (RESULTS / f"nonml_{name}_result.md").exists():
            out.append(name)
    return out


def added_ts(name: str):
    r = subprocess.run(
        ["git", "log", "--reverse", "--format=%ct", "--diff-filter=A", "--",
         f"finance/trading/results/nonml_{name}_result.md"],
        cwd=str(REPO), capture_output=True, text=True, timeout=120)
    out = [l for l in r.stdout.split("\n") if l.strip().isdigit()]
    return int(out[0]) if out else None


def main():
    full = pool_all()
    already = set()
    remaining = list(full)
    for seed, size in LOTS:
        drawn = set(random.Random(seed).sample(remaining, size))
        already |= drawn
        remaining = [n for n in remaining if n not in drawn]
    sample = sorted(random.Random(SEED).sample(remaining, min(SAMPLE_SIZE, len(remaining))))

    L = ["# Reproductibilité des rapports publiés — lot 3 (pré-enregistré)", ""]
    L.append("Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,")
    L.append("aucun paramètre touché, **aucun rapport publié modifié**.")
    L.append("")
    L.append("## Volet A — tirage")
    L.append("")
    L.append(f"- vivier total : **{len(full)}**")
    L.append(f"- déjà testés aux #434 / #435, exclus : **{len(already)}**")
    L.append(f"- vivier restant : **{len(remaining)}**")
    L.append(f"- graine, fixée au pré-enregistrement : **{SEED}**")
    L.append(f"- taille : **{len(sample)}**, délai maximal **{TIMEOUT_S} s**")
    L.append("")
    L.append("Échantillon tiré, publié **avant** les résultats individuels :")
    L.append("")
    for n in sample:
        L.append(f"- `{n}`")
    L.append("")

    tmp = Path(tempfile.mkdtemp(prefix="repro3_"))
    identical, divergent, inconclusive = [], [], []
    for name in sample:
        rep = RESULTS / f"nonml_{name}_result.md"
        backup = tmp / rep.name
        shutil.copy2(rep, backup)
        t0 = time.time()
        try:
            r = subprocess.run([sys.executable, str(SCRIPTS / f"nonml_{name}_backtest.py")],
                               capture_output=True, text=True, timeout=TIMEOUT_S)
            dt = time.time() - t0
            if r.returncode != 0:
                inconclusive.append((name, f"code {r.returncode}",
                                     (r.stderr.strip().splitlines() or ["—"])[-1][:160]))
            elif rep.read_bytes() == backup.read_bytes():
                identical.append((name, dt))
            else:
                a = backup.read_text(encoding="utf-8").splitlines()
                b = rep.read_text(encoding="utf-8").splitlines()
                nd = sum(1 for x, y in zip(a, b) if x != y) + abs(len(a) - len(b))
                sd = [(x, y) for x, y in zip(a, b) if x != y][:3]
                divergent.append((name, dt, nd, sd))
        except subprocess.TimeoutExpired:
            inconclusive.append((name, f"délai > {TIMEOUT_S} s", "—"))
        finally:
            shutil.copy2(backup, rep)

    tested = len(identical) + len(divergent)
    L.append("## Volet A — résultat")
    L.append("")
    L.append("| | Nombre |")
    L.append("|---|---|")
    L.append(f"| **identiques** octet à octet | **{len(identical)}** |")
    L.append(f"| **divergents** | **{len(divergent)}** |")
    L.append(f"| **non concluants** | **{len(inconclusive)}** |")
    L.append("")
    if divergent:
        L.append("### Divergents")
        L.append("")
        L.append("| Script | Durée | Lignes différentes |")
        L.append("|---|---|---|")
        for n, dt, nd, _ in sorted(divergent):
            L.append(f"| `{n}` | {dt:.1f} s | {nd} |")
        L.append("")
        for n, _, _, sd in sorted(divergent):
            L.append(f"**`{n}` — premières lignes divergentes :**")
            L.append("")
            L.append("```")
            for a, b in sd:
                L.append(f"- {a}")
                L.append(f"+ {b}")
            L.append("```")
            L.append("")
        L.append("**Non committées** : le rapport d'origine a été restauré.")
        L.append("")
    if inconclusive:
        L.append("### Non concluants")
        L.append("")
        L.append("| Script | Raison | Détail |")
        L.append("|---|---|---|")
        for n, why, det in sorted(inconclusive):
            L.append(f"| `{n}` | {why} | {det} |")
        L.append("")
    if identical:
        L.append("### Identiques")
        L.append("")
        L.append("| Script | Durée |")
        L.append("|---|---|")
        for n, dt in sorted(identical):
            L.append(f"| `{n}` | {dt:.1f} s |")
        L.append("")

    prior_ok = sum(size for _, size in LOTS)
    total_ok = prior_ok + len(identical)
    L.append("## Volet A — borne cumulée sur les trois lots")
    L.append("")
    if not divergent:
        b = 1.0 - 0.05 ** (1.0 / total_ok)
        bp = 1.0 - 0.05 ** (1.0 / (total_ok - 1))
        L.append("| | Sans divergence | Borne à 95 % | Divergents encore possibles |")
        L.append("|---|---|---|---|")
        for n, lab in ((12, "#434"), (36, "#434 + #435"), (total_ok, "**les trois lots**")):
            bb = 1.0 - 0.05 ** (1.0 / n)
            L.append(f"| {lab} | {n} | {100*bb:.1f} % | ~{int(bb*len(full))} |")
        L.append("")
        L.append(f"Version prudente (−1 connu d'avance) : **{100*bp:.1f} %**.")
        L.append("")
        L.append("La borne annoncée avant la mesure était de **~4,9 %**.")
    else:
        L.append("**La borne ne s'applique plus** — une divergence a été observée. Le résultat")
        L.append("principal du cycle est la divergence elle-même.")
    L.append("")

    # --- Volet B : représentativité en âge --------------------------------
    L.append("## Volet B — représentativité en âge du cumul")
    L.append("")
    L.append("La borne suppose que les scripts testés sont **représentatifs** du dépôt. Si les")
    L.append("tirages se concentraient sur les rapports **récents**, elle serait rassurante à")
    L.append("tort : le code partagé a évolué et les corrections #375-#404 ont touché des")
    L.append("fonctions communes **après** la publication de beaucoup de rapports.")
    L.append("")
    ages = {n: added_ts(n) for n in full}
    ages = {n: t for n, t in ages.items() if t is not None}
    tested_all = sorted((already | set(sample)) & set(ages))
    pool_sorted = sorted(ages, key=lambda n: ages[n])
    third = max(1, len(pool_sorted) // 3)
    oldest_third = set(pool_sorted[:third])
    n_tested_old = len(set(tested_all) & oldest_third)
    expected_share = 100.0 * len(tested_all) / len(ages)
    observed_share = 100.0 * n_tested_old / len(oldest_third)
    gap = observed_share - expected_share
    representative = abs(gap) <= AGE_TOLERANCE_POINTS

    med_pool = statistics.median(ages.values())
    med_tested = statistics.median([ages[n] for n in tested_all])
    import datetime as dt_
    fmt = lambda t: dt_.datetime.utcfromtimestamp(t).strftime("%Y-%m-%d")

    L.append("| | Vivier | Testés |")
    L.append("|---|---|---|")
    L.append(f"| effectif | {len(ages)} | {len(tested_all)} |")
    L.append(f"| date de publication médiane | {fmt(med_pool)} | {fmt(med_tested)} |")
    L.append("")
    L.append(f"- part des testés dans le vivier entier : **{expected_share:.1f} %**")
    L.append(f"- part des testés dans le **tiers le plus ancien** ({len(oldest_third)} rapports) : "
             f"**{observed_share:.1f} %**")
    L.append(f"- écart : **{gap:+.1f} points** — tolérance fixée avant mesure : "
             f"**±{AGE_TOLERANCE_POINTS:.0f} points**")
    L.append("")
    if representative:
        L.append("**Tirage représentatif en âge.** Les rapports anciens sont couverts à la même")
        L.append("fréquence que les récents : la borne du volet A s'applique au dépôt entier,")
        L.append("pas seulement à sa partie récente.")
    else:
        L.append("**Tirage NON représentatif en âge.** La borne du volet A doit être lue avec")
        L.append("cette réserve : elle ne couvre pas également les rapports anciens, qui sont")
        L.append("précisément les plus exposés à la dérive du code partagé.")
    L.append("")

    L.append("## Portée")
    L.append("")
    L.append(f"Les trois lots couvrent **{len(tested_all)}** scripts sur **{len(full)}**, soit")
    L.append(f"**{100*len(tested_all)/len(full):.1f} %** du dépôt, par tirages aléatoires")
    L.append("**disjoints** à graines fixées d'avance.")
    L.append("")

    shutil.rmtree(tmp, ignore_errors=True)
    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
