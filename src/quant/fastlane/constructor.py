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
    return [a.entry for a in admit_detailed(entries, slots=slots, horizon=horizon,
                                            seed=seed)[0]]


REJECT_ISSUER_ACTIVE = "issuer_active_slot"
REJECT_BOOK_FULL = "book_full"


@dataclass(frozen=True)
class Admission:
    entry: Entry
    slot: int                    # lowest free slot number (0-based) at admission


def admit_detailed(entries: Sequence[Entry], *, slots: int, horizon: int,
                   seed: int) -> tuple[list[Admission], list[tuple[Entry, str]]]:
    """:func:`admit` plus slot numbers and the logged reason for every a_j = 0.

    Entries are processed by (entry_session, tie_break); the lowest free slot is
    taken; an issuer with an active slot (including a second issuer-day of the
    same issuer in the same session) or a full book is rejected with its reason.
    """
    if slots < 1 or horizon < 1:
        raise ValueError("slots and horizon must be >= 1")
    by_session: dict[int, list[Entry]] = {}
    for entry in entries:
        by_session.setdefault(entry.entry_index, []).append(entry)
    active: dict[str, tuple[int, int]] = {}      # issuer -> (last busy session, slot)
    admitted: list[Admission] = []
    rejected: list[tuple[Entry, str]] = []
    for session in sorted(by_session):
        for issuer in [i for i, (last, _) in active.items() if last < session]:
            del active[issuer]
        ordered = sorted(by_session[session],
                         key=lambda e: (tie_break_key(seed, e.accessions), e.issuer))
        for entry in ordered:
            if entry.issuer in active:
                rejected.append((entry, REJECT_ISSUER_ACTIVE))
                continue
            if len(active) >= slots:
                rejected.append((entry, REJECT_BOOK_FULL))
                continue
            used = {slot for _, slot in active.values()}
            slot = next(i for i in range(slots) if i not in used)
            active[entry.issuer] = (session + horizon - 1, slot)
            admitted.append(Admission(entry, slot))
    return admitted, rejected
