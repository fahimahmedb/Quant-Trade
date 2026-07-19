"""Chargement des donnees du module « prediction politique ».

Contient le loader du REGISTRE (verite terrain + contexte, coeur du backtest)
et le loader des variables FONDAMENTALES. Les briques marches/NLP fournissent
leurs propres loaders hybrides (live -> fallback snapshot) dans pp_markets.py
et pp_nlp.py, en s'appuyant sur les election_id / reference_id exposes ici.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

import pandas as pd

from pp_types import Candidate, ElectionContext, ElectionResult, TrainingExample

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REGISTRY_PATH = DATA / "fr_presidentielles.json"
FUNDAMENTALS_PATH = DATA / "fr_fundamentals.csv"


def load_fundamentals(path: str | Path = FUNDAMENTALS_PATH) -> dict[str, dict[str, float]]:
    """election_id -> {gdp_growth, unemployment, approval, tenure_years}."""
    df = pd.read_csv(path, comment="#")
    df = df.set_index("election_id")
    return {eid: {k: float(v) for k, v in row.items()} for eid, row in df.to_dict("index").items()}


def load_registry(
    path: str | Path = REGISTRY_PATH,
    fundamentals_path: str | Path = FUNDAMENTALS_PATH,
) -> list[TrainingExample]:
    """Charge les elections en (ElectionContext, ElectionResult), triees par annee.

    Les variables fondamentales (CSV) sont fusionnees dans `context.features`,
    aux cotes de `incumbent_running` (0/1). Le contexte ne contient JAMAIS le
    resultat : la separation contexte/resultat garantit qu'une source ne peut
    pas tricher.
    """
    raw = json.loads(Path(path).read_text())
    fundamentals = load_fundamentals(fundamentals_path)

    examples: list[TrainingExample] = []
    for e in raw["elections"]:
        eid = e["election_id"]
        feats: dict[str, float] = dict(fundamentals.get(eid, {}))
        feats["incumbent_running"] = 1.0 if e["incumbent_running"] else 0.0

        candidates = tuple(
            Candidate(id=c["id"], name=c["name"], camp=c["camp"], incumbent=bool(c["incumbent"]))
            for c in e["candidates"]
        )
        ctx = ElectionContext(
            election_id=eid,
            year=int(e["year"]),
            reference_id=e["reference_id"],
            candidates=candidates,
            incumbent_running=bool(e["incumbent_running"]),
            features=feats,
        )
        res = ElectionResult(
            election_id=eid,
            r1_shares={k: float(v) for k, v in e["r1_shares"].items()},
            r2_finalists=tuple(e["r2_finalists"]),
            r2_shares={k: float(v) for k, v in e["r2_shares"].items()},
            winner_id=e["winner_id"],
        )
        examples.append(TrainingExample(context=ctx, result=res))

    examples.sort(key=lambda ex: ex.context.year)
    return examples


def registry_quality_report(examples: list[TrainingExample]) -> Mapping[str, object]:
    """Controles de coherence sur le registre (leve si incoherence fatale)."""
    rep: dict[str, object] = {"n_elections": len(examples)}
    problems: list[str] = []
    for ex in examples:
        ctx, res = ex.context, ex.result
        ids = {c.id for c in ctx.candidates}
        if ctx.reference_id not in ids:
            problems.append(f"{ctx.election_id}: reference absente des candidats")
        if res.winner_id not in res.r2_finalists:
            problems.append(f"{ctx.election_id}: vainqueur hors finalistes")
        s = sum(res.r2_shares.values())
        if not (0.98 <= s <= 1.02):
            problems.append(f"{ctx.election_id}: parts 2nd tour = {s:.3f} (attendu ~1)")
        for cid in res.r2_finalists:
            if cid not in ids:
                problems.append(f"{ctx.election_id}: finaliste {cid} hors candidats")
    rep["problems"] = problems
    if problems:
        raise ValueError("Registre incoherent: " + " | ".join(problems))
    rep["years"] = [ex.context.year for ex in examples]
    return rep
