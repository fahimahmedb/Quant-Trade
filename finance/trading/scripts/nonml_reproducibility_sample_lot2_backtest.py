"""Reproductibilité des rapports publiés — lot 2 (#435).

Spécification pré-enregistrée dans `PREREG_reproducibility_sample_lot2.md`,
committée avant tout tirage.

Resserre la borne publiée au #434 (p ≤ 22,1 % sur 12 tirages) en échantillonnant
**24 scripts supplémentaires**, disjoints des 12 déjà testés.

Régime FIXÉ AVANT EXÉCUTION, repris du #434 sans assouplissement : chaque
rapport est sauvegardé, comparé, puis **restauré à l'identique**.
"""
import random
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
OUT = RESULTS / "nonml_reproducibility_sample_lot2_result.md"

SEED = 20260814        # fixée dans le pré-enregistrement
SAMPLE_SIZE = 24       # fixée dans le pré-enregistrement
TIMEOUT_S = 300        # repris tel quel du #434

SEED_LOT1 = 20260813
SIZE_LOT1 = 12
# Les cycles de reproductibilite s'excluent de leur propre vivier : lecon du
# #434, ou le cycle s'etait ajoute lui-meme et avait decale le tirage.
SELF = {"reproducibility_sample", "reproducibility_sample_lot2"}


def pool_all():
    out = []
    for s in sorted(SCRIPTS.glob("nonml_*_backtest.py")):
        name = s.name.replace("nonml_", "").replace("_backtest.py", "")
        if name in SELF:
            continue
        if (RESULTS / f"nonml_{name}_result.md").exists():
            out.append(name)
    return out


def main():
    full = pool_all()
    lot1 = set(random.Random(SEED_LOT1).sample(full, SIZE_LOT1))
    remaining = [n for n in full if n not in lot1]
    sample = sorted(random.Random(SEED).sample(remaining, min(SAMPLE_SIZE, len(remaining))))

    L = ["# Reproductibilité des rapports publiés — lot 2 (pré-enregistré)", ""]
    L.append("Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,")
    L.append("aucun paramètre touché, **aucun rapport publié modifié**.")
    L.append("")
    L.append("Resserre la borne publiée au #434 — **p ≤ 22,1 %** sur 12 tirages — en")
    L.append("échantillonnant **24 scripts supplémentaires, disjoints des 12 déjà testés**.")
    L.append("")
    L.append("## Tirage")
    L.append("")
    L.append(f"- vivier total (backtest **et** rapport publié) : **{len(full)}**")
    L.append(f"- déjà testés au #434, exclus : **{len(lot1)}**")
    L.append(f"- vivier restant : **{len(remaining)}**")
    L.append(f"- graine, fixée au pré-enregistrement : **{SEED}**")
    L.append(f"- taille : **{len(sample)}**, délai maximal **{TIMEOUT_S} s** par script")
    L.append("")
    L.append("Échantillon tiré, publié **avant** les résultats individuels :")
    L.append("")
    for n in sample:
        L.append(f"- `{n}`")
    L.append("")

    tmp = Path(tempfile.mkdtemp(prefix="repro2_"))
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
                sample_diff = [(x, y) for x, y in zip(a, b) if x != y][:3]
                divergent.append((name, dt, nd, sample_diff))
        except subprocess.TimeoutExpired:
            inconclusive.append((name, f"délai > {TIMEOUT_S} s", "—"))
        finally:
            shutil.copy2(backup, rep)   # RESTAURATION systematique

    tested = len(identical) + len(divergent)
    L.append("## Résultat du lot 2")
    L.append("")
    L.append("| | Nombre |")
    L.append("|---|---|")
    L.append(f"| rapports **identiques** octet à octet | **{len(identical)}** |")
    L.append(f"| rapports **divergents** | **{len(divergent)}** |")
    L.append(f"| **non concluants** (délai / erreur) | **{len(inconclusive)}** |")
    L.append("")
    if tested:
        L.append(f"**Taux sur les {tested} effectivement testés : "
                 f"{100*len(identical)/tested:.1f} %.**")
    L.append("")

    if divergent:
        L.append("### Divergents — le rapport publié ne correspond plus à son code")
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
        L.append("**Ces divergences ne sont pas committées** : le rapport d'origine a été")
        L.append("restauré. Corriger un résultat publié demanderait son propre")
        L.append("pré-enregistrement et son propre régime déclaré.")
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

    # --- Borne cumulée ----------------------------------------------------
    L.append("## Borne cumulée sur les deux lots")
    L.append("")
    total_ok = SIZE_LOT1 + len(identical)
    L.append("| | Sans divergence | Borne à 95 % |")
    L.append("|---|---|---|")
    L.append(f"| #434 seul | {SIZE_LOT1} | 22,1 % |")
    if not divergent:
        b = 1.0 - 0.05 ** (1.0 / total_ok)
        b_prud = 1.0 - 0.05 ** (1.0 / (total_ok - 1))   # halloween_effect connu d'avance
        L.append(f"| **#434 + #435** | **{total_ok}** | **{100*b:.1f} %** |")
        L.append(f"| version prudente (−1 connu d'avance) | {total_ok - 1} | {100*b_prud:.1f} %")
        L.append("")
        L.append("La borne annoncée **avant** de mesurer était de **8,0 %** (8,2 % en version")
        L.append("prudente), pour 24 tirages tous identiques.")
        L.append("")
    else:
        L.append("")
        L.append("**La borne ne s'applique plus** : une divergence a été observée. Le résultat")
        L.append("principal du cycle est la divergence elle-même, publiée ci-dessus, et non un")
        L.append("taux resserré.")
        L.append("")

    L.append("## Portée")
    L.append("")
    L.append(f"Les deux lots couvrent **{SIZE_LOT1 + len(sample)}** scripts sur **{len(full)}**, soit")
    L.append(f"**{100*(SIZE_LOT1 + len(sample))/len(full):.1f} %** du dépôt. Les tirages étant")
    L.append("aléatoires à graines fixées d'avance et **disjoints**, ils sont reproductibles et")
    L.append("non choisis.")
    L.append("")

    shutil.rmtree(tmp, ignore_errors=True)
    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
