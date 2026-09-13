"""One-shot final repair patch for the independent V1 red-team review."""
from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected exactly one patch target, found {count}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


# A same-session restatement replaces the authoritative mark. The peak used for
# future drawdown/risk must therefore be recomputed from authoritative history,
# not retain a superseded high mark.
replace_once(
    "src/quant/book/ledger.py",
    '''        self.state.last_session_date = date
        self.state.peak_nav = max(self.state.peak_nav, nav)
        point = {"date": date, "nav": nav, "cash": self.state.cash,
''',
    '''        self.state.last_session_date = date
        point = {"date": date, "nav": nav, "cash": self.state.cash,
''')
replace_once(
    "src/quant/book/ledger.py",
    '''        else:
            self.state.sessions += 1
            self.state.nav_history.append(point)
        self.save()
        return point
''',
    '''        else:
            self.state.sessions += 1
            self.state.nav_history.append(point)
        self.state.peak_nav = max(
            [self.state.initial_capital]
            + [float(item["nav"]) for item in self.state.nav_history])
        self.save()
        return point
''')

# The causal test compares semantics, not wall-clock timestamps generated while
# the two equivalent scenarios run a few milliseconds apart.
replace_once(
    "tests/test_v1_red_team.py",
    '''                ticket = summary["tickets"][0]
                tickets.append((ticket["status"], ticket["stage"], ticket["stage_trace"]))
                size = next((entry for entry in ticket["stage_trace"]
''',
    '''                ticket = summary["tickets"][0]
                semantic_trace = [
                    {key: value for key, value in entry.items() if key != "at"}
                    for entry in ticket["stage_trace"]]
                tickets.append((ticket["status"], ticket["stage"], semantic_trace))
                size = next((entry for entry in ticket["stage_trace"]
''')

print("final red-team repairs applied")
