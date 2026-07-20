import runpy
from pathlib import Path


def test_basic_usage_example_runs() -> None:
    runpy.run_path(Path("examples/basic_usage.py"))
