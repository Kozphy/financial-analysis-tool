from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.financial_analysis_tool.cli import main  # type: ignore[import-not-found]


if __name__ == "__main__":
    raise SystemExit(main())
