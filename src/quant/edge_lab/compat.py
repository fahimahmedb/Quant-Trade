"""Reuse ResearchTask without importing the legacy package's eager pipeline."""
import importlib.util
import sys
from pathlib import Path

_name = "quant.edge_lab._existing_runtime"
if _name not in sys.modules:
    _path = Path(__file__).resolve().parents[2] / "autonomous_research/runtime.py"
    _spec = importlib.util.spec_from_file_location(_name, _path)
    _module = importlib.util.module_from_spec(_spec)
    sys.modules[_name] = _module
    _spec.loader.exec_module(_module)

ResearchTask = sys.modules[_name].ResearchTask
