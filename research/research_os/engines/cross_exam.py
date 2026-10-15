from __future__ import annotations

from itertools import combinations
from typing import Any, Dict, List


def cross_examine(outputs: List[Dict[str, Any]]) -> Dict[str, Any]:
    questions = []
    for left, right in combinations(outputs, 2):
        lc, rc = left["candidate"], right["candidate"]
        shared = sorted(set(lc["economic_tags"]) & set(rc["economic_tags"]))
        if shared:
            questions.append({
                "left": lc["hypothesis_id"],
                "right": rc["hypothesis_id"],
                "shared_tags": shared,
                "question": "Do the candidates remain distinct after controlling for shared economic exposure?",
                "authority": "CHALLENGE_ONLY",
            })
    return {
        "cross_examiner": "cross-exam.v0",
        "status": "COMPLETE",
        "questions": questions,
        "mutated_hypotheses": False,
        "new_hypotheses_created": False,
    }
