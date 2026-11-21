"""`evaluation` reads results and never imports an arm.

Results are scored into the shapes in `evaluation.scoring`; the report, figure
and breakdowns read those. An import from `arms` here would make evaluation
depend on the thing it measures, and reintroduce the cycle this replaced.
"""

import ast
from pathlib import Path

import pytest

EVALUATION = Path(__file__).parents[2] / "src" / "arbiter" / "evaluation"


def _imported_modules(source: str) -> list[str]:
    found: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            found += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            found.append(node.module or "")
    return found


@pytest.mark.parametrize("module", sorted(EVALUATION.glob("*.py")), ids=lambda path: path.name)
def test_no_evaluation_module_imports_an_arm(module: Path):
    imported = _imported_modules(module.read_text(encoding="utf-8"))

    assert not [name for name in imported if name.startswith("arbiter.arms")]


def test_the_check_reads_imports_inside_functions_too():
    """Several modules import lazily; the walk must not stop at module level."""
    source = "def f():\n    from arbiter.arms.evaluate import Evaluation\n"

    assert "arbiter.arms.evaluate" in _imported_modules(source)
