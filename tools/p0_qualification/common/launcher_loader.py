"""Load ``deploy/quant_sec_supervisor.py`` as an isolated module instance.

Mirrors the pattern already used in ``tests/test_astra_pre_t0.py``
(``importlib.util.spec_from_file_location``): the deploy launcher has no
``__init__.py`` and is not meant to be a package, so a fresh module object is
loaded per isolated root instead of mutating ``sys.modules`` globally, and
instead of adding an ``__init__.py`` the mission's immutability boundary
forbids touching.
"""

from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path
from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parents[3]
LAUNCHER_SOURCE = REPO_ROOT / "deploy" / "quant_sec_supervisor.py"
UNIT_SOURCE = REPO_ROOT / "deploy" / "quant-sec-capture.service"


def load_launcher(module_name: str = "p0_qualification_launcher") -> ModuleType:
    """Load the frozen launcher by file path, read-only, no root isolation."""
    spec = importlib.util.spec_from_file_location(module_name, LAUNCHER_SOURCE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def stage_isolated_root(root: Path) -> ModuleType:
    """Symlink ``src``/``scripts``/``deploy`` into ``root`` and load the launcher.

    Several launcher code paths resolve sibling files relative to the module's
    own directory (the unit file, the fingerprint's module closure). Symlinking
    the real trees in, exactly as the existing Astra fixtures do, lets the
    harness exercise the real launcher against a disposable state root without
    ever writing into the checked-out repository tree.
    """
    for name in ("src", "scripts", "deploy"):
        (root / name).symlink_to(REPO_ROOT / name, target_is_directory=True)
    return load_launcher(f"p0_qualification_launcher_{id(root)}")
