"""Status surface: an observer of persistent state, never a source of it."""

from .brief import write_chief_brief
from .render import render_status

__all__ = ["render_status", "write_chief_brief"]
