from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


class DashboardModuleTests(unittest.TestCase):
    def test_dashboard_modules_import_without_streamlit_runtime(self) -> None:
        from financial_analysis_tool import dashboard, esg_dashboard, financial_dashboard

        self.assertTrue(callable(dashboard.run_dashboard))
        self.assertTrue(callable(esg_dashboard.render_esg_dashboard))
        self.assertTrue(callable(financial_dashboard.render_financial_dashboard))


if __name__ == "__main__":
    unittest.main()
