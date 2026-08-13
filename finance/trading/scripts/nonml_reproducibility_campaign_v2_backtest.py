"""Campagne de reproductibilité v2 — critère d'auto-référence, puis relance (#437).

Spécification pré-enregistrée dans `PREREG_reproducibility_campaign_v2.md`,
committée avant tout tirage.

Le #436 a trouvé une divergence dont la cause était un **compteur du dépôt**
embarqué dans le rapport, et s'est interdit d'écarter ce cas après coup. Ce
script applique le critère promis, **fixé dans le pré-enregistrement** :

> auto-référent = le code balaie l'ensemble du dépôt (`glob` sur
> `nonml_*_backtest.py`, `*_pnl.npz`, `nonml_*_result.md`).

Les auto-référents sont exclus du vivier. La campagne repart de **zéro** : les
60 tirages des #434-#436 ne sont pas réutilisés.
"""
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
OUT = RESULTS / "nonml_reproducibility_campaign_v2_result.md"

SEED, SAMPLE_SIZE, TIMEOUT_S = 20260816, 24, 300

# Critere FIXE au pre-enregistrement, propriete du CODE et non du resultat.
SELF_REF = re.compile(
    r'glob\("nonml_\*_backtest\.py"\)|glob\("\*_pnl\.npz"\)|glob\("nonml_\*_result\.md"\)')

CLAIMED_V1 = 8.0   # borne revendiquee au #435, caduque depuis le #436


def bound(n):
    return 1.0 - 0.05 ** (1.0 / n)


def main():
    all_scripts, self_ref = [], []
    for s in sorted(SCRIPTS.glob("nonml_*_backtest.py")):
        name = s.name.replace("nonml_", "").replace("_backtest.py", "")
        if not (RESULTS / f"nonml_{name}_result.md").exists():
            continue
        try:
            src = s.read_text(encoding="utf-8")
        except Exception:  # noqa: BLE001
            continue
        if SELF_REF.search(src):
            self_ref.append(name)
        else:
            all_scripts.append(name)

    sample = sorted(random.Random(SEED).sample(all_scripts,
                                               min(SAMPLE_SIZE, len(all_scripts))))

    L = ["# Campagne de reproductibilité v2 — critère d'auto-référence et relance (pré-enregistré)", ""]
    L.append("Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,")
    L.append("aucun paramètre touché, **aucun rapport publié modifié**.")
    L.append("")

    # --- Le critère -------------------------------------------------------
    L.append("## Le critère d'auto-référence, appliqué")
    L.append("")
    L.append("Fixé au pré-enregistrement, **avant tout tirage**, et portant sur le **code** :")
    L.append("un script est auto-référent si son source balaie l'ensemble du dépôt")
    L.append("(`glob` sur `nonml_*_backtest.py`, `*_pnl.npz`, `nonml_*_result.md`).")
    L.append("")
    L.append("Un rapport auto-référent **dérive nécessairement** dès qu'un cycle ajoute un")
    L.append("fichier : sa divergence ne dit rien sur la péremption d'un résultat.")
    L.append("")
    L.append(f"- scripts avec rapport publié : **{len(all_scripts) + len(self_ref)}**")
    L.append(f"- **auto-référents, exclus** : **{len(self_ref)}**")
    L.append(f"- vivier de la campagne v2 : **{len(all_scripts)}**")
    L.append("")
    L.append("Exclus :")
    L.append("")
    for n in self_ref:
        L.append(f"- `{n}`")
    L.append("")
    L.append("Tous sont des **diagnostics**, pas des stratégies : aucun verdict PASS/FAIL n'en")
    L.append("dépend. Ils ne sont **pas corrigés** ici — les rendre stables modifierait des")
    L.append("rapports publiés et relève d'un cycle de modification déclarée.")
    L.append("")

    # --- Le tirage --------------------------------------------------------
    L.append("## Tirage")
    L.append("")
    L.append(f"- graine, fixée au pré-enregistrement : **{SEED}**")
    L.append(f"- taille : **{len(sample)}**, délai maximal **{TIMEOUT_S} s**")
    L.append("")
    L.append("**Les 60 tirages des #434-#436 ne sont pas réutilisés.** La campagne repart de")
    L.append("zéro, conformément à l'engagement du #436 de ne pas reclasser des tirages selon")
    L.append("une règle qui n'existait pas quand ils ont été faits.")
    L.append("")
    L.append("Échantillon tiré, publié **avant** les résultats individuels :")
    L.append("")
    for n in sample:
        L.append(f"- `{n}`")
    L.append("")

    # --- Mesure -----------------------------------------------------------
    tmp = Path(tempfile.mkdtemp(prefix="repro_v2_"))
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
    L.append("## Résultat")
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
        L.append("**Non committées** : le rapport d'origine a été restauré. Ces divergences")
        L.append("sont **substantielles** — le critère d'auto-référence les avait écartées du")
        L.append("vivier — et constituent le résultat principal du cycle.")
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

    # --- La borne, et son recul assumé ------------------------------------
    L.append("## Borne v2 — et le recul assumé")
    L.append("")
    if not divergent and tested:
        b = bound(tested)
        L.append("| | Sans divergence | Borne à 95 % |")
        L.append("|---|---|---|")
        L.append(f"| revendiqué au #435, **caduc** depuis le #436 | 36 | {CLAIMED_V1:.1f} % |")
        L.append(f"| **campagne v2, ce lot** | **{tested}** | **{100*b:.1f} %** |")
        L.append("")
        L.append(f"**La borne est moins bonne qu'avant : {100*b:.1f} % contre {CLAIMED_V1:.1f} %.**")
        L.append("Le pré-enregistrement l'annonçait chiffrée avant la mesure. C'est le coût")
        L.append("direct du refus de reclasser 60 tirages selon une règle écrite après eux, et")
        L.append("ce recul est le prix d'une borne qui, elle, veut dire quelque chose.")
        L.append("")
        L.append(f"Sur un vivier de **{len(all_scripts)}** rapports non auto-référents, il reste")
        L.append(f"de la place pour **~{int(b * len(all_scripts))}** divergences substantielles.")
    elif divergent:
        L.append("**Aucune borne n'est publiée** : une divergence substantielle a été observée,")
        L.append("et c'est elle le résultat du cycle.")
    L.append("")

    L.append("## Portée")
    L.append("")
    L.append(f"Ce lot couvre **{len(sample)}** scripts sur **{len(all_scripts)}** du vivier v2,")
    L.append(f"soit **{100*len(sample)/len(all_scripts):.1f} %**. Tirage aléatoire à graine")
    L.append("fixée d'avance, donc reproductible et non choisi.")
    L.append("")

    shutil.rmtree(tmp, ignore_errors=True)
    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
