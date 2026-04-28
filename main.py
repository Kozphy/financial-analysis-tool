"""Repository-root CLI entrypoint.

This wrapper makes the package runnable from a raw checkout with
``python main.py``. It adds ``src`` to ``sys.path`` before delegating to the
packaged command-line interface, preserving the same behavior as the installed
``financial-analysis-tool`` console script.
"""

from __future__ import annotations
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


from financial_analysis_tool.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
