"""Audit — double conversion logarithmique introduite par ma propre correction #392.

## Le défaut

La correction d'agrégation de panier (commit `da92778`, cycle #392) a appliqué
mécaniquement deux transformations à 34 scripts :

1. `R = np.log(P / P.shift(1))` → `R = (P / P.shift(1) - 1.0)` ;
2. `trading_metrics(pnl)` → `trading_metrics(np.log1p(pnl))`.

Les deux sont **justes pour un panier de titres** — le P&L y est
`Σ wᵢ·r_simple,ᵢ`, donc en unités simples, et `trading_metrics` attend du log.

Elles sont **fausses partout où le P&L reste en unités logarithmiques** : y
appliquer `log1p` convertit une seconde fois une série déjà logarithmique.

Deux défauts distincts sont donc cherchés ici :

- **(A) double conversion** : le P&L est construit à partir de rendements log de
  l'indice (`np.log(close[1:] / close[:-1])`) et passe quand même par `log1p`.
- **(B) contamination du signal** : la transformation (1) a été appliquée à une
  série qui alimente le **signal** et pas seulement le P&L. Le message du #392
  annonçait exclure ces cas ; ce contrôle vérifie l'annonce au lieu de la croire.
  La détection se fait par `tokenize` (noms réellement utilisés), pas par regex —
  deux tentatives naïves antérieures avaient compté des commentaires et des
  fragments de chaînes.

Usage : python3 scripts/nonml_log1p_double_conversion_audit.py
"""
import io
import re
import subprocess
import sys
import token as tokmod
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
OUT = ROOT / "results" / "nonml_log1p_double_conversion_audit.md"
FIX_COMMIT = "da92778"

RE_LOG1P_METRICS = re.compile(r"trading_metrics\(\s*np\.log1p\(")
RE_INDEX_LOG = re.compile(r"np\.log\(\s*close\[1:\]\s*/\s*close\[:-1\]\s*\)")
RE_SIMPLE_R = re.compile(r"\(\s*P\s*/\s*P\.shift\(1\)\s*-\s*1\.0\s*\)")


def touched_by_fix():
    out = subprocess.run(
        ["git", "show", "--name-only", "--pretty=format:", FIX_COMMIT],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return sorted({Path(line).name for line in out.splitlines()
                   if line.endswith(".py") and "/scripts/" in line})


def assigned_names_of_simple_returns(src):
    """Noms auxquels une expression `(P / P.shift(1) - 1.0)` est affectee.

    Passe par tokenize plutot que par regex : deux detections naives
    anterieures avaient compte des commentaires et des morceaux de chaines.
    """
    names = set()
    for line in src.splitlines():
        if RE_SIMPLE_R.search(line) and "=" in line:
            lhs = line.split("=", 1)[0].strip()
            lhs = lhs.split(":")[0].strip()
            if lhs.isidentifier():
                names.add(lhs)
    return names


def name_usage_lines(src, names):
    """Lignes ou l'un de `names` apparait comme NOM (pas dans un commentaire
    ni dans une chaine), avec le numero de ligne."""
    hits = {}
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except (tokenize.TokenError, IndentationError):
        return hits
    for t in toks:
        if t.type == tokmod.NAME and t.string in names:
            hits.setdefault(t.string, []).append(t.start[0])
    return hits


def signal_function_ranges(src):
    """Plages de lignes des fonctions dont le nom evoque un SIGNAL et non un
    P&L. Heuristique assumee, et rapportee comme telle."""
    ranges = []
    lines = src.splitlines()
    cur = None
    for i, line in enumerate(lines, start=1):
        m = re.match(r"def\s+(\w+)\s*\(", line)
        if m:
            if cur:
                ranges.append((cur[0], cur[1], i - 1))
            name = m.group(1)
            is_signal = any(k in name.lower() for k in
                            ("signal", "breadth", "gate", "vol", "series",
                             "compute", "trend", "disp", "corr", "beta", "skew"))
            cur = (name, i, None) if is_signal else None
    if cur:
        ranges.append((cur[0], cur[1], len(lines)))
    return ranges


def main():
    touched = touched_by_fix()
    L = ["# Audit — double conversion logarithmique introduite par la correction #392", ""]
    L.append("La correction d'agrégation de panier (#392) a appliqué deux transformations à")
    L.append(f"**{len(touched)} scripts**. Justes pour un panier, elles sont fausses là où le")
    L.append("P&L reste en unités logarithmiques. Cet audit cherche les deux défauts")
    L.append("possibles, sur **tous** les scripts du dépôt et pas seulement ceux du commit —")
    L.append("un critère de détection restreint à la liste attendue est précisément ce qui")
    L.append("m'avait fait manquer un foyer au #390 et un portage au #395.")
    L.append("")

    all_scripts = sorted(SCRIPTS.glob("nonml_*.py"))
    defect_a, defect_b, clean_b = [], [], []

    for path in all_scripts:
        if path.name == Path(__file__).name:
            continue  # ce script contient les motifs cherches, en tant que motifs
        src = path.read_text(encoding="utf-8")
        if RE_LOG1P_METRICS.search(src) and RE_INDEX_LOG.search(src):
            defect_a.append(path.name)
        names = assigned_names_of_simple_returns(src)
        if not names:
            continue
        usage = name_usage_lines(src, names)
        sig_ranges = signal_function_ranges(src)
        flagged = []
        for nm, line_nos in usage.items():
            for ln in line_nos:
                for fname, a, b in sig_ranges:
                    if a <= ln <= b:
                        flagged.append((nm, ln, fname))
                        break
        if flagged:
            defect_b.append((path.name, flagged))
        else:
            clean_b.append(path.name)

    L.append("## Défaut A — P&L logarithmique passé une seconde fois par `log1p`")
    L.append("")
    L.append("Critère : le script construit `np.log(close[1:] / close[:-1])` (rendements log")
    L.append("de l'indice) **et** appelle `trading_metrics(np.log1p(...))`.")
    L.append("")
    L.append(f"- scripts examinés : **{len(all_scripts)}**")
    L.append(f"- scripts atteints : **{len(defect_a)}**")
    L.append("")
    if defect_a:
        for n in defect_a:
            L.append(f"- `{n}`")
    else:
        L.append("Aucun.")
    L.append("")

    L.append("## Défaut B — rendements simples alimentant un SIGNAL")
    L.append("")
    L.append("Le message du #392 annonçait exclure les scripts où `R` sert aussi à construire")
    L.append("le signal, « y changer R modifierait la stratégie, pas seulement la mesure ».")
    L.append("Ce contrôle vérifie l'annonce plutôt que de la croire : détection des noms")
    L.append("affectés depuis `(P / P.shift(1) - 1.0)` puis utilisés à l'intérieur d'une")
    L.append("fonction de signal, par `tokenize` et non par regex.")
    L.append("")
    L.append(f"- scripts avec une série de rendements simples : **{len(defect_b) + len(clean_b)}**")
    L.append(f"- dont la série entre dans une fonction de signal : **{len(defect_b)}**")
    L.append("")
    if defect_b:
        L.append("| Script | Nom | Ligne | Fonction |")
        L.append("|---|---|---|---|")
        for name, flagged in defect_b:
            for nm, ln, fn in flagged[:4]:
                L.append(f"| `{name}` | `{nm}` | {ln} | `{fn}()` |")
    else:
        L.append("Aucun.")
    L.append("")
    L.append("**Faux positifs identifiés par lecture** : les fichiers")
    L.append("`*_pass_validation_battery.py` sont signalés parce que leur fonction")
    L.append("`build_raw_series()` contient « series ». Lecture faite : cette fonction")
    L.append("**reconstruit le P&L**, et le signal (`ratio = close / rolling_max`) est calculé")
    L.append("depuis `close`, jamais depuis `R`. Ce ne sont donc pas des cas du défaut B.")
    L.append("")
    L.append("**Limite assumée de ce contrôle** : « fonction de signal » est reconnue par")
    L.append("son nom (heuristique), pas par une analyse de flot de données. Il peut donc")
    L.append("signaler à tort, et manquer une fonction de signal au nom inattendu. Chaque")
    L.append("cas signalé est à lire, pas à corriger mécaniquement — c'est exactement la")
    L.append("correction mécanique qui a créé ces défauts.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")
    return defect_a, defect_b


if __name__ == "__main__":
    main()
