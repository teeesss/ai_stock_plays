import py_compile
from pathlib import Path

import pytest


def test_syntax_engine_files():
    """Verify that all Python files in the engine directory are syntactically correct."""
    engine_path = Path(__file__).parent.parent / "engine"

    python_files = list(engine_path.glob("*.py"))

    errors = []
    for py_file in python_files:
        try:
            py_compile.compile(str(py_file), doraise=True)
        except py_compile.PyCompileError as e:
            errors.append(f"Syntax error in {py_file.name}: {e}")

    if errors:
        pytest.fail("\n".join(errors))
