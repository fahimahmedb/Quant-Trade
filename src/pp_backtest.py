"""Protocole d'evaluation hors-echantillon (OOS) du module « prediction politique ».

DISCIPLINE ANTI-DATA-SNOOPING (portee de scripts/run_etape_c.py) :
- Fenetre EXPANSIVE : pour predire l'election de l'annee T, une source n'est
  entrainee que sur les elections d'annee < T. Aucun acces au futur, jamais.
- L'univers de sources / la specification sont figes AVANT de lire les scores.
- On ne re-itere pas sur l'echantillon de test jusqu'a un chiffre plaisant :
  on allonge l'historique ou on ameliore les donnees, puis on re-teste une fois.

Grandeur scoree : part du candidat de reference au 2nd tour (r2_share) et
issue binaire (reference gagne / perd).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np
from scipy.stats import norm

from pp_types import ElectionContext, Source, SourceSignal, TrainingExample

# Fabrique de source : rend une instance NEUVE a chaque pli (evite toute fuite
# d'etat d'un pli a l'autre).
SourceFactory = Callable[[], Source]


# --------------------------------------------------------------------------- #
# Metriques                                                                     #
# --------------------------------------------------------------------------- #


def win_prob_from_normal(mean: float, sd: float) -> float:
    """P(part > 0.5) sous une gaussienne N(mean, sd) = proba de victoire."""
    if sd <= 0:
        return 1.0 if mean > 0.5 else 0.0
    return float(norm.cdf((mean - 0.5) / sd))


def brier_score(probs: Sequence[float], outcomes: Sequence[int]) -> float:
    """Moyenne des (p - y)^2. 0 = parfait, 0.25 = pile ou face constant."""
    p, y = np.asarray(probs, float), np.asarray(outcomes, float)
    return float(np.mean((p - y) ** 2))


def log_loss_binary(probs: Sequence[float], outcomes: Sequence[int], eps: float = 1e-9) -> float:
    """Log-loss (entropie croisee) binaire, en nats."""
    p = np.clip(np.asarray(probs, float), eps, 1 - eps)
    y = np.asarray(outcomes, float)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def mae(pred: Sequence[float], actual: Sequence[float]) -> float:
    return float(np.mean(np.abs(np.asarray(pred, float) - np.asarray(actual, float))))


# --------------------------------------------------------------------------- #
# Boucle OOS                                                                    #
# --------------------------------------------------------------------------- #


@dataclass
class FoldRecord:
    election_id: str
    year: int
    reference_id: str
    pred_share: float
    pred_win_prob: float
    actual_share: float
    actual_win: int
    available: bool


@dataclass
class BacktestReport:
    source_name: str
    folds: list[FoldRecord]

    def scored(self) -> list[FoldRecord]:
        """Plis effectivement scorables (source disponible + part reelle finie)."""
        return [f for f in self.folds if f.available and np.isfinite(f.actual_share)]

    def metrics(self) -> dict[str, float]:
        s = self.scored()
        if not s:
            return {"n": 0}
        probs = [f.pred_win_prob for f in s]
        wins = [f.actual_win for f in s]
        preds = [f.pred_share for f in s]
        acts = [f.actual_share for f in s]
        acc = float(np.mean([(p > 0.5) == bool(w) for p, w in zip(probs, wins)]))
        return {
            "n": len(s),
            "brier": brier_score(probs, wins),
            "log_loss": log_loss_binary(probs, wins),
            "share_mae": mae(preds, acts),
            "hit_rate": acc,
        }


def run_oos(
    make_source: SourceFactory,
    examples: Sequence[TrainingExample],
    min_train: int = 4,
    source_name: str | None = None,
) -> BacktestReport:
    """Backtest expansif : entraine sur le passe strict, predit, score.

    `make_source` doit renvoyer une instance neuve de `Source` a chaque appel.
    Les elections sont supposees triees par annee (cf. load_registry).
    """
    ex = list(examples)
    folds: list[FoldRecord] = []
    resolved_name = source_name

    for i in range(min_train, len(ex)):
        train = ex[:i]                 # STRICTEMENT anterieures
        test = ex[i]
        ctx: ElectionContext = test.context
        res = test.result

        src = make_source().fit(train)
        if resolved_name is None:
            resolved_name = getattr(src, "name", "source")
        sig: SourceSignal = src.predict(ctx)

        actual_share = res.r2_reference_share(ctx.reference_id)
        actual_win = int(res.winner_id == ctx.reference_id)
        win_p = win_prob_from_normal(sig.r2_share_mean, sig.r2_share_sd)

        folds.append(
            FoldRecord(
                election_id=ctx.election_id,
                year=ctx.year,
                reference_id=ctx.reference_id,
                pred_share=float(sig.r2_share_mean),
                pred_win_prob=win_p,
                actual_share=float(actual_share),
                actual_win=actual_win,
                available=bool(sig.available),
            )
        )

    return BacktestReport(source_name=resolved_name or "source", folds=folds)


def markdown_table(report: BacktestReport) -> str:
    """Rend un tableau markdown des plis OOS + ligne de metriques agregees."""
    lines = ["| Annee | Election | Reference | Part prevue | P(victoire) | Part reelle | Issue |",
             "|---|---|---|---|---|---|---|"]
    for f in report.folds:
        if not f.available:
            lines.append(f"| {f.year} | {f.election_id} | {f.reference_id} | — | — | "
                         f"{f.actual_share:.3f} | (source indispo.) |")
            continue
        issue = "✓ gagne" if f.actual_win else "✗ perd"
        lines.append(f"| {f.year} | {f.election_id} | {f.reference_id} | {f.pred_share:.3f} "
                     f"| {f.pred_win_prob:.2f} | {f.actual_share:.3f} | {issue} |")
    m = report.metrics()
    if m.get("n"):
        lines.append("")
        lines.append(f"**OOS (n={m['n']})** — Brier {m['brier']:.3f} | log-loss "
                     f"{m['log_loss']:.3f} | MAE part {m['share_mae']:.3f} | "
                     f"taux de bonne issue {m['hit_rate']:.0%}")
    return "\n".join(lines)
