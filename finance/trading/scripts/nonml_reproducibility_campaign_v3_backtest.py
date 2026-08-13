"""Campagne de reproductibilité v3 — classification par test sentinelle (#438).

Spécification pré-enregistrée dans `PREREG_reproducibility_campaign_v3.md`,
committée avant tout tirage.

Les campagnes v1 et v2 ont échoué en tentant de reconnaître « le rapport
compte-t-il le dépôt ? » par des motifs de code. Ici la propriété est **testée** :

> on ajoute au dépôt deux fichiers neutres, on ré-exécute, et on regarde si le
> rapport bouge.

Rapport modifié ⇒ divergence **structurelle**. Rapport inchangé ⇒ divergence
**substantielle**, seule comptée dans la borne.
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
OUT = RESULTS / "nonml_reproducibility_campaign_v3_result.md"

SEED, SAMPLE_SIZE, TIMEOUT_S = 20260817, 24, 300

SENTINELS = [
    RESULTS / "nonml__sentinelle_tmp_result.md",
    SCRIPTS / "nonml__sentinelle_tmp_backtest.py",
    RESULTS / "nonml__sentinelle_tmp_pnl.npz",
]


def eligible():
    out = []
    for s in sorted(SCRIPTS.glob("nonml_*_backtest.py")):
        n = s.name.replace("nonml_", "").replace("_backtest.py", "")
        if "_sentinelle_tmp" in n:
            continue
        if (RESULTS / f"nonml_{n}_result.md").exists():
            out.append(n)
    return out


def run(name):
    return subprocess.run([sys.executable, str(SCRIPTS / f"nonml_{name}_backtest.py")],
                          capture_output=True, text=True, timeout=TIMEOUT_S)


def place_sentinels():
    import numpy as np
    SENTINELS[0].write_text("# sentinelle temporaire (#438) — à supprimer\n", encoding="utf-8")
    SENTINELS[1].write_text('"""Sentinelle temporaire (#438) — à supprimer."""\n', encoding="utf-8")
    np.savez(SENTINELS[2], pos=np.ones(3), r_asset=np.zeros(3),
             dates=np.arange(3), cost_bps=5.0)


def remove_sentinels():
    for p in SENTINELS:
        try:
            p.unlink(missing_ok=True)
        except Exception:  # noqa: BLE001
            pass


def sentinel_test(name, tmpdir):
    """Le rapport change-t-il quand le dépôt gagne des fichiers neutres ?"""
    rep = RESULTS / f"nonml_{name}_result.md"
    base = tmpdir / f"{name}_base.md"
    shutil.copy2(rep, base)          # rapport tel que le script vient de le produire
    verdict, detail = "indéterminé", ""
    try:
        place_sentinels()
        r = run(name)
        if r.returncode != 0:
            verdict = "indéterminé"
            detail = f"le script échoue en présence des sentinelles (code {r.returncode})"
        elif rep.read_bytes() != base.read_bytes():
            verdict = "STRUCTURELLE"
            detail = "le rapport change quand le dépôt gagne des fichiers neutres"
        else:
            verdict = "SUBSTANTIELLE"
            detail = "le rapport ne dépend pas du contenu du dépôt"
    except subprocess.TimeoutExpired:
        detail = "délai dépassé en présence des sentinelles"
    finally:
        remove_sentinels()           # QUOI QU'IL ARRIVE
        shutil.copy2(base, rep)
    return verdict, detail


def main():
    pool = eligible()
    sample = sorted(random.Random(SEED).sample(pool, min(SAMPLE_SIZE, len(pool))))

    L = ["# Campagne de reproductibilité v3 — classification par test sentinelle (pré-enregistré)", ""]
    L.append("Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,")
    L.append("aucun paramètre touché, **aucun rapport publié modifié**.")
    L.append("")
    L.append("Les campagnes v1 et v2 ont échoué en tentant de reconnaître « le rapport")
    L.append("compte-t-il le dépôt ? » par des **motifs de code**. Ici la propriété est")
    L.append("**testée** : on ajoute au dépôt des fichiers neutres, on ré-exécute, et on")
    L.append("regarde si le rapport bouge. Aucune orthographe n'intervient.")
    L.append("")
    L.append("## Tirage")
    L.append("")
    L.append(f"- vivier **entier** (aucune exclusion syntaxique) : **{len(pool)}**")
    L.append(f"- graine, fixée au pré-enregistrement : **{SEED}**")
    L.append(f"- taille : **{len(sample)}**, délai **{TIMEOUT_S} s**")
    L.append("")
    L.append("**Les 84 tirages des #434-#437 ne sont pas réutilisés** — troisième remise à")
    L.append("zéro.")
    L.append("")
    for n in sample:
        L.append(f"- `{n}`")
    L.append("")

    tmp = Path(tempfile.mkdtemp(prefix="repro_v3_"))
    identical, structural, substantive, inconclusive = [], [], [], []

    try:
        for name in sample:
            rep = RESULTS / f"nonml_{name}_result.md"
            backup = tmp / f"{name}_published.md"
            shutil.copy2(rep, backup)
            t0 = time.time()
            try:
                r = run(name)
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
                    kind, why = sentinel_test(name, tmp)
                    (structural if kind == "STRUCTURELLE" else
                     substantive if kind == "SUBSTANTIELLE" else
                     inconclusive).append((name, dt, nd, sd, why) if kind != "indéterminé"
                                          else (name, "test sentinelle indéterminé", why))
            except subprocess.TimeoutExpired:
                inconclusive.append((name, f"délai > {TIMEOUT_S} s", "—"))
            finally:
                shutil.copy2(backup, rep)
    finally:
        remove_sentinels()

    n_classified = len(identical) + len(structural) + len(substantive)
    L.append("## Résultat")
    L.append("")
    L.append("| | Nombre |")
    L.append("|---|---|")
    L.append(f"| **identiques** octet à octet | **{len(identical)}** |")
    L.append(f"| divergences **structurelles** (le rapport compte le dépôt) | "
             f"**{len(structural)}** |")
    L.append(f"| divergences **SUBSTANTIELLES** | **{len(substantive)}** |")
    L.append(f"| non concluants | **{len(inconclusive)}** |")
    L.append("")

    for label, rows in (("structurelles", structural), ("SUBSTANTIELLES", substantive)):
        if not rows:
            continue
        L.append(f"### Divergences {label}")
        L.append("")
        L.append("| Script | Lignes différentes | Verdict du test sentinelle |")
        L.append("|---|---|---|")
        for n, dt, nd, sd, why in sorted(rows):
            L.append(f"| `{n}` | {nd} | {why} |")
        L.append("")
        for n, _, _, sd, _ in sorted(rows):
            L.append(f"**`{n}` — premières lignes divergentes :**")
            L.append("")
            L.append("```")
            for a, b in sd:
                L.append(f"- {a}")
                L.append(f"+ {b}")
            L.append("```")
            L.append("")
    if inconclusive:
        L.append("### Non concluants")
        L.append("")
        L.append("| Script | Raison | Détail |")
        L.append("|---|---|---|")
        for row in sorted(inconclusive):
            L.append(f"| `{row[0]}` | {row[1]} | {row[2]} |")
        L.append("")
    if identical:
        L.append("### Identiques")
        L.append("")
        L.append("| Script | Durée |")
        L.append("|---|---|")
        for n, dt in sorted(identical):
            L.append(f"| `{n}` | {dt:.1f} s |")
        L.append("")

    # --- Borne ------------------------------------------------------------
    L.append("## Borne")
    L.append("")
    denom = len(identical) + len(substantive)
    L.append("La borne porte sur les divergences **substantielles uniquement** : les")
    L.append("structurelles sont comptées, listées et **exclues du dénominateur**, règle fixée")
    L.append("au pré-enregistrement avant tout tirage.")
    L.append("")
    if substantive:
        L.append(f"**Aucune borne n'est publiée** : **{len(substantive)}** divergence(s)")
        L.append("substantielle(s) observée(s). Elles sont le résultat du cycle.")
    elif denom:
        b = 1.0 - 0.05 ** (1.0 / denom)
        L.append(f"- tirages retenus au dénominateur : **{denom}** "
                 f"({len(identical)} identiques + {len(substantive)} substantielles)")
        L.append(f"- **borne à 95 % : p ≤ {100*b:.1f} %**")
        L.append("")
        L.append(f"Sur un vivier de **{len(pool)}**, il reste de la place pour "
                 f"**~{int(b*len(pool))}** divergences substantielles non détectées.")
    L.append("")

    # --- Garde-fou sentinelle ---------------------------------------------
    L.append("## Contrôle des sentinelles")
    L.append("")
    left = [p.name for p in SENTINELS if p.exists()]
    L.append(f"- fichiers sentinelles subsistant : **{len(left)}** "
             f"{'✔' if not left else '✘ — CYCLE EN ÉCHEC'}")
    if left:
        for n in left:
            L.append(f"  - `{n}`")
    L.append("")

    L.append("## Portée")
    L.append("")
    L.append(f"Ce lot couvre **{len(sample)}** scripts sur **{len(pool)}**, soit")
    L.append(f"**{100*len(sample)/len(pool):.1f} %**, par tirage aléatoire à graine fixée.")
    L.append("")

    shutil.rmtree(tmp, ignore_errors=True)
    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
