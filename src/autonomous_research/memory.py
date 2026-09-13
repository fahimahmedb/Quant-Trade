"""Append-only JSONL research memory."""

from __future__ import annotations

import json
from pathlib import Path

from .ticket import ResearchTicket


def append_ticket(path: Path, ticket: ResearchTicket) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(ticket.to_dict(), sort_keys=True) + "\n")
