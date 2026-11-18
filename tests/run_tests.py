"""Minimal pytest-compatible runner (pytest is not in the locked environment).

    python tests/run_tests.py [pattern]

Discovers tests/test_*.py, runs every `test_*` function, supports the `tmp_path` fixture.
With pytest installed, `pytest tests/` runs the same files.
"""

from __future__ import annotations

import importlib.util
import inspect
import sys
import tempfile
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))


def main() -> int:
    pattern = sys.argv[1] if len(sys.argv) > 1 else ""
    failed = passed = 0
    for f in sorted(HERE.glob("test_*.py")):
        spec = importlib.util.spec_from_file_location(f.stem, f)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for name, fn in inspect.getmembers(mod, inspect.isfunction):
            if not name.startswith("test_") or pattern not in f"{f.stem}::{name}":
                continue
            t0 = time.time()
            try:
                kwargs = {}
                if "tmp_path" in inspect.signature(fn).parameters:
                    kwargs["tmp_path"] = Path(tempfile.mkdtemp(prefix="sc_test_"))
                fn(**kwargs)
                passed += 1
                print(f"PASS {f.stem}::{name} ({time.time() - t0:.1f}s)")
            except Exception as exc:  # noqa: BLE001
                if type(exc).__name__ in ("_Skip", "Skipped"):
                    print(f"SKIP {f.stem}::{name}: {exc}")
                    continue
                failed += 1
                print(f"FAIL {f.stem}::{name}")
                traceback.print_exc()
    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


class _Skip(Exception):
    pass


def skip(reason: str):
    """Use in tests: `from tests.run_tests import skip`; maps to pytest.skip when available."""
    try:
        import pytest

        pytest.skip(reason)
    except ImportError:
        raise _Skip(reason) from None


if __name__ == "__main__":
    sys.exit(main())
