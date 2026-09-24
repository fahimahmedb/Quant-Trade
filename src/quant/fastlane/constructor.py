"""Slot constructor ordering for ``QUANT_FASTLANE_HPIT_V1`` (outcome-blind).

When more entry events share an entry session than there are free slots, the
admission order must not correlate with anything economic. Issuer CIK order
does (older registrants have smaller CIKs), so the tie-break is a keyed hash:

    key = sha256(utf8(str(seed) + "|" + ",".join(sorted(accessions_of_issuer_day))))

ascending hex, with the sealed ``bootstrap_seed`` as the seed.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable, Sequence


def tie_break_key(seed: int, accessions: Iterable[str]) -> str:
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise TypeError("seed must be an integer")
    joined = ",".join(sorted(accessions))
    if not joined:
        raise ValueError("an issuer-day needs at least one accession")
    return hashlib.sha256(f"{seed}|{joined}".encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Entry:
    entry_index: int              # vendor session index of the entry
    issuer: str
    accessions: tuple[str, ...]


def admit(entries: Sequence[Entry], *, slots: int, horizon: int, seed: int) -> list[Entry]:
    """Deterministic slot admission: one active slot per issuer, time-based release.

    A slot taken at entry session e is busy through e + horizon - 1 and is
    released at the start of session e + horizon. Weights/outcomes play no role.
    """
    by_session: dict[int, list[Entry]] = {}
    for entry in entries:
        by_session.setdefault(entry.entry_index, []).append(entry)
    active: dict[str, int] = {}          # issuer -> last busy session
    admitted: list[Entry] = []
    for session in sorted(by_session):
        for issuer in [i for i, last in active.items() if last < session]:
            del active[issuer]
        candidates = sorted((e for e in by_session[session] if e.issuer not in active),
                            key=lambda e: tie_break_key(seed, e.accessions))
        seen: set[str] = set()
        for entry in candidates:
            if len(active) >= slots:
                break
            if entry.issuer in seen:
                continue
            seen.add(entry.issuer)
            active[entry.issuer] = session + horizon - 1
            admitted.append(entry)
    return admitted
