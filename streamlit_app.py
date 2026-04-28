"""Repository-root Streamlit entrypoint.

This file lets users launch the dashboard with ``python -m streamlit run
streamlit_app.py`` from a source checkout. It prepares the local import path and
delegates all UI behavior to the packaged dashboard module.
"""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from financial_analysis_tool.dashboard import run_dashboard


if __name__ == "__main__":
    run_dashboard()
